import csv
import logging
from pathlib import Path
from include.load.database import get_connection

logger=logging.getLogger(__name__)

def export_audit_csv(ds):
    report_file= Path(f"/opt/airflow/output/audit/audit_{ds}.csv")
    report_file.parent.mkdir(parents=True, exist_ok=True)

    conn=get_connection()
    cursor=conn.cursor()
    try:
        cursor.execute(
            """
                SELECT
                pipeline_name,
                run_id,
                execution_date,
                start_time,
                end_time,
                duration_seconds,
                status,
                records_received,
                records_loaded,
                duplicates_skipped,
                failed_task,
                error_message
                FROM etl_audit_log
                WHERE execution_date = %s
                ORDER BY start_time;
            """,
            (ds,)
        )
        rows=cursor.fetchall() #fetchall gives you rows-actual data, no columns name ,only data,column name are stored in cursor.description
        #cursor.description-each tuple represent one column,not row,,it returns metadata about the column where desc[0] returns column name (column_name, data_type, display_size....)
        headers=[desc[0] for desc in cursor.description] #gives info about header-headers-column name

        with open(report_file,"w", newline="") as csv_file: #newline prevents extra blank lines
            writer = csv.writer(csv_file)
            writer.writerow(headers)
            writer.writerows(rows)

        logger.info(f"Audit CSV exported to {report_file}")
        return str(report_file)


    except Exception as e:
        logger.exception("Failed to export audit report")
        raise
    finally:
        cursor.close()
        conn.close()

