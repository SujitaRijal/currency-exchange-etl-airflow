from airflow.sdk import dag,task
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.utils.timezone import utc
from airflow.timetables.interval import CronDataIntervalTimetable
from datetime import datetime, timedelta
from include.extract.api_client import fetch_exchange_rate
from include.utils.file_utils import write_json
from include.transform.transform_rates import transform_exchange_rates
from include.load.loader import load_exchange_rates
from include.validate.validator import validate_exchange_rates
from include.load.metadata import get_last_processed_timestamp
from include.load.metadata import update_last_processed_timestamp
from include.load.metadata import create_metadata_table
import json
import logging

logger=logging.getLogger(__name__)
PIPELINE_NAME = "currency_etl"

default_args = {
    "owner": "Sujita Rijal",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),

}


@dag (
    dag_id="CurrencyETLPipeline",
    description="Daily ETL pipeline for currency exchange rates.",
    default_args=default_args,
    start_date=datetime(2026,9,20, tzinfo=utc),
    schedule=CronDataIntervalTimetable("0 6 * * *", timezone=utc),
    catchup=False,
    tags=["ETL", "Currency", "PostgreSQL"]
)

def currency_pipeline():
    start= EmptyOperator(task_id="start")
    end=EmptyOperator(task_id="end")

    @task  #taskflow api
    def extract_exchange_rate(ds):  #ds-date string 
        data=fetch_exchange_rate()  #dag doesn't know how api works,simply calls the helper function
        file_path= f"/opt/airflow/output/raw/{ds}.json"
        write_json(data,file_path) #dag doesnt know how files are written ,it delegates the responsibility
        return file_path  #why returing filepath instead of data,imagine api returns 10 mb of json,passing entire obj through xcom is inefficient,instead we pass the path,and task simply read the file

    
    @task.short_circuit   
    def check_metadata(raw_file):
        create_metadata_table()
        logger.info("Checking metadata for incremental loading.")
        
        with open(raw_file,"r") as f:
            data= json.load(f)

        api_timestamp= data["time_last_update_utc"]

        last_processed_timestamp=get_last_processed_timestamp(PIPELINE_NAME)

        logger.info(f"API timestamp: {api_timestamp}")
        logger.info(f"Last processed timestamp: {last_processed_timestamp}")

        if api_timestamp == last_processed_timestamp:
            logger.info("No new data found, skipping downstream tasks")
            return False
        
        logger.info("New data found. Continuing pipeline")
        return True
       
    @task
    def validate(raw_file):
        validate_exchange_rates(raw_file)
        logger.info("Validation successful")

    
    @task
    def transform_data(raw_file, ds):
        output_file= f"/opt/airflow/output/processed/{ds}.json"
        return transform_exchange_rates(
            raw_file,output_file, ds
        )

    @task
    def load_data(processed_file):
        load_exchange_rates(processed_file)

    @task
    def update_metadata(raw_file):
        logger.info("Updating ETL metadata.")

        with open(raw_file,"r") as f:
            data=json.load(f)

        api_timestamp= data["time_last_update_utc"]

        update_last_processed_timestamp(PIPELINE_NAME,api_timestamp)
        logger.info(f"Updated metadata for '{PIPELINE_NAME}' with timestamp '{api_timestamp}'.")


    #task obj
    extract=extract_exchange_rate() #add this tag to dag
    metadata = check_metadata(extract)
    validation=validate(extract)
    transform=transform_data(extract)
    load=load_data(transform)
    update=update_metadata(extract)

    #set dependencies
    start >> extract >>metadata >>validation >> transform >> load >>update >> end

#build dag
dag=currency_pipeline()



#Idempotent means you can run the pipeline multiple times with the same input, and the final result in the database stays the same.
#"An idempotent ETL pipeline can be executed multiple times with the same input without changing the final state of the target database
# . We usually achieve this by using unique constraints together with UPSERT or ON CONFLICT logic to avoid duplicate records."

#primary key->one for entire table,cannot be null,uniquely identify record
#unique- there can be many for a table,prevent duplicates,,used to enforce business rules

#"The DAG uses Airflow's @task.short_circuit. When no new source data is detected, the operator intentionally skips all downstream 
# tasks to avoid unnecessary processing. Since end is downstream, it is also marked as skipped."