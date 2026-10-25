from unittest.mock import Mock, patch
from pathlib import Path
from include.reports.report_generator import (generate_pipeline_report,print_pipeline_report,save_pipeline_report)
from include.reports.report_generator import PIPELINE_NAME

@patch("include.reports.report_generator.get_failure_rate")
@patch("include.reports.report_generator.get_success_rate")
@patch("include.reports.report_generator.get_total_duplicates_skipped")
@patch("include.reports.report_generator.get_total_records_loaded")
@patch("include.reports.report_generator.get_total_records_received")
@patch("include.reports.report_generator.get_average_duration")
@patch("include.reports.report_generator.get_skipped_runs")
@patch("include.reports.report_generator.get_failed_runs")
@patch("include.reports.report_generator.get_successful_runs")
@patch("include.reports.report_generator.get_total_runs")
def test_generate_pipeline_report_success(mock_get_total_runs,mock_get_successful_runs,mock_get_failed_runs,mock_get_skipped_runs,mock_get_average_duration,mock_get_total_records_received,mock_get_total_records_loaded,mock_total_duplicates_skipped,mock_get_success_rate,mock_get_failure_rate):
    mock_get_total_runs.return_value = 10
    mock_get_successful_runs.return_value = 8 
    mock_get_failed_runs.return_value = 1
    mock_get_skipped_runs.return_value = 1
    mock_get_average_duration.return_value = 45.5
    mock_get_total_records_received.return_value = 170
    mock_get_total_records_loaded.return_value = 168
    mock_total_duplicates_skipped.return_value = 2
    mock_get_success_rate.return_value = 80.0
    mock_get_failure_rate.return_value = 10.0

    report = generate_pipeline_report()

    assert report["pipeline_name"] == PIPELINE_NAME
    assert report["generated_on"] is not None
    assert report["total_runs"] == 10
    assert report["successful_runs"] == 8
    assert report["failed_runs"] == 1
    assert report["skipped_runs"] == 1
    assert report["average_duration"] == 45.5
    assert report["total_records_received"] == 170
    assert report["total_records_loaded"] == 168
    assert report["duplicates_skipped"] == 2
    assert report["success_rate"] == 80.0
    assert report["failure_rate"] == 10.0

    mock_get_total_runs.assert_called_once()
    mock_get_successful_runs.assert_called_once()
    mock_get_failed_runs.assert_called_once()
    mock_get_skipped_runs.assert_called_once()
    mock_get_average_duration.assert_called_once()
    mock_get_total_records_received.assert_called_once()
    mock_get_total_records_loaded.assert_called_once()
    mock_total_duplicates_skipped.assert_called_once()
    mock_get_success_rate.assert_called_once()
    mock_get_failure_rate.assert_called_once()

@patch("include.reports.report_generator.save_pipeline_report")
@patch("include.reports.report_generator.generate_pipeline_report")

def test_print_pipeline_report_scheduled_run(mock_generate_pipeline_report, mock_save_pipeline_report):
    mock_generate_pipeline_report.return_value ={
        "pipeline_name": "CurrencyETLPipeline",
        "generated_on": "2026-10-25",
        "total_runs": 10,
        "successful_runs": 8,
        "failed_runs": 1,
        "skipped_runs": 1,
        "average_duration": 45.5,
        "total_records_received": 170,
        "total_records_loaded": 168,
        "duplicates_skipped": 2,
        "success_rate": 80.0,
        "failure_rate": 10.0
    }

    print_pipeline_report("scheduled__2026-10-25", "2026-10-25")

    mock_generate_pipeline_report.assert_called_once()
    mock_save_pipeline_report.assert_called_once_with(
        mock_generate_pipeline_report.return_value,
        "2026-10-25"
    )
@patch("include.reports.report_generator.save_pipeline_report")
@patch("include.reports.report_generator.generate_pipeline_report")
def test_print_pipeline_report_manual_run(mock_generate_pipeline_report,mock_save_pipeline_report):
    mock_generate_pipeline_report.return_value ={
        "pipeline_name": "CurrencyETLPipeline",
        "generated_on": "2026-10-25",
        "total_runs": 10,
        "successful_runs": 8,
        "failed_runs": 1,
        "skipped_runs": 1,
        "average_duration": 45.5,
        "total_records_received": 170,
        "total_records_loaded": 168,
        "duplicates_skipped": 2,
        "success_rate": 80.0,
        "failure_rate": 10.0
    }

    print_pipeline_report("manual__2026-10-25", "2026-10-25")

    mock_generate_pipeline_report.assert_called_once()
    mock_save_pipeline_report.assert_not_called()


def test_save_pipeline_report_success(tmp_path, monkeypatch):

    # Arrange
    report = {
        "pipeline_name": "CurrencyETLPipeline",
        "generated_on": "2026-10-25 10:00:00 UTC",
        "total_runs": 10,
        "successful_runs": 8,
        "failed_runs": 1,
        "skipped_runs": 1,
        "average_duration": 45.5,
        "total_records_received": 170,
        "total_records_loaded": 168,
        "duplicates_skipped": 2,
        "success_rate": 80.0,
        "failure_rate": 10.0
    }


    # Replace Path inside report_generator temporarily
    def fake_path(path):
        return tmp_path / Path(path).name


    monkeypatch.setattr(
        "include.reports.report_generator.Path",
        fake_path
    )


    # Act
    save_pipeline_report(
        report,
        "2026-10-25"
    )


    # Assert
    file_path = tmp_path / "2026-10-25.txt"

    assert file_path.exists()


    with open(file_path, "r") as f:
        content = f.read()


    assert "CurrencyETLPipeline" in content
    assert "Generated On" in content
    assert "Total Runs" in content
    assert "Successful Runs" in content
    assert "Failed Runs" in content
    assert "Skipped Runs" in content
    assert "Average Duration" in content
    assert "Total Records Received" in content
    assert "Total Records Loaded" in content
    assert "Duplicates Skipped" in content
    assert "Success Rate" in content
    assert "Failure Rate" in content
    
