import json
import pytest

from unittest.mock import Mock, patch

from include.load.loader import load_exchange_rates

@pytest.fixture
def processed_file(tmp_path):
    return tmp_path / "processed.json"

@pytest.fixture
def sample_data():
    return [
        {
            "load_date": "2026-10-07",
            "source_timestamp": "Wed, 07 Oct 2026 00:02:31 +0000",
            "base_currency": "USD",
            "target_currency": "NPR",
            "exchange_rate": 137.2,
        },
        {
            "load_date": "2026-10-07",
            "source_timestamp": "Wed, 07 Oct 2026 00:02:31 +0000",
            "base_currency": "USD",
            "target_currency": "EUR",
            "exchange_rate": 0.91,
        },
    ]

@pytest.fixture
def fake_db():
    conn = Mock()
    cursor = Mock()

    conn.cursor.return_value = cursor

    return conn, cursor

@pytest.fixture
def create_processed_file(processed_file):
    def _create_file(data):
        with open(processed_file, "w") as f:
            json.dump(data, f)
        return processed_file

    return _create_file

@patch("include.load.loader.get_connection")
def test_load_exchange_rates_success(mock_get_connection,sample_data,fake_db,create_processed_file):
    #Arrange
    conn, cursor = fake_db
    mock_get_connection.return_value = conn

    processed_file = create_processed_file(sample_data)

    cursor.rowcount = 2

    #Act
    result = load_exchange_rates(processed_file)

    #Assert
    assert result == {
        "records_received": 2,
        "records_loaded": 2,
        "duplicates_skipped": 0,
    }

    mock_get_connection.assert_called_once()
    cursor.execute.assert_called_once()
    cursor.executemany.assert_called_once()
    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()
    cursor.close.assert_called_once()
    conn.close.assert_called_once()


@patch("include.load.loader.get_connection")
def test_load_empty_file(mock_get_connection,create_processed_file,fake_db):
    # Arrange
    conn, cursor = fake_db
    mock_get_connection.return_value = conn

    processed_file = create_processed_file([])


    cursor.rowcount = 0

    #Act
    result = load_exchange_rates(processed_file)

    #Assert
    assert result == {
        "records_received": 0,
        "records_loaded": 0,
        "duplicates_skipped": 0,
    }

    mock_get_connection.assert_called_once()
    cursor.execute.assert_called_once()
    cursor.executemany.assert_called_once()
    _, values = cursor.executemany.call_args.args
    assert values == []

    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()

    cursor.close.assert_called_once()
    conn.close.assert_called_once()

@patch("include.load.loader.get_connection")
def test_load_duplicate_records(mock_get_connection,create_processed_file,sample_data,fake_db):
    conn, cursor = fake_db
    mock_get_connection.return_value = conn

    processed_file = create_processed_file(sample_data)


     # Simulate PostgreSQL inserting only one row
    cursor.rowcount = 1

    #Act
    result = load_exchange_rates(processed_file)

    #Assert
    assert result == {
            "records_received": 2,
            "records_loaded": 1,
            "duplicates_skipped": 1,
        }
    mock_get_connection.assert_called_once()

    cursor.execute.assert_called_once()
    cursor.executemany.assert_called_once()

    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()

    cursor.close.assert_called_once()
    conn.close.assert_called_once()

@patch("include.load.loader.get_connection")
def test_load_database_exception(mock_get_connection,create_processed_file,sample_data,fake_db):
    conn,cursor = fake_db
    mock_get_connection.return_value = conn

    processed_file = create_processed_file(sample_data)


    cursor.executemany.side_effect = Exception("Database Error")

    #Act + Assert
    with pytest.raises(Exception, match ="Database Error"):
        load_exchange_rates(processed_file)

    mock_get_connection.assert_called_once()

    cursor.execute.assert_called_once()
    cursor.executemany.assert_called_once()

    conn.rollback.assert_called_once()
    conn.commit.assert_not_called()

    cursor.close.assert_called_once()
    conn.close.assert_called_once()

    
    


