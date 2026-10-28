from unittest.mock import patch

from include.callbacks.pipeline_callback import pipeline_failure_callback


@patch("include.callbacks.pipeline_callback.email_failure_callback")
@patch("include.callbacks.pipeline_callback.audit_failure_callback")
def test_pipeline_failure_callback(
    mock_audit_failure_callback, mock_email_failure_callback
):
    context = {}

    pipeline_failure_callback(context)

    mock_audit_failure_callback.assert_called_once_with(context)
    mock_email_failure_callback.assert_called_once_with(context)


@patch("include.callbacks.pipeline_callback.email_failure_callback")
@patch("include.callbacks.pipeline_callback.audit_failure_callback")
def test_pipeline_failure_callback_audit_failure(
    mock_audit_failure_callback, mock_email_failure_callback
):
    context = {}
    mock_audit_failure_callback.side_effect = Exception("Audit failed")
    pipeline_failure_callback(context)
    mock_audit_failure_callback.assert_called_once_with(context)
    mock_email_failure_callback.assert_called_once_with(context)


@patch("include.callbacks.pipeline_callback.email_failure_callback")
@patch("include.callbacks.pipeline_callback.audit_failure_callback")
def test_pipeline_failure_callback_email_failure(
    mock_audit_failure_callback, mock_email_failure_callback
):
    context = {}
    mock_email_failure_callback.side_effect = Exception("Email failed")
    pipeline_failure_callback(context)
    mock_audit_failure_callback.assert_called_once_with(context)
    mock_email_failure_callback.assert_called_once_with(context)
