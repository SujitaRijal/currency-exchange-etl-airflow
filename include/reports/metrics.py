from include.load.database import get_connection
import logging

logger= logging.getLogger(__name__)

def get_total_runs():
    conn=get_connection()
    cursor=conn.cursor()
    try:
        cursor.execute(
            """
            SELECT COUNT (*)
            FROM etl_audit_log;
            """
        )
        total_runs=cursor.fetchone()[0]
        logger.info(f"Total Pipelines run :{total_runs}")

        return total_runs
    except Exception:
        logger.exception("Failed to fetch total pipeline runs")
        raise
    finally:
        cursor.close()
        conn.close()

def get_successful_runs():
    conn=get_connection()
    cursor=conn.cursor()

    try:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM etl_audit_log
            WHERE status = 'SUCCESS';
            """
        )
        successful_runs= cursor.fetchone()[0]
        logger.info(f"Successful pipeline runs:{successful_runs}")
        return successful_runs
    except Exception:
        logger.exception("Failed to fetch successful pipeline runs")
        raise
    finally:
        cursor.close()
        conn.close()

def get_failed_runs():
    conn=get_connection()
    cursor=conn.cursor()
    try:
        cursor.execute(
            """
            SELECT COUNT (*)
            FROM etl_audit_log
            WHERE status ='FAILED';
            """
        )
        failed_runs=cursor.fetchone()[0]
        logger.info(f"Failed pipeline runs:{failed_runs}")
        return failed_runs
    except Exception:
        logger.exception("Failed to fetch failed pipeline runs")
        raise
    finally:
        cursor.close()
        conn.close()

def get_skipped_runs():
    conn=get_connection()
    cursor=conn.cursor()
    try:
        cursor.execute(
            """
            SELECT COUNT (*)
            FROM etl_audit_log
            WHERE status = 'SKIPPED';
            """
        )
        skipped_runs=cursor.fetchone()[0]
        logger.info(f"Skipped pipeline runs:{skipped_runs}")
        return skipped_runs
    except Exception:
        logger.exception("Failed to fetch skipped pipeline runs")
        raise
    finally:
        cursor.close()
        conn.close()

def get_average_duration():
    conn=get_connection()
    cursor=conn.cursor()
    try:
        cursor.execute(
            """
            SELECT AVG(duration_seconds)
            FROM etl_audit_log
            WHERE duration_seconds IS NOT NULL;
            """
        )
        average_duration = cursor.fetchone()[0]

        if average_duration is None:
            average_duration = 0
        average_duration = round(float(average_duration),2)
        logger.info(f"Average pipeline duration :{average_duration} seconds")
        return average_duration
    except Exception:
        logger.exception("Failed to fetch average pipeline execution")
        raise
    finally:
        cursor.close()
        conn.close()


def get_total_records_received():
    conn=get_connection()
    cursor=conn.cursor()
    try:
        cursor.execute(
            """
            SELECT SUM(records_received)
            FROM etl_audit_log;
            """
        )
        total_loaded=cursor.fetchone()[0]
        if total_loaded is None:
            total_loaded = 0

        logger.info(f"Total records received : {total_loaded}")
        return total_loaded
    except Exception:
        logger.exception("Failed to fetch total records received")
        raise
    finally:
        cursor.close()
        conn.close()

def get_total_records_loaded():
    conn=get_connection()
    cursor=conn.cursor()
    try:
        cursor.execute(
            """
            SELECT SUM(records_loaded)
            FROM etl_audit_log;
            """
        )
        total_loaded=cursor.fetchone()[0]
        if total_loaded is None:
            total_loaded = 0

        logger.info(f"Total records loaded : {total_loaded}")
        return total_loaded
    except Exception:
        logger.exception("Failed to fetch total records loaded")
        raise
    finally:
        cursor.close()
        conn.close()

def get_total_duplicates_skipped():
    conn=get_connection()
    cursor=conn.cursor()
    try:
        cursor.execute(
            """
            SELECT SUM(duplicates_skipped)
            FROM etl_audit_log;
            """
        )
        duplicates_skipped = cursor.fetchone()[0]
        if duplicates_skipped is None:
            duplicates_skipped = 0

        logger.info(f"Total duplicates skipped : {duplicates_skipped}")
        return duplicates_skipped
    except Exception:
        logger.exception("Failed to fetch total duplicates skipped")
        raise
    finally:
        cursor.close()
        conn.close()

def get_success_rate():
    total_runs=get_total_runs()
    successful_runs=get_successful_runs()

    if total_runs == 0:
        return 0
    success_rate=round((successful_runs/total_runs)*100 , 2)
    logger.info(f"Success rate: {success_rate}")
    return success_rate

def get_failure_rate():
    total_runs=get_total_runs()
    failed_runs=get_failed_runs()

    if total_runs == 0:
        return 0
    failure_rate=round((failed_runs/total_runs)*100 , 2)
    logger.info(f"Failure rate: {failure_rate}")
    return failure_rate






