import json
from include.validate.validator import validate_exchange_rates
import pytest

def test_valid_exchange_rate_file(tmp_path):
    data = {
        "base_code": "USD",
        "time_last_update_utc":"Thu, 01 Oct 2026 00:00:01 +0000",
        "rates": {
             "NPR": 137.2,
             "EUR": 0.85
        }
    }
    file = tmp_path / "sample.json"
    with open(file ,"w") as f:
        json.dump(data,f)

    validate_exchange_rates(file)

def test_missing_base_code(tmp_path):
    data={
        "time_last_update_utc":"Thu, 01 Oct 2026 00:00:01 +0000",
        "rates": {
            "NPR": 137.2        
            }
    }
    file = tmp_path / "sample.json"
    with open(file ,"w") as f:
        json.dump(data,f)

    with pytest.raises(ValueError, match="Missing base_code"):
        validate_exchange_rates(file)

def test_empty_rates_dictionary(tmp_path):

    data = {
        "base_code": "USD",
        "time_last_update_utc": "Thu, 01 Oct 2026 00:00:01 +0000",
        "rates": {}
    }

    file = tmp_path / "sample.json"

    with open(file, "w") as f:
        json.dump(data, f)

    with pytest.raises(ValueError, match="Rates dictionary is empty."):
        validate_exchange_rates(file)