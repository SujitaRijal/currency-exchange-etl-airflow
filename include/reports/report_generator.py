#format and present
import logging
from pathlib import Path
from airflow.models import Variable
from datetime import datetime
from airflow.utils.timezone import utc



from include.reports.metrics import (
    get_total_runs,
    get_successful_runs,
    get_failed_runs,
    get_skipped_runs,
    get_average_duration,
    get_total_records_received,
    get_total_records_loaded,
    get_total_duplicates_skipped,
    get_success_rate,
    get_failure_rate
)

logger=logging.getLogger(__name__)
PIPELINE_NAME = Variable .get("PIPELINE_NAME")

def generate_pipeline_report():
    #gathers data
    total_runs=get_total_runs()
    successful_runs=get_successful_runs()
    failed_runs=get_failed_runs()
    skipped_runs=get_skipped_runs()
    average_duration=get_average_duration()
    total_received=get_total_records_received()
    total_loaded=get_total_records_loaded()
    duplicates_skipped=get_total_duplicates_skipped()
    success_rate=get_success_rate()
    failure_rate=get_failure_rate()

    return {
        "pipeline_name": PIPELINE_NAME,
        "generated_on":datetime.now(utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "total_runs":total_runs,
        "successful_runs":successful_runs,
        "failed_runs":failed_runs,
        "skipped_runs":skipped_runs,
        "average_duration":average_duration,
        "total_records_received":total_received,
        "total_records_loaded":total_loaded,
        "duplicates_skipped":duplicates_skipped,
        "success_rate":success_rate,
        "failure_rate":failure_rate
    }

def print_pipeline_report(run_id, ds):
    #presents the data
    #call generate piepliene report and store the returned dict in a variable
    report = generate_pipeline_report()

    logger.info("================Currency ETL Pipeline Summary=====================")
    logger.info(f"Pipeline Name              : {report['pipeline_name']}")
    logger.info(f"Generated On               : {report['generated_on']}")
    logger.info("")
    logger.info(f"Total Runs                 : {report['total_runs']}")
    logger.info(f"Successful Runs           : {report['successful_runs']}")
    logger.info(f"Failed Runs                : {report['failed_runs']}")
    logger.info(f"Skipped Runs               : {report['skipped_runs']}")
    logger.info(f"Average Duration           : {report['average_duration']} seconds")
    logger.info(f"Total Records Received     : {report['total_records_received']}")
    logger.info(f"Total Records Loaded       : {report['total_records_loaded']}")
    logger.info(f"Duplicates Skipped         : {report['duplicates_skipped']}")
    logger.info(f"Success Rate               : {report['success_rate']}%")
    logger.info(f"Failure Rate               : {report['failure_rate']}%")

    logger.info("=========================================================")

    is_scheduled_run = run_id.startswith("scheduled__")
    if is_scheduled_run :
        save_pipeline_report(report,ds)

def save_pipeline_report(report,ds):
    report_file= Path(f"/opt/airflow/output/reports/{ds}.txt")
    report_file.parent.mkdir(parents=True,exist_ok=True)
    with open(report_file, "w") as f:
        f.write("================ Currency ETL Pipeline Summary =====================\n")
        f.write(f"Pipeline Name              : {report['pipeline_name']}\n")
        f.write(f"Generated On               : {report['generated_on']}\n")
        f.write("\n")
        f.write(f"Total Runs                 : {report['total_runs']}\n")
        f.write(f"Successful Runs            : {report['successful_runs']}\n")
        f.write(f"Failed Runs                : {report['failed_runs']}\n")
        f.write(f"Skipped Runs               : {report['skipped_runs']}\n")
        f.write(f"Average Duration           : {report['average_duration']} seconds\n")
        f.write(f"Total Records Received     : {report['total_records_received']}\n")
        f.write(f"Total Records Loaded       : {report['total_records_loaded']}\n")
        f.write(f"Duplicates Skipped         : {report['duplicates_skipped']}\n")
        f.write(f"Success Rate               : {report['success_rate']}%\n")
        f.write(f"Failure Rate               : {report['failure_rate']}%\n")
        f.write("=========================================================\n")

        logger.info(f"Pipeline report saved to {report_file}")







    



