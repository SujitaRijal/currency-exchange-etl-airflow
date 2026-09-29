from airflow.providers.smtp.notifications.smtp import send_smtp_notification

from airflow.models import Variable
ALERT_EMAIL= Variable.get("ALERT_EMAIL")

smtp_callback = send_smtp_notification(
        to = ALERT_EMAIL,
        subject="Airflow Task Failed: {{ti.task_id}}",
        html_content="""
        <h2> Currency ETL Pipeline Failed </h2>

        <p><b>DAG:</b> {{ dag.dag_id }}</p>
        <p><b>Task:</b> {{ ti.task_id }}</p>
        <p><b>Execution Date:</b> {{ ds }}</p>
        <p><b>Exception:</b> {{ exception }}</p>

        <p>Please check the Airflow logs for more details.</p>
        """,
    )

def email_failure_callback(context):
    """
    Sends an email notification when a task fails.
    """
    smtp_callback(context)