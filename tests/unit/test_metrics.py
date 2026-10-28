from unittest.mock import MagicMock, patch

import pytest

from include.reports.metrics import (
    get_average_duration,
    get_failed_runs,
    get_failure_rate,
    get_skipped_runs,
    get_success_rate,
    get_successful_runs,
    get_total_duplicates_skipped,
    get_total_records_loaded,
    get_total_records_received,
    get_total_runs,
)


@patch("include.reports.metrics.get_connection")
def test_get_total_runs_success(mock_get_connection):

    conn = MagicMock()
    cursor = MagicMock()

    mock_get_connection.return_value = conn
    conn.cursor.return_value = cursor
    cursor.fetchone.return_value = (10,)

    result = get_total_runs()

    assert result == 10

    mock_get_connection.assert_called_once()
    conn.cursor.assert_called_once()
    cursor.execute.assert_called_once()
    cursor.fetchone.assert_called_once()
    cursor.close.assert_called_once()
    conn.close.assert_called_once()


@patch("include.reports.metrics.get_connection")
def test_get_total_runs_exception(mock_get_connection):
    conn = MagicMock()
    cursor = MagicMock()
    mock_get_connection.return_value = conn
    conn.cursor.return_value = cursor

    cursor.execute.side_effect = Exception("Failed to fetch total pipeline runs")

    with pytest.raises(Exception, match="Failed to fetch total pipeline runs"):
        get_total_runs()
    cursor.close.assert_called_once()
    conn.close.assert_called_once()


@patch("include.reports.metrics.get_connection")
def test_get_successful_runs_success(mock_get_connection):

    conn = MagicMock()
    cursor = MagicMock()

    mock_get_connection.return_value = conn
    conn.cursor.return_value = cursor
    cursor.fetchone.return_value = (5,)

    result = get_successful_runs()

    assert result == 5

    mock_get_connection.assert_called_once()
    conn.cursor.assert_called_once()
    cursor.execute.assert_called_once()
    cursor.fetchone.assert_called_once()
    cursor.close.assert_called_once()
    conn.close.assert_called_once()


@patch("include.reports.metrics.get_connection")
def test_get_successful_runs_exception(mock_get_connection):
    conn = MagicMock()
    cursor = MagicMock()
    mock_get_connection.return_value = conn
    conn.cursor.return_value = cursor

    cursor.execute.side_effect = Exception("Failed to fetch successful pipeline runs")

    with pytest.raises(Exception, match="Failed to fetch successful pipeline runs"):
        get_successful_runs()
    cursor.close.assert_called_once()
    conn.close.assert_called_once()


@patch("include.reports.metrics.get_connection")
def test_get_failed_runs_success(mock_get_connection):

    conn = MagicMock()
    cursor = MagicMock()

    mock_get_connection.return_value = conn
    conn.cursor.return_value = cursor
    cursor.fetchone.return_value = (3,)

    result = get_failed_runs()

    assert result == 3

    mock_get_connection.assert_called_once()
    conn.cursor.assert_called_once()
    cursor.execute.assert_called_once()
    cursor.fetchone.assert_called_once()
    cursor.close.assert_called_once()
    conn.close.assert_called_once()


@patch("include.reports.metrics.get_connection")
def test_get_failed_runs_exception(mock_get_connection):
    conn = MagicMock()
    cursor = MagicMock()
    mock_get_connection.return_value = conn
    conn.cursor.return_value = cursor

    cursor.execute.side_effect = Exception("Failed to fetch failed pipeline runs")

    with pytest.raises(Exception, match="Failed to fetch failed pipeline runs"):
        get_failed_runs()
    cursor.fetchone.assert_not_called()
    cursor.close.assert_called_once()
    conn.close.assert_called_once()


@patch("include.reports.metrics.get_connection")
def test_get_skipped_runs_success(mock_get_connection):

    conn = MagicMock()
    cursor = MagicMock()

    mock_get_connection.return_value = conn
    conn.cursor.return_value = cursor
    cursor.fetchone.return_value = (2,)

    result = get_skipped_runs()

    assert result == 2

    mock_get_connection.assert_called_once()
    conn.cursor.assert_called_once()
    cursor.execute.assert_called_once()
    cursor.fetchone.assert_called_once()
    cursor.close.assert_called_once()
    conn.close.assert_called_once()


@patch("include.reports.metrics.get_connection")
def test_get_skipped_runs_exception(mock_get_connection):
    conn = MagicMock()
    cursor = MagicMock()
    mock_get_connection.return_value = conn
    conn.cursor.return_value = cursor

    cursor.execute.side_effect = Exception("Failed to fetch skipped pipeline runs")

    with pytest.raises(Exception, match="Failed to fetch skipped pipeline runs"):
        get_skipped_runs()
    cursor.fetchone.assert_not_called()
    cursor.close.assert_called_once()
    conn.close.assert_called_once()


@patch("include.reports.metrics.get_connection")
def test_get_average_duration_success(mock_get_connection):
    conn = MagicMock()
    cursor = MagicMock()

    mock_get_connection.return_value = conn
    conn.cursor.return_value = cursor

    cursor.fetchone.return_value = (126.244,)
    result = get_average_duration()

    assert result == 126.24

    mock_get_connection.assert_called_once()
    conn.cursor.assert_called_once()
    cursor.execute.assert_called_once()
    cursor.fetchone.assert_called_once()
    cursor.close.assert_called_once()
    conn.close.assert_called_once()


@patch("include.reports.metrics.get_connection")
def test_get_average_duration_no_data(mock_get_connection):
    conn = MagicMock()
    cursor = MagicMock()

    mock_get_connection.return_value = conn
    conn.cursor.return_value = cursor

    cursor.fetchone.return_value = (None,)
    result = get_average_duration()

    assert result == 0
    mock_get_connection.assert_called_once()
    conn.cursor.assert_called_once()
    cursor.execute.assert_called_once()
    cursor.fetchone.assert_called_once()
    cursor.close.assert_called_once()
    conn.close.assert_called_once()


@patch("include.reports.metrics.get_connection")
def test_get_average_duration_exception(mock_get_connection):
    conn = MagicMock()
    cursor = MagicMock()

    mock_get_connection.return_value = conn
    conn.cursor.return_value = cursor

    cursor.execute.side_effect = Exception("Failed to fetch average pipeline execution")

    with pytest.raises(Exception, match="Failed to fetch average pipeline execution"):
        get_average_duration()
    cursor.fetchone.assert_not_called()
    cursor.close.assert_called_once()
    conn.close.assert_called_once()


@patch("include.reports.metrics.get_connection")
def test_get_total_records_received_success(mock_get_connection):
    conn = MagicMock()
    cursor = MagicMock()

    mock_get_connection.return_value = conn
    conn.cursor.return_value = cursor

    cursor.fetchone.return_value = (200,)
    result = get_total_records_received()

    assert result == 200

    mock_get_connection.assert_called_once()
    conn.cursor.assert_called_once()
    cursor.execute.assert_called_once()
    cursor.fetchone.assert_called_once()
    cursor.close.assert_called_once()
    conn.close.assert_called_once()


@patch("include.reports.metrics.get_connection")
def test_get_total_records_received_no_data(mock_get_connection):
    conn = MagicMock()
    cursor = MagicMock()

    mock_get_connection.return_value = conn
    conn.cursor.return_value = cursor

    cursor.fetchone.return_value = (None,)
    result = get_total_records_received()

    assert result == 0
    mock_get_connection.assert_called_once()
    conn.cursor.assert_called_once()
    cursor.execute.assert_called_once()
    cursor.fetchone.assert_called_once()
    cursor.close.assert_called_once()
    conn.close.assert_called_once()


@patch("include.reports.metrics.get_connection")
def test_get_total_records_received_exception(mock_get_connection):
    conn = MagicMock()
    cursor = MagicMock()

    mock_get_connection.return_value = conn
    conn.cursor.return_value = cursor

    cursor.execute.side_effect = Exception("Failed to fetch total records received")

    with pytest.raises(Exception, match="Failed to fetch total records received"):
        get_total_records_received()
    cursor.fetchone.assert_not_called()
    cursor.close.assert_called_once()
    conn.close.assert_called_once()


@patch("include.reports.metrics.get_connection")
def test_get_total_records_loaded_success(mock_get_connection):
    conn = MagicMock()
    cursor = MagicMock()

    mock_get_connection.return_value = conn
    conn.cursor.return_value = cursor

    cursor.fetchone.return_value = (100,)
    result = get_total_records_loaded()

    assert result == 100

    mock_get_connection.assert_called_once()
    conn.cursor.assert_called_once()
    cursor.execute.assert_called_once()
    cursor.fetchone.assert_called_once()
    cursor.close.assert_called_once()
    conn.close.assert_called_once()


@patch("include.reports.metrics.get_connection")
def test_get_total_records_loaded_no_data(mock_get_connection):
    conn = MagicMock()
    cursor = MagicMock()

    mock_get_connection.return_value = conn
    conn.cursor.return_value = cursor

    cursor.fetchone.return_value = (None,)
    result = get_total_records_loaded()

    assert result == 0
    mock_get_connection.assert_called_once()
    conn.cursor.assert_called_once()
    cursor.execute.assert_called_once()
    cursor.fetchone.assert_called_once()
    cursor.close.assert_called_once()
    conn.close.assert_called_once()


@patch("include.reports.metrics.get_connection")
def test_get_total_records_loaded_exception(mock_get_connection):
    conn = MagicMock()
    cursor = MagicMock()

    mock_get_connection.return_value = conn
    conn.cursor.return_value = cursor

    cursor.execute.side_effect = Exception("Failed to fetch total records loaded")

    with pytest.raises(Exception, match="Failed to fetch total records loaded"):
        get_total_records_loaded()
    cursor.fetchone.assert_not_called()
    cursor.close.assert_called_once()
    conn.close.assert_called_once()


@patch("include.reports.metrics.get_connection")
def test_get_total_duplicates_skipped_success(mock_get_connection):
    conn = MagicMock()
    cursor = MagicMock()

    mock_get_connection.return_value = conn
    conn.cursor.return_value = cursor

    cursor.fetchone.return_value = (100,)
    result = get_total_duplicates_skipped()

    assert result == 100

    mock_get_connection.assert_called_once()
    conn.cursor.assert_called_once()
    cursor.execute.assert_called_once()
    cursor.fetchone.assert_called_once()
    cursor.close.assert_called_once()
    conn.close.assert_called_once()


@patch("include.reports.metrics.get_connection")
def test_get_total_duplicates_skipped_no_data(mock_get_connection):
    conn = MagicMock()
    cursor = MagicMock()

    mock_get_connection.return_value = conn
    conn.cursor.return_value = cursor

    cursor.fetchone.return_value = (None,)
    result = get_total_duplicates_skipped()

    assert result == 0
    mock_get_connection.assert_called_once()
    conn.cursor.assert_called_once()
    cursor.execute.assert_called_once()
    cursor.fetchone.assert_called_once()
    cursor.close.assert_called_once()
    conn.close.assert_called_once()


@patch("include.reports.metrics.get_connection")
def test_get_total_duplicates_skipped_exception(mock_get_connection):
    conn = MagicMock()
    cursor = MagicMock()

    mock_get_connection.return_value = conn
    conn.cursor.return_value = cursor

    cursor.execute.side_effect = Exception("Failed to fetch total duplicates skipped")

    with pytest.raises(Exception, match="Failed to fetch total duplicates skipped"):
        get_total_duplicates_skipped()
    cursor.fetchone.assert_not_called()
    cursor.close.assert_called_once()
    conn.close.assert_called_once()


@patch("include.reports.metrics.get_successful_runs")
@patch("include.reports.metrics.get_total_runs")
def test_get_success_rate_success(mock_get_total_runs, mock_get_successful_runs):
    mock_get_total_runs.return_value = 10
    mock_get_successful_runs.return_value = 8

    result = get_success_rate()

    assert result == 80.0

    mock_get_total_runs.assert_called_once()
    mock_get_successful_runs.assert_called_once()


@patch("include.reports.metrics.get_successful_runs")
@patch("include.reports.metrics.get_total_runs")
def test_get_success_rate_zero_runs(mock_get_total_runs, mock_get_successful_runs):
    mock_get_total_runs.return_value = 0
    mock_get_successful_runs.return_value = 0

    result = get_success_rate()

    assert result == 0

    mock_get_total_runs.assert_called_once()
    mock_get_successful_runs.assert_called_once()


@patch("include.reports.metrics.get_failed_runs")
@patch("include.reports.metrics.get_total_runs")
def test_get_failure_rate_success(mock_get_total_runs, mock_get_failed_runs):
    mock_get_total_runs.return_value = 10
    mock_get_failed_runs.return_value = 2

    result = get_failure_rate()

    assert result == 20.0

    mock_get_total_runs.assert_called_once()
    mock_get_failed_runs.assert_called_once()


@patch("include.reports.metrics.get_failed_runs")
@patch("include.reports.metrics.get_total_runs")
def test_get_failure_rate_zero_runs(mock_get_total_runs, mock_get_failed_runs):
    mock_get_total_runs.return_value = 0
    mock_get_failed_runs.return_value = 0

    result = get_failure_rate()

    assert result == 0

    mock_get_total_runs.assert_called_once()
    mock_get_failed_runs.assert_called_once()
