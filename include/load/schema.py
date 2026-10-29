import logging

from include.load.database import get_connection

logger = logging.getLogger(__name__)


def create_exchange_rates_table():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS exchange_rates(
                id SERIAL PRIMARY KEY,
                load_date DATE,
                source_timestamp TEXT,
                base_currency VARCHAR(10),
                target_currency VARCHAR(10),
                exchange_rate NUMERIC(20,8),

                UNIQUE(load_date, base_currency, target_currency)
            )
            """)

        conn.commit()

        logger.info("exchange_rates table initialized")

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()
