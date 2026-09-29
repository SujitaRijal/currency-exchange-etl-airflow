#"What happened during each pipeline execution?"

from include.load.database import get_connection
import logging

logger=logging.getLogger(__name__)

def create_audit_table():
    conn=get_connection()
    cursor=conn.cursor()

    try:
        cursor.execute (
            """
            CREATE TABLE IF NOT EXISTS etl_audit_log (
            id SERIAL PRIMARY KEY,
            pipeline_name VARCHAR(100) NOT NULL,
            run_id TEXT NOT NULL,
            execution_date DATE NOT NULL,
            start_time TIMESTAMPTZ NOT NULL,
            end_time TIMESTAMPTZ,
            duration_seconds Numeric(10,2),
            status VARCHAR(20) NOT NULL,
            records_received INTEGER DEFAULT 0,
            records_loaded INTEGER DEFAULT 0,
            duplicates_skipped INTEGER DEFAULT 0,
            failed_task TEXT,
            error_message TEXT
            )
            """
        )
        conn.commit()
        logger.info("Audit table is ready.")

    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to create audit table :{e}")
        raise

    finally:
        cursor.close()
        conn.close()


#Notice that I'm not including end_time, records_loaded, or error_message yet,because when the pipeline starts, we don't know them yet.
def insert_audit_log(
    pipeline_name,
    run_id,
    execution_date,
    start_time,
    status
):
    conn=get_connection()
    cursor=conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO etl_audit_log
            (
                pipeline_name,
                run_id,
                execution_date,
                start_time,
                status
            )
            VALUES(%s, %s, %s, %s, %s)
            """,
            (
                pipeline_name,
                run_id,
                execution_date,
                start_time,
                status
            ),
        )

        conn.commit()
        logger.info(
            f"Audit log created for pipeline '{pipeline_name}' " f"with run_id '{run_id}'"
        )

    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to insert audit log: {e}")
        raise

    finally:
        cursor.close()
        conn.close()

def get_start_time(run_id):
    conn=get_connection()
    cursor=conn.cursor()

    try:
        cursor.execute(
            """
            SELECT start_time 
            FROM etl_audit_log
            WHERE run_id = %s
            """,
            (run_id,)
        )
        result = cursor.fetchone()
        if result :
            return result[0]
        raise ValueError(f"No audit record found for run_id: {run_id}")
    except Exception as e:
        logger.exception("Failed to fetch start time")
        raise
    finally:
        cursor.close()
        conn.close()


def update_audit_success(run_id, end_time, load_metrics):
    conn=get_connection()
    cursor=conn.cursor()

    try:
        start_time =get_start_time(run_id)
        duration_seconds = round((end_time - start_time).total_seconds(),2)
        cursor.execute(
            """ 
            UPDATE  etl_audit_log
            SET 
                end_time = %s,
                duration_seconds = %s,
                status = %s,
                records_received = %s,
                records_loaded = %s,
                duplicates_skipped = %s
                WHERE run_id = %s;
            """,
            (
                end_time,
                duration_seconds,
                "SUCCESS",
                load_metrics["records_received"],
                load_metrics["records_loaded"],
                load_metrics["duplicates_skipped"], 
                run_id
            )
        )
        conn.commit()
        logger.info(f"Audit log marked SUCCESS for run_id : {run_id}")
    except Exception as e:
        conn.rollback()
        logger.exception("Failed to update audit log")
        raise
    finally:
        cursor.close()
        conn.close()

def update_audit_failure(run_id, end_time,failed_task, error_message):
    conn=get_connection()
    cursor=conn.cursor()

    try:
        start_time=get_start_time(run_id)
        duration_seconds = round((end_time - start_time).total_seconds(),2)
        cursor.execute(
            """ 
            UPDATE etl_audit_log
            SET
                end_time = %s,
                duration_seconds = %s,
                status = %s,
                failed_task = %s,
                error_message = %s
                WHERE run_id = %s; 
            """,
            (
                end_time,
                duration_seconds,
                "FAILED",
                failed_task,
                error_message,
                run_id
            )
        )
        conn.commit()
        logger.info(f"Audit log marked FAILED for run_id : {run_id}")

    except Exception as e:
        conn.rollback()
        logger.exception("Failed to update audit log")
        raise

    finally:
        cursor.close()
        conn.close()

def update_audit_skipped(run_id, end_time):
    conn=get_connection()
    cursor=conn.cursor()

    try:
        start_time = get_start_time(run_id)
        duration_seconds= round((end_time - start_time).total_seconds(),2)
        cursor.execute(
            """ 
            UPDATE etl_audit_log
            SET
                end_time = %s,
                duration_seconds = %s,
                status = %s
                WHERE run_id = %s; 
            """,
            (
                end_time,
                duration_seconds,
                "SKIPPED",
                run_id
            )
        )
        conn.commit()
        logger.info(f"Audit log marked SKIPPED for run_id : {run_id}")

    except Exception as e:
        conn.rollback()
        logger.exception("Failed to update audit log")
        raise

    finally:
        cursor.close()
        conn.close()
