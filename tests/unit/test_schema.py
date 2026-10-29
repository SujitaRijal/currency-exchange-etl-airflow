from unittest.mock import patch

import pytest

from include.load.schema import create_exchange_rates_table


@patch("include.load.schema.get_connection")
def test_create_exchange_rates_table(mock_get_connection):
    # Arrange
    conn = mock_get_connection.return_value
    cursor = conn.cursor.return_value

    # Act
    create_exchange_rates_table()

    # Assert
    mock_get_connection.assert_called_once()

    cursor.execute.assert_called_once()

    conn.commit.assert_called_once()

    cursor.close.assert_called_once()

    conn.close.assert_called_once()


@patch("include.load.schema.get_connection")
def test_create_exchange_rates_table_exception(mock_get_connection):

    conn = mock_get_connection.return_value
    cursor = conn.cursor.return_value

    cursor.execute.side_effect = Exception("Table creation failed")

    with pytest.raises(Exception, match="Table creation failed"):
        create_exchange_rates_table()

    conn.rollback.assert_called_once()

    cursor.close.assert_called_once()

    conn.close.assert_called_once()
