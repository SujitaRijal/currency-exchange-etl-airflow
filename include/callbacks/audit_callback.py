from datetime import datetime
from airflow.utils.timezone import utc
from include.load.audit import update_audit_failure

def audit_failure_callback(context):
    """
    Updates the audit log when a task fails.
    """
    run_id = context["dag_run"].run_id
    end_time= datetime.now(utc)
    error_message = str(context["exception"])
    update_audit_failure(
        run_id= run_id,
        end_time= end_time,
        error_message=error_message
    )