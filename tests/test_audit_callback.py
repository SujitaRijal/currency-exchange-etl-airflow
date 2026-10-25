from datetime import datetime
from unittest.mock import MagicMock,patch

from include.callbacks.audit_callback import audit_failure_callback

@patch("include.callbacks.audit_callback.update_audit_failure")
def test_audit_failure_callback_success(mock_update_audit_failure):
    context = {
        "dag_run": MagicMock(),
        "task_instance": MagicMock(),
        "exception" : Exception("API failed")
    }

    context["dag_run"].run_id ="scheduled__2025-10-25"
    context["task_instance"].task_id = "extract_exchange_rate"

    audit_failure_callback(context)

    mock_update_audit_failure.assert_called_once()
    args = mock_update_audit_failure.call_args.kwargs

    assert args["run_id"] == "scheduled__2025-10-25"
    assert args["failed_task"] == "extract_exchange_rate"
    assert args["error_message"] == "API failed"

    assert isinstance(args["end_time"],datetime)
