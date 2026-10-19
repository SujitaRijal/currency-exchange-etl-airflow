import pytest
from datetime import datetime 
from unittest.mock import Mock,patch

from include.load.audit import (
    create_audit_table,insert_audit_log,get_start_time,update_audit_success,update_audit_failure,update_audit_skipped
)

@pytest.fixture
def fake_db():
    conn = Mock()
    cursor = Mock()

    conn.cursor.return_value = cursor
    return conn, cursor

@patch("include.load.audit.get_connection")
def test_create_audit_table_success(mock_get_connection,fake_db):
    conn, cursor = fake_db
    mock_get_connection.return_value = conn

    create_audit_table()

    mock_get_connection.assert_called_once()
    cursor.execute.assert_called_once()
    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()
    cursor.close.assert_called_once()
    conn.close.assert_called_once()

@patch("include.load.audit.get_connection")
def test_create_audit_table_exception(mock_get_connection,fake_db):
    conn, cursor = fake_db
    mock_get_connection.return_value = conn

    cursor.execute.side_effect=Exception("Database Error")
    with pytest.raises(Exception, match="Database Error"):
        create_audit_table()

    mock_get_connection.assert_called_once()
    cursor.execute.assert_called_once()
    conn.commit.assert_not_called()
    conn.rollback.assert_called_once()
    cursor.close.assert_called_once()
    conn.close.assert_called_once()


@patch("include.load.audit.get_connection")
def test_insert_audit_log_success(mock_get_connection,fake_db):
    conn, cursor = fake_db
    mock_get_connection.return_value= conn

    insert_audit_log(
        pipeline_name="currency_pipeline",
        run_id="run_001",
        execution_date="2026-10-14",
        start_time="2026-10-14 06:26:00+00:00",
        status="RUNNING"
    )

    mock_get_connection.assert_called_once()
    cursor.execute.assert_called_once_with(
        """
            INSERT INTO etl_audit_log
            (
                pipeline_name,
                run_id,
                execution_date,
                start_time,
                status
            )
            VALUES(%s, %s, %s, %s, %s)
            """,
        (
            "currency_pipeline",
            "run_001",
            "2026-10-14",
            "2026-10-14 06:26:00+00:00",
            "RUNNING"
        ),
    )
    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()
    cursor.close.assert_called_once()
    conn.close.assert_called_once()

@patch("include.load.audit.get_connection")
def test_insert_audit_log_exception(mock_get_connection,fake_db):
    conn, cursor=fake_db
    mock_get_connection.return_value = conn

    cursor.execute.side_effect = Exception("Database Error")

    with pytest.raises(Exception,match="Database Error"):
        insert_audit_log(
            "currency_pipeline",
            "run_001",
            "2026-10-14",
            "2026-10-14 06:26:00+00:00",
            "RUNNING"
        )
    mock_get_connection.assert_called_once()
    cursor.execute.assert_called_once()
    conn.commit.assert_not_called()
    conn.rollback.assert_called_once()
    cursor.close.assert_called_once()
    conn.close.assert_called_once()


@patch("include.load.audit.get_connection")
def test_get_start_time_exists(mock_get_connection,fake_db):
    conn, cursor = fake_db
    mock_get_connection.return_value = conn

    cursor.fetchone.return_value = ("2026-10-14 06:26:00+00:00",)

    result = get_start_time("run_001")

    assert result == "2026-10-14 06:26:00+00:00"

    mock_get_connection.assert_called_once()

    cursor.execute.assert_called_once_with(
         """
            SELECT start_time 
            FROM etl_audit_log
            WHERE run_id = %s
            """,
            ("run_001",)
    )

    cursor.fetchone.assert_called_once()
    cursor.close.assert_called_once()
    conn.close.assert_called_once()

@patch("include.load.audit.get_start_time")
@patch("include.load.audit.get_connection")

def test_update_audit_success(mock_get_connection,mock_get_start_time,fake_db):
    #Arrange
    conn, cursor = fake_db
    mock_get_connection.return_value = conn

    start_time = datetime(2026, 10, 18, 6, 26, 0)
    end_time = datetime(2026, 10, 18, 6, 27, 30)

    mock_get_start_time.return_value = start_time

    load_metrics = {
        "records_received": 100,
        "records_loaded": 98,
        "duplicates_skipped": 2,    
    }
    #Act
    update_audit_success("run_001",end_time,load_metrics)

    #Assert
    mock_get_connection.assert_called_once()
    mock_get_start_time.assert_called_once_with("run_001")
    cursor.execute.assert_called_once()
    sql,params=cursor.execute.call_args.args

    assert "UPDATE etl_audit_log" in sql
    assert "status = %s" in sql

    assert params == (
        end_time,
        90.0,
        "SUCCESS",
        100,
        98,
        2,
        "run_001",
    )

    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()
    cursor.close.assert_called_once()
    conn.close.assert_called_once()

@patch("include.load.audit.get_start_time")
@patch("include.load.audit.get_connection")
def test_update_audit_success_exception(mock_get_connection,mock_get_start_time,fake_db):
    conn, cursor = fake_db
    mock_get_connection.return_value = conn

    start_time = datetime(2026, 10, 18, 6, 26, 0)
    end_time = datetime(2026, 10, 18, 6, 27, 30)
    
    mock_get_start_time.return_value = start_time
    load_metrics = {
            "records_received": 100,
            "records_loaded": 98,
            "duplicates_skipped": 2,    
        }
    cursor.execute.side_effect= Exception("Database Error")

    with pytest.raises(Exception, match="Database Error"):
        update_audit_success("run_001",end_time,load_metrics)
    mock_get_connection.assert_called_once()
    mock_get_start_time.assert_called_once_with("run_001")

    cursor.execute.assert_called_once()

    conn.commit.assert_not_called()
    conn.rollback.assert_called_once()

    cursor.close.assert_called_once()
    conn.close.assert_called_once()



@patch("include.load.audit.get_start_time")
@patch("include.load.audit.get_connection")

def test_update_audit_failure_success(mock_get_connection,mock_get_start_time,fake_db):
    #Arrange
    conn, cursor = fake_db
    mock_get_connection.return_value = conn

    start_time = datetime(2026, 10, 18, 6, 26, 0)
    end_time = datetime(2026, 10, 18, 6, 27, 30)

    mock_get_start_time.return_value = start_time

    #Act
    update_audit_failure("run_001",end_time,"transform_task", "Invalid exchange rate")

    #Assert
    mock_get_connection.assert_called_once()
    mock_get_start_time.assert_called_once_with("run_001")
    cursor.execute.assert_called_once()
    sql,params=cursor.execute.call_args.args

    assert "UPDATE etl_audit_log" in sql
    assert "status = %s" in sql
    assert "failed_task = %s" in sql
    assert "error_message = %s" in sql


    assert params == (
        end_time,
        90.0,
        "FAILED",
        "transform_task",
        "Invalid exchange rate",
        "run_001",
    )

    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()
    cursor.close.assert_called_once()
    conn.close.assert_called_once()

@patch("include.load.audit.get_start_time")
@patch("include.load.audit.get_connection")
def test_update_audit_failure_exception(mock_get_connection,mock_get_start_time,fake_db):
    conn, cursor=fake_db
    mock_get_connection.return_value = conn

    start_time= datetime(2026, 10, 18, 6, 26, 0)
    end_time= datetime(2026, 10, 18, 6, 27, 30)

    mock_get_start_time.return_value = start_time

    cursor.execute.side_effect= Exception("Database Error")
    with pytest.raises(Exception, match="Database Error"):
        update_audit_failure("run_001",end_time,"transform_task", "Invalid exchange rate")
    mock_get_connection.assert_called_once()
    mock_get_start_time.assert_called_once_with("run_001")
    
    cursor.execute.assert_called_once()
    
    conn.commit.assert_not_called()
    conn.rollback.assert_called_once()
    
    cursor.close.assert_called_once()
    conn.close.assert_called_once()
    

@patch("include.load.audit.get_start_time")
@patch("include.load.audit.get_connection")

def test_update_audit_skipped_success(mock_get_connection,mock_get_start_time,fake_db):
    #Arrange
    conn, cursor = fake_db
    mock_get_connection.return_value = conn

    start_time = datetime(2026, 10, 18, 6, 26, 0)
    end_time = datetime(2026, 10, 18, 6, 27, 30)

    mock_get_start_time.return_value = start_time

    #Act
    update_audit_skipped("run_001",end_time)

    #Assert
    mock_get_connection.assert_called_once()
    mock_get_start_time.assert_called_once_with("run_001")
    cursor.execute.assert_called_once()
    sql,params=cursor.execute.call_args.args

    assert "UPDATE etl_audit_log" in sql
    assert "status = %s" in sql

    assert params == (
        end_time,
        90.0,
        "SKIPPED",
        "run_001",
    )

    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()
    cursor.close.assert_called_once()
    conn.close.assert_called_once()


@patch("include.load.audit.get_start_time")
@patch("include.load.audit.get_connection")
def test_update_audit_skipped_exception(mock_get_connection,mock_get_start_time,fake_db):
    conn, cursor=fake_db
    mock_get_connection.return_value = conn

    start_time= datetime(2026, 10, 18, 6, 26, 0)
    end_time= datetime(2026, 10, 18, 6, 27, 30)

    mock_get_start_time.return_value = start_time

    cursor.execute.side_effect= Exception("Database Error")
    with pytest.raises(Exception, match="Database Error"):
        update_audit_skipped("run_001",end_time)
    mock_get_connection.assert_called_once()
    mock_get_start_time.assert_called_once_with("run_001")
    
    cursor.execute.assert_called_once()
    
    conn.commit.assert_not_called()
    conn.rollback.assert_called_once()
    
    cursor.close.assert_called_once()
    conn.close.assert_called_once()




