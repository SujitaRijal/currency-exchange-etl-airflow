from airflow.sdk import dag
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.smtp.operators.smtp import EmailOperator

from pendulum import datetime

@dag(
    dag_id="email_test",
    start_date= datetime(2026,9,27),
    schedule=None,
    catchup=False,
)

def email_test():
    start=EmptyOperator(task_id="start")

    send_email=EmailOperator(
        task_id="send_email",
        to="rijalsujeeta@gmail.com",
        subject="Airflow Email Test",
        html_content=""" 
        <h2> Email Test successful </h2>
        <p> This email was sent from your apache airflow pipeline </p>
        """,
    )

    end=EmptyOperator(task_id="end")

    start >> send_email >> end

email_test()