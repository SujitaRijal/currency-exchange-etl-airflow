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

    @task
    def validate(raw_file):
        validate_exchange_rates(raw_file)
        print("Validation succesfull")

    
    @task
    def transform_data(raw_file, ds):
        output_file= f"/opt/airflow/output/processed/{ds}.json"
        return transform_exchange_rates(
            raw_file,output_file, ds
        )

    @task
    def load_data(processed_file):
        load_exchange_rates(processed_file)

    #task obj
    extract=extract_exchange_rate() #add this tag to dag
    validation=validate(extract)
    transform=transform_data(extract)
    load=load_data(transform)
    

    #set dependencies
    start >> extract >>validation >> transform >> load >> end

#build dag
dag=currency_pipeline()



#Idempotent means you can run the pipeline multiple times with the same input, and the final result in the database stays the same.
#"An idempotent ETL pipeline can be executed multiple times with the same input without changing the final state of the target database
# . We usually achieve this by using unique constraints together with UPSERT or ON CONFLICT logic to avoid duplicate records."

#primary key->one for entire table,cannot be null,uniquely identify record
#unique- there can be many for a table,prevent duplicates,,used to enforce business rules