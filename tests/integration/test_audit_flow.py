from datetime import datetime, timedelta

import pytest

from airflow.utils.timezone import utc
from include.load.audit import (
    create_audit_table,
    insert_audit_log,
    update_audit_failure,
    update_audit_skipped,
    update_audit_success,
)
from include.load.database import get_connection


@pytest.fixture
def cleanup_audit_records():
    yield

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM etl_audit_log
        WHERE run_id LIKE 'integration_%';
        """)

    conn.commit()

    cursor.close()
    conn.close()


def test_insert_audit_log(cleanup_audit_records):
    create_audit_table()

    run_id = "integration_test_001"

    insert_audit_log(
        pipeline_name="CurrencyETLPipeline",
        run_id=run_id,
        execution_date="2026-10-25",
        start_time=datetime.now(utc),
        status="RUNNING",
    )
    # # Verify from real database
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT pipeline_name, status
        FROM etl_audit_log
        WHERE run_id = %s;
        """,
        (run_id,),
    )

    result = cursor.fetchone()
    assert result[0] == "CurrencyETLPipeline"
    assert result[1] == "RUNNING"


def test_update_audit_success(cleanup_audit_records):
    create_audit_table()
    run_id = "integration_success_001"

    start_time = datetime.now(utc)
    # # First create RUNNING audit record
    insert_audit_log(
        pipeline_name="CurrencyETLPipeline",
        run_id=run_id,
        execution_date="2026-10-25",
        start_time=start_time,
        status="RUNNING",
    )
    load_metrics = {
        "records_received": 170,
        "records_loaded": 168,
        "duplicates_skipped": 2,
    }
    end_time = start_time + timedelta(seconds=120)

    # update RUNNING-SUCCESS
    update_audit_success(run_id=run_id, end_time=end_time, load_metrics=load_metrics)

    # verify from real database
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            status,
            records_received,
            records_loaded,
            duplicates_skipped,
            duration_seconds
        FROM etl_audit_log
        WHERE run_id = %s;
        """,
        (run_id,),
    )

    result = cursor.fetchone()
    assert result[0] == "SUCCESS"
    assert result[1] == 170
    assert result[2] == 168
    assert result[3] == 2
    assert result[4] == 120

    cursor.close()
    conn.close()


def test_update_audit_failure(cleanup_audit_records):
    create_audit_table()
    run_id = "integration_failure_001"
    start_time = datetime.now(utc)

    # first create running audit record
    insert_audit_log(
        pipeline_name="CurrencyETLPipeline",
        run_id=run_id,
        execution_date="2026-10-25",
        start_time=start_time,
        status="RUNNING",
    )
    end_time = start_time + timedelta(seconds=30)
    # Update Running- Failed
    update_audit_failure(
        run_id=run_id,
        end_time=end_time,
        failed_task="transform_data",
        error_message="Validation failed",
    )

    # Verify from real database
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            status,
            failed_task,
            error_message,
            duration_seconds
        FROM etl_audit_log
        WHERE run_id = %s;
        """,
        (run_id,),
    )

    result = cursor.fetchone()
    assert result[0] == "FAILED"
    assert result[1] == "transform_data"
    assert result[2] == "Validation failed"
    assert result[3] == 30

    cursor.close()
    conn.close()


def test_update_audit_skipped(cleanup_audit_records):
    create_audit_table()
    run_id = "integration_skipped_001"
    start_time = datetime.now(utc)

    # first create running audit record
    insert_audit_log(
        pipeline_name="CurrencyETLPipeline",
        run_id=run_id,
        execution_date="2026-10-25",
        start_time=start_time,
        status="RUNNING",
    )
    end_time = start_time + timedelta(seconds=10)
    # Update Running- Skipped
    update_audit_skipped(run_id=run_id, end_time=end_time)

    # Verify from real database
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            status,
            duration_seconds
        FROM etl_audit_log
        WHERE run_id = %s;
        """,
        (run_id,),
    )

    result = cursor.fetchone()
    assert result[0] == "SKIPPED"
    assert result[1] == 10

    cursor.close()
    conn.close()
