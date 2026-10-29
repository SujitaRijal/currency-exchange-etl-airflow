from unittest.mock import patch

from include.callbacks.email_callback import email_failure_callback


@patch("include.callbacks.email_callback.smtp_callback")
def test_email_failure_callback_success(mock_smpt_callback):
    context = {}
    email_failure_callback(context)
    mock_smpt_callback.assert_called_once_with(context)
