import logging

import requests
from airflow.models import Variable

logger = logging.getLogger(__name__)


def fetch_exchange_rate():
    """
    Fetch latest exchange rates from public API
    """
    api_base_url = Variable.get("API_BASE_URL")
    base_currency = Variable.get("BASE_CURRENCY")

    url = f"{api_base_url}/{base_currency}"

    logger.info(f"Fetching exchange rates from :{url}")
    # Timeout prevents the task from waiting indefinitely.
    # If the API does not respond within 30 seconds,
    # requests raises an exception and the task fails.
    response = requests.get(url, timeout=30)
    # error handling ,,If the HTTP status code isn't successful (2xx),
    # stop immediately and raise an exception.
    response.raise_for_status()

    # The API returns JSON text.
    # response.json() converts it into a Python dictionary
    # that downstream DAG tasks can process.
    return response.json()
