import json
import logging
from datetime import datetime, timedelta

from airflow.models import Variable
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.sdk import dag, get_current_context, task
from airflow.timetables.interval import CronDataIntervalTimetable
from airflow.utils.timezone import utc
from include.callbacks.pipeline_callback import pipeline_failure_callback
from include.extract.api_client import fetch_exchange_rate
from include.load.audit import (
    create_audit_table,
    insert_audit_log,
    update_audit_skipped,
    update_audit_success,
)
from include.load.loader import load_exchange_rates
from include.load.metadata import (
    create_metadata_table,
    get_last_processed_timestamp,
    update_last_processed_timestamp,
)
from include.quality.quality_check import check_data_quality
from include.reports.audit_export import export_audit_csv
from include.reports.report_generator import print_pipeline_report
from include.transform.transform_rates import transform_exchange_rates
from include.utils.file_utils import write_json
from include.utils.purge_utils import purge_old_files
from include.validate.validator import validate_exchange_rates

logger = logging.getLogger(__name__)
PIPELINE_NAME = Variable.get("PIPELINE_NAME")
RETENTION_DAYS = int(Variable.get("FILE_RETENTION_DAYS"))

default_args = {
    "owner": "Sujita Rijal",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "on_failure_callback": pipeline_failure_callback,
}


@dag(
    dag_id="CurrencyETLPipeline",
    description="Daily ETL pipeline for currency exchange rates.",
    default_args=default_args,
    start_date=datetime(2026, 9, 20, tzinfo=utc),
    schedule=CronDataIntervalTimetable("0 6 * * *", timezone=utc),
    catchup=False,
    tags=["ETL", "Currency", "PostgreSQL"],
)
def currency_pipeline():
    start = EmptyOperator(task_id="start")
    end = EmptyOperator(task_id="end")

    @task
    def initialize_database():
        create_metadata_table()
        create_audit_table()

        logger.info("Database initialization completed")

    @task
    # Create one audit record with status = RUNNING.
    def start_audit(ds):
        context = get_current_context()
        run_id = context["dag_run"].run_id
        start_time = datetime.now(utc)
        insert_audit_log(
            pipeline_name=PIPELINE_NAME,
            run_id=run_id,
            execution_date=ds,
            start_time=start_time,
            status="RUNNING",
        )
        return run_id

    @task  # taskflow api
    def extract_exchange_rate(ds):  # ds-date string
        data = (
            fetch_exchange_rate()
        )  # dag doesn't know how api works,simply calls the helper function
        file_path = f"/opt/airflow/output/raw/{ds}.json"
        write_json(
            data, file_path
        )  # dag doesnt know how files are written ,it delegates the responsibility
        # We return the file path instead of the complete data object.
        # Passing large objects through XCom is inefficient.
        # Downstream tasks can read the file when required.
        return file_path

    @task.short_circuit
    def check_metadata(raw_file):
        logger.info("Checking metadata for incremental loading.")

        with open(raw_file, "r") as f:
            data = json.load(f)

        api_timestamp = data["time_last_update_utc"]

        last_processed_timestamp = get_last_processed_timestamp(PIPELINE_NAME)

        logger.info(f"API timestamp: {api_timestamp}")
        logger.info(f"Last processed timestamp: {last_processed_timestamp}")

        if api_timestamp == last_processed_timestamp:
            logger.info("No new data found, skipping downstream tasks")
            context = get_current_context()
            run_id = context["dag_run"].run_id
            end_time = datetime.now(utc)

            update_audit_skipped(run_id=run_id, end_time=end_time)
            return False

        logger.info("New data found. Continuing pipeline")
        return True

    @task
    def validate(raw_file):
        validate_exchange_rates(raw_file)
        logger.info("Validation successful")

    @task
    def transform_data(raw_file, ds):
        output_file = f"/opt/airflow/output/processed/{ds}.json"
        return transform_exchange_rates(raw_file, output_file, ds)

    @task
    def quality(processed_file):
        check_data_quality(processed_file)
        logger.info("Data quality check passed.")

    @task
    def load_data(processed_file):
        load_metrics = load_exchange_rates(processed_file)
        return load_metrics

    @task
    def update_metadata(raw_file):
        logger.info("Updating ETL metadata.")

        with open(raw_file, "r") as f:
            data = json.load(f)

        api_timestamp = data["time_last_update_utc"]

        update_last_processed_timestamp(PIPELINE_NAME, api_timestamp)
        logger.info(
            f"Updated metadata for '{PIPELINE_NAME}' with timestamp '{api_timestamp}'."
        )

    @task
    def purge_old_output_files(ds):

        purge_old_files(
            directory="/opt/airflow/output/raw", retention_days=RETENTION_DAYS, ds=ds
        )

        purge_old_files(
            directory="/opt/airflow/output/processed",
            retention_days=RETENTION_DAYS,
            ds=ds,
        )

    @task
    def finish_audit_success(audit_run_id, load_metrics):
        end_time = datetime.now(utc)
        update_audit_success(
            run_id=audit_run_id, end_time=end_time, load_metrics=load_metrics
        )

    @task
    def pipeline_report(ds):
        context = get_current_context()
        run_id = context["dag_run"].run_id
        print_pipeline_report(run_id, ds)

    @task
    def export_daily_audit(ds):
        export_audit_csv(ds)

    # task obj
    initialize = initialize_database()
    audit_run = start_audit()
    extract = extract_exchange_rate()  # add this tag to dag
    metadata = check_metadata(extract)
    validation = validate(extract)
    transform = transform_data(extract)
    quality_check = quality(transform)
    load = load_data(transform)
    update = update_metadata(extract)
    purge_files = purge_old_output_files()
    finish = finish_audit_success(audit_run, load)
    report = pipeline_report()
    audit_csv = export_daily_audit()

    # set dependencies
    (
        start
        >> initialize
        >> audit_run
        >> extract
        >> metadata
        >> validation
        >> transform
        >> quality_check
        >> load
        >> update
        >> purge_files
        >> finish
        >> report
        >> audit_csv
        >> end
    )


# build dag
dag = currency_pipeline()

# Idempotent means the pipeline can run multiple times
# with the same input without changing the final database state.

# An idempotent ETL pipeline can execute repeatedly
# without changing the final state of the target database.

# This is achieved using unique constraints,
# UPSERT operations, or ON CONFLICT logic.

# primary key->one for entire table,cannot be null,uniquely identify record
# unique- there can be many for a table,prevent duplicates,,
# used to enforce business rules

# The DAG uses Airflow's @task.short_circuit.
# When no new data is detected, downstream tasks are skipped.

# This avoids unnecessary processing.
# Downstream tasks including end are marked skipped.
