#responsible for creating metadata table,checking last processed timestamp,updating metadata
from include.load.database import get_connection
import logging

logger=logging.getLogger(__name__)

def create_metadata_table():
    conn=get_connection()
    cursor=conn.cursor()

    try :
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS etl_metadata(
            pipeline_name VARCHAR(100) PRIMARY KEY,
            last_processed_timestamp TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        conn.commit()
        logger.info("ETL metadata table is ready")

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()


def get_last_processed_timestamp(pipeline_name):
    conn=get_connection()
    cursor=conn.cursor()

    try:
        logger.info(f"Checking last processed timestamp for {pipeline_name}")
        cursor.execute(
            """
            SELECT  last_processed_timestamp
            FROM  etl_metadata
            WHERE pipeline_name= %s
            """,
            (pipeline_name,) #comma creates tuple
        )

        result=cursor.fetchone() #expect at most one two,name is primary key and there wont be two row having same name

        if result:
            logger.info(f"Found timestamp: {result[0]}")
            return result[0]
        
        logger.info("No previous timestamp found.")
        return None


    except Exception:
        logger.exception("Failed to fetch last processed timestamp.")
        raise

    finally:
        cursor.close()
        conn.close()


#Upsert-if new then insert, otherwise update existing row,,two query at same
def update_last_processed_timestamp(pipeline_name,timestamp):  # Insert or update the last processed timestamp for the pipeline
    conn=get_connection()
    cursor=conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO etl_metadata(
            pipeline_name,
            last_processed_timestamp
            ) 
            VALUES (%s, %s)

            ON CONFLICT (pipeline_name)   
            DO UPDATE SET
                last_processed_timestamp = EXCLUDED.last_processed_timestamp,
                updated_at = current_timestamp
            """,
            (pipeline_name,timestamp)
        )

        conn.commit()

        logger.info(f"Updated metadata for pipeline '{pipeline_name}' with timestamp '{timestamp}'.")
        
    except Exception:
        logger.exception("Failed to update ETL metadata")
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

#If a row with this pipeline already exists, update its timestamp using the timestamp from the row I was trying to insert."--excluded
        


    


