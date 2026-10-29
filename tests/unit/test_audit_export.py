import csv
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from include.reports.audit_export import export_audit_csv


@patch("include.reports.audit_export.get_connection")
def test_export_audit_csv_success(mock_get_connection):
    # Arrange
    conn = MagicMock()
    cursor = MagicMock()

    mock_get_connection.return_value = conn
    conn.cursor.return_value = cursor

    cursor.fetchall.return_value = [
        (
            "CurrencyETLPipeline",
            "run_001",
            "2026-10-23",
            "06:00",
            "06:02",
            120,
            "SUCCESS",
            170,
            170,
            0,
            None,
            None,
        )
    ]
    cursor.description = [
        ("pipeline_name",),
        ("run_id",),
        ("execution_date",),
        ("start_time",),
        ("end_time",),
        ("duration_seconds",),
        ("status",),
        ("records_received",),
        ("records_loaded",),
        ("duplicates_skipped",),
        ("failed_task",),
        ("error_message",),
    ]

    # Act
    result = export_audit_csv("2026-10-23")

    # Assert
    mock_get_connection.assert_called_once()
    conn.cursor.assert_called_once()

    cursor.execute.assert_called_once_with(
        """
                SELECT
                pipeline_name,
                run_id,
                execution_date,
                start_time,
                end_time,
                duration_seconds,
                status,
                records_received,
                records_loaded,
                duplicates_skipped,
                failed_task,
                error_message
                FROM etl_audit_log
                WHERE execution_date = %s
                ORDER BY start_time;
            """,
        ("2026-10-23",),
    )

    cursor.fetchall.assert_called_once()
    assert result.endswith("audit_2026-10-23.csv")
    assert Path(result).exists()
    cursor.close.assert_called_once()
    conn.close.assert_called_once()

    with open(result, "r", newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)

    assert rows[0] == [
        "pipeline_name",
        "run_id",
        "execution_date",
        "start_time",
        "end_time",
        "duration_seconds",
        "status",
        "records_received",
        "records_loaded",
        "duplicates_skipped",
        "failed_task",
        "error_message",
    ]

    assert rows[1] == [
        "CurrencyETLPipeline",
        "run_001",
        "2026-10-23",
        "06:00",
        "06:02",
        "120",
        "SUCCESS",
        "170",
        "170",
        "0",
        "",
        "",
    ]


@patch("include.reports.audit_export.get_connection")
def test_export_audit_csv_exception(mock_get_connection):
    conn = MagicMock()
    cursor = MagicMock()

    mock_get_connection.return_value = conn
    conn.cursor.return_value = cursor

    cursor.execute.side_effect = Exception("Database query failed")

    with pytest.raises(Exception, match="Database query failed"):
        export_audit_csv("2026-10-23")

    cursor.close.assert_called_once()
    conn.close.assert_called_once()
