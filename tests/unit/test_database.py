from unittest.mock import Mock, patch

import pytest

from include.load.database import get_connection


@patch("include.load.database.PostgresHook")
def test_get_connection_success(mock_hook):
    # Arrange
    mock_connection = Mock()

    mock_hook_instance = mock_hook.return_value
    mock_hook_instance.get_conn.return_value = mock_connection

    # Act
    result = get_connection()

    # Assert
    mock_hook.assert_called_once_with(postgres_conn_id="postgres_default")

    mock_hook_instance.get_conn.assert_called_once()
    assert result == mock_connection


@patch("include.load.database.PostgresHook")
def test_get_connection_exception(mock_hook):
    mock_hook.return_value.get_conn.side_effect = Exception(
        "Database connection failed"
    )

    with pytest.raises(Exception, match="Database connection failed"):
        get_connection()

    mock_hook.assert_called_once_with(postgres_conn_id="postgres_default")

    mock_hook.return_value.get_conn.assert_called_once()
