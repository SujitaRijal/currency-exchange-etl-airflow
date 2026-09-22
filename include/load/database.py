# Responsible for connecting to PostgreSQL.
# This module knows nothing about exchange rates or business logic.
#connection-instead of storing credentials on your code,airflow stores them securely in metadata database

from airflow.providers.postgres.hooks.postgres import PostgresHook
 #This imports Airflow's PostgreSQL helper.
#"Airflow, please connect to PostgreSQL using one of your saved Connections."

def get_connection():
    """
    Returns a PostgreSQL connection using
    the Airflow Connection 'postgres_default'.
    """

    hook = PostgresHook(postgres_conn_id="postgres_default") #Find the Connection whose ID is postgres_default.

    return hook.get_conn()  #This returns a normal PostgreSQL connection object.