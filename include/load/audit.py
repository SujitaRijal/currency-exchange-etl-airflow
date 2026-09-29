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
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP ,
            status VARCHAR(20) NOT NULL,
            records_loaded INTEGER DEFAULT 0,
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
        logger.error("Failed to insert audit log: {e}")
        raise

    finally:
        cursor.close()
        conn.close()

def update_audit_success(run_id, end_time, records_loaded):
    conn=get_connection()
    cursor=conn.cursor()

    try:
        cursor.execute(
            """ 
            UPDATE  etl_audit_log
            SET 
                end_time = %s,
                status = %s,
                records_loaded = %s
                WHERE run_id = %s;
            """,
            (
                end_time,
                "SUCCESS",
                records_loaded,
                run_id
            )
        )
        conn.commit()
        logger.info(f"Audit log marked SUCCESS for run_id : {run_id}")
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to update audit log :{e}")
        raise
    finally:
        cursor.close()
        conn.close()

def update_audit_failure(run_id, end_time, error_message):
    conn=get_connection()
    cursor=conn.cursor()

    try:
        cursor.execute(
            """ 
            UPDATE etl_audit_log
            SET
                end_time = %s,
                status = %s,
                error_message = %s
                WHERE run_id = %s; 
            """,
            (
                end_time,
                "FAILED",
                error_message,
                run_id
            )
        )
        conn.commit()
        logger.info(f"Audit log marked FAILED for run_id : {run_id}")

    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to update audit log : {e}")
        raise

    finally:
        cursor.close()
        conn.close()

def update_audit_skipped(run_id, end_time):
    conn=get_connection()
    cursor=conn.cursor()

    try:
        cursor.execute(
            """ 
            UPDATE etl_audit_log
            SET
                end_time = %s,
                status = %s
                WHERE run_id = %s; 
            """,
            (
                end_time,
                "SKIPPED",
                run_id
            )
        )
        conn.commit()
        logger.info(f"Audit log marked SKIPPED for run_id : {run_id}")

    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to update audit log : {e}")
        raise

    finally:
        cursor.close()
        conn.close()
