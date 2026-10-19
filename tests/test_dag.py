import pytest
from dags.currency_pipeline import dag
from airflow.timetables.interval import CronDataIntervalTimetable


def test_dag_loaded():
    assert dag is not None

def test_dag_id():
    assert dag.dag_id == "CurrencyETLPipeline"

def test_schedule():
    assert isinstance(dag.schedule , CronDataIntervalTimetable)

def test_catchup():
    assert dag.catchup is False

def test_tags():
    assert set(dag.tags) == {"ETL", "Currency", "PostgreSQL"}

def test_start_date():
    assert dag.start_date.year == 2026
    assert dag.start_date.month == 9
    assert dag.start_date.day ==  20

def test_number_of_tasks():
    assert len(dag.tasks) == 15

def test_task_ids():
    expected = {
        "start",
        "initialize_database",
        "start_audit",
        "extract_exchange_rate",
        "check_metadata",
        "validate",
        "transform_data",
        "quality",
        "load_data",
        "update_metadata",
        "purge_old_output_files",
        "finish_audit_success",
        "pipeline_report",
        "export_daily_audit",
        "end",
    }

    assert set(dag.task_ids)== expected

def test_dependencies():
    assert "initialize_database" in dag.get_task("start").downstream_task_ids
    assert "start_audit" in dag.get_task("initialize_database").downstream_task_ids
    assert "extract_exchange_rate" in dag.get_task("start_audit").downstream_task_ids
    assert "check_metadata" in dag.get_task("extract_exchange_rate").downstream_task_ids
    assert "validate" in dag.get_task("check_metadata").downstream_task_ids
    assert "transform_data" in dag.get_task("validate").downstream_task_ids
    assert "quality" in dag.get_task("transform_data").downstream_task_ids
    assert "load_data" in dag.get_task("quality").downstream_task_ids
    assert "update_metadata" in dag.get_task("load_data").downstream_task_ids
    assert "purge_old_output_files" in dag.get_task("update_metadata").downstream_task_ids
    assert "finish_audit_success" in dag.get_task("purge_old_output_files").downstream_task_ids
    assert "pipeline_report" in dag.get_task("finish_audit_success").downstream_task_ids
    assert "export_daily_audit" in dag.get_task("pipeline_report").downstream_task_ids
    assert "end" in dag.get_task("export_daily_audit").downstream_task_ids