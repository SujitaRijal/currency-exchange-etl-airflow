import json
from datetime import date

import pytest

from include.load.database import get_connection
from include.load.loader import load_exchange_rates

TEST_DATE = date.today().isoformat()


@pytest.fixture
def cleanup_exchange_rates():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM exchange_rates
        WHERE load_date = %s
        AND base_currency = 'USD'
        AND target_currency IN ('EUR','GBP','NPR');
        """,
        (TEST_DATE,),
    )

    conn.commit()

    cursor.close()
    conn.close()

    yield

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM exchange_rates
        WHERE load_date = %s
        AND base_currency = 'USD'
        AND target_currency IN ('EUR','GBP','NPR');
        """,
        (TEST_DATE,),
    )
    conn.commit()
    cursor.close()
    conn.close()


def test_load_exchange_rates(tmp_path, cleanup_exchange_rates):
    # Sample processed JSON data
    data = [
        {
            "load_date": TEST_DATE,
            "source_timestamp": "123456",
            "base_currency": "USD",
            "target_currency": "EUR",
            "exchange_rate": 0.92,
        },
        {
            "load_date": TEST_DATE,
            "source_timestamp": "123456",
            "base_currency": "USD",
            "target_currency": "GBP",
            "exchange_rate": 0.78,
        },
        {
            "load_date": TEST_DATE,
            "source_timestamp": "123456",
            "base_currency": "USD",
            "target_currency": "NPR",
            "exchange_rate": 140.50,
        },
    ]
    # Create temporary processed JSON file
    processed_file = tmp_path / "processed.json"
    processed_file.write_text(json.dumps(data))

    # Call real load function
    result = load_exchange_rates(processed_file)

    # Verify returned load metrics
    assert result["records_received"] == 3
    assert result["records_loaded"] == 3
    assert result["duplicates_skipped"] == 0

    # verify actual database insertion
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
            SELECT COUNT(*)
            FROM exchange_rates
            WHERE load_date = %s
            AND base_currency = 'USD'
            AND target_currency IN ('EUR','GBP','NPR');
            """,
        (TEST_DATE,),
    )

    count = cursor.fetchone()[0]
    assert count == 3

    cursor.close()
    conn.close()


def test_load_exchange_rates_duplicates(tmp_path, cleanup_exchange_rates):
    data = [
        {
            "load_date": TEST_DATE,
            "source_timestamp": "123456",
            "base_currency": "USD",
            "target_currency": "EUR",
            "exchange_rate": 0.92,
        },
        {
            "load_date": TEST_DATE,
            "source_timestamp": "123456",
            "base_currency": "USD",
            "target_currency": "GBP",
            "exchange_rate": 0.78,
        },
        {
            "load_date": TEST_DATE,
            "source_timestamp": "123456",
            "base_currency": "USD",
            "target_currency": "NPR",
            "exchange_rate": 140.50,
        },
    ]

    # Create temporary processed JSON file
    processed_file = tmp_path / "processed.json"
    processed_file.write_text(json.dumps(data))

    # First load
    first_result = load_exchange_rates(processed_file)
    assert first_result["records_received"] == 3
    assert first_result["records_loaded"] == 3
    assert first_result["duplicates_skipped"] == 0

    # second load with the same file
    second_result = load_exchange_rates(processed_file)
    assert second_result["records_received"] == 3
    assert second_result["records_loaded"] == 0
    assert second_result["duplicates_skipped"] == 3

    # verify actual database still contains 3 data
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
         SELECT COUNT(*)
         FROM exchange_rates
         WHERE load_date = %s
         AND base_currency = 'USD'
        AND target_currency IN ('EUR','GBP','NPR');
        """,
        (TEST_DATE,),
    )
    count = cursor.fetchone()[0]
    assert count == 3
    cursor.close()
    conn.close()
