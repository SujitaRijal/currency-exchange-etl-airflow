#responsible for reading processed json,calling database connection,inserting rows,knows nthg about how posgres credentials are stored

import json
from include.load.database import get_connection
import logging

logger=logging.getLogger(__name__)


def load_exchange_rates(processed_file):
    """
    Reads transformed exchange rates and loads them into postgreSQL.

    """
    with open(processed_file) as f:
        data=json.load(f)

    #connect to postgresql
    conn = get_connection()  #conn-open connection to PostgreSQL

    cursor = conn.cursor() #connection alone can't execute sql-need a cursor,cursor is what actually sends sql commands

    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS exchange_rates(
        id SERIAL PRIMARY KEY,
        load_date DATE,
        source_timestamp TEXT,
        base_currency VARCHAR(10),
        target_currency VARCHAR(10),
        exchange_rate NUMERIC(20,8),

        UNIQUE(load_date,base_currency,target_currency)
        )
        """)

        #build the list of values for bulk insert
        values = [
             (
                record["load_date"],
                record["source_timestamp"],
                record["base_currency"],
                record["target_currency"],
                record["exchange_rate"]
             ) 
            for record in data
        ]   

        cursor.executemany(
            """ 
            INSERT INTO exchange_rates(
            load_date,
            source_timestamp,
            base_currency,
            target_currency,
            exchange_rate
            )
            VALUES (%s, %s, %s, %s, %s) 

            ON CONFLICT(load_date,base_currency,target_currency) 
            DO NOTHING;
            """,
            values
        )
        #%s simply a placeholder for a value
    
        inserted = cursor.rowcount
        skipped = len(values)-inserted

        conn.commit()  #everything in this transaction is correct, save it permanently

        records_received=len(data)
        # -----------------------------
        # Load summary
        # -----------------------------
        logger.info("========== Load Summary ==========")
        logger.info(f"Records Received    : {records_received}")
        logger.info(f"Records Inserted    : {inserted}")
        logger.info(f"Duplicates Skipped  : {skipped}")
        logger.info("==================================")

    except Exception as e:
        conn.rollback()
        logger.error(f"Error loading data :{e}")
        raise

    finally:
        cursor.close() #done executing sql,release the cursor

        conn.close()  #done talking to PostgreSQL, so we close connection



    