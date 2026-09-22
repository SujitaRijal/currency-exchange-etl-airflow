import json
import logging
logger = logging.getLogger(__name__)  #logging-logging module, getLogger()-creates or retrieves a logger,__name__-gives the name of current python module


def validate_exchange_rates(raw_file):
    """
    Validates the raw exchange rate API response.

    Raises:
        ValueError: If the API response is invalid.
    """

    # Read raw JSON
    with open(raw_file) as f:
        data = json.load(f)

    # -----------------------------
    # Validate base currency
    # -----------------------------
    if "base_code" not in data:
        raise ValueError("Missing base_code.")

    if not isinstance(data["base_code"], str):
        raise ValueError("base_code must be a string.")

    if not data["base_code"].strip():
        raise ValueError("base_code cannot be empty.")

    # -----------------------------
    # Validate source timestamp
    # -----------------------------
    if "time_last_update_utc" not in data:
        raise ValueError("Missing time_last_update_utc.")

    if not isinstance(data["time_last_update_utc"], str):
        raise ValueError("time_last_update_utc must be a string.")

    if not data["time_last_update_utc"].strip():
        raise ValueError("time_last_update_utc cannot be empty.")

    # -----------------------------
    # Validate exchange rates
    # -----------------------------
    if "rates" not in data:
        raise ValueError("Missing rates.")

    if not isinstance(data["rates"], dict):
        raise ValueError("Rates must be a dictionary.")

    if not data["rates"]:
        raise ValueError("Rates dictionary is empty.")

   # print("Validation successful.")
    logger.info("Validation Successful") 