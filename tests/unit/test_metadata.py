import pytest
from unittest.mock import Mock, patch
from include.load.metadata import (
    create_metadata_table,get_last_processed_timestamp,update_last_processed_timestamp
)

@pytest.fixture
def fake_db():
    conn = Mock()
    cursor = Mock()

    conn.cursor.return_value = cursor
    return conn, cursor

@patch("include.load.metadata.get_connection")
def test_create_metadata_table_success(mock_get_connection,fake_db):
    #Arrange
    conn , cursor = fake_db
    mock_get_connection.return_value = conn

    #Act
    create_metadata_table()

    #Assert
    mock_get_connection.assert_called_once()
    cursor.execute.assert_called_once()
    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()
    cursor.close.assert_called_once()
    conn.close.assert_called_once()


@patch("include.load.metadata.get_connection")
def test_create_metadata_table_exception(mock_get_connection,fake_db):
    conn , cursor = fake_db
    mock_get_connection.return_value = conn

    cursor.execute.side_effect = Exception("Database Error")

    #Act + Asssert
    with pytest.raises(Exception, match="Database Error"):
        create_metadata_table()

    mock_get_connection.assert_called_once()
    cursor.execute.assert_called_once()
    conn.commit.assert_not_called()
    conn.rollback.assert_called_once()
    cursor.close.assert_called_once()
    conn.close.assert_called_once()



@patch("include.load.metadata.get_connection")
def test_get_last_processed_timestamp_exists(mock_get_connection,fake_db):
    #Arrange
    conn , cursor = fake_db
    mock_get_connection.return_value = conn

    cursor.fetchone.return_value = ("Wed, 14 Oct 2026 06:26:00 +0000",)

    #Act
    result = get_last_processed_timestamp("currency_pipeline")

    #Assert
    assert result == "Wed, 14 Oct 2026 06:26:00 +0000"

    mock_get_connection.assert_called_once()
    cursor.execute.assert_called_once_with(
         """
            SELECT  last_processed_timestamp
            FROM  etl_metadata
            WHERE pipeline_name= %s
            """,
            ("currency_pipeline",)
    )

    cursor.fetchone.assert_called_once()
    cursor.close.assert_called_once()
    conn.close.assert_called_once()


@patch("include.load.metadata.get_connection")
def test_get_last_processed_timestamp_not_found(mock_get_connection,fake_db):
    #Arrange
    conn, cursor = fake_db
    mock_get_connection.return_value = conn

    cursor.fetchone.return_value = None
    #Act
    result =get_last_processed_timestamp("currency_pipeline")

    #Assert
    assert result is None

    mock_get_connection.assert_called_once()
    cursor.execute.assert_called_once()
    cursor.fetchone.assert_called_once()
    cursor.close.assert_called_once()
    conn.close.assert_called_once()

@patch("include.load.metadata.get_connection")
def test_get_last_processed_timestamp_exception(mock_get_connection,fake_db):
    conn, cursor = fake_db
    mock_get_connection.return_value = conn

    cursor.execute.side_effect= Exception("Database error")
    with pytest.raises(Exception, match="Database error"):
        get_last_processed_timestamp("currency_pipeline")

    mock_get_connection.assert_called_once()
    cursor.execute.assert_called_once()
    cursor.close.assert_called_once()
    conn.close.assert_called_once()

@patch("include.load.metadata.get_connection")
def test_update_last_processed_timestamp(mock_get_connection,fake_db):
    #Arrange
    conn, cursor= fake_db
    mock_get_connection.return_value = conn

    #Act
    update_last_processed_timestamp("currency_pipeline","Wed, 14 Oct 2026 06:26:00 +0000",)

    #Assert
    mock_get_connection.assert_called_once()
    cursor.execute.assert_called_once_with(
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
            ("currency_pipeline","Wed, 14 Oct 2026 06:26:00 +0000",)
            
    )
    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()

    cursor.close.assert_called_once()
    conn.close.assert_called_once()

@patch("include.load.metadata.get_connection")
def test_update_last_processed_timestamp_exception(mock_get_connection,fake_db):
    conn, cursor = fake_db
    mock_get_connection.return_value = conn

    cursor.execute.side_effect=Exception("Database Error")

    with pytest.raises(Exception, match="Database Error"):
        update_last_processed_timestamp("currency_pipeline","Wed, 14 Oct 2026 06:26:00 +0000",)
    mock_get_connection.assert_called_once()
    cursor.execute.assert_called_once()
    conn.commit.assert_not_called()
    conn.rollback.assert_called_once()
    cursor.close.assert_called_once()
    conn.close.assert_called_once()




    


