#coordinates all the failure callbacks

import logging
from include.callbacks.audit_callback import audit_failure_callback
from include.callbacks.email_callback import email_failure_callback

logger=logging.getLogger(__name__)

def pipeline_failure_callback(context):
    """
    Executes all failure handlers when a task fails.
    """

    #we dont want one failure callback stop the another so using different try-block
    try:
        audit_failure_callback(context)
    except Exception as e:
        logger.exception(f"Audit callback failed :{e}")

    try:
        email_failure_callback(context)
    except Exception as e:
        logger.exception(f"Email callback failed :{e}")