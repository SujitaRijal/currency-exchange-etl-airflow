import json
import pytest
#Pytest is used to automatically verify that your code behaves correctly under both normal and abnormal conditions.

from include.validate.validator import validate_exchange_rates

TEST_FILE ="sample.json"
#Every test starts from a valid payload and changes only one thing.
VALID_DATA = {
    "base_code": "USD",
    "time_last_update_utc": "Thu, 01 Oct 2026 00:00:01 +0000",
    "rates": {
        "NPR": 137.2,
        "EUR": 0.85,
    },
}

TEST_CASES = [
    (
    {
        "time_last_update_utc": VALID_DATA["time_last_update_utc"],
        "rates": VALID_DATA["rates"],
    },
    "Missing base_code.",
    ),
    (
    {
        **VALID_DATA,
        "base_code": 123,
    },
    "base_code must be a string.",
    ),
    (
    {
        **VALID_DATA,
        "base_code": "",
    },
    "base_code cannot be empty.",
    ),
    (
    {
        "base_code": VALID_DATA["base_code"],
        "rates": VALID_DATA["rates"],
    },
    "Missing time_last_update_utc.",
    ),
    (
    {
        **VALID_DATA,
        "time_last_update_utc": 123,
    },
    "time_last_update_utc must be a string.",
    ),
    (
    {
        **VALID_DATA,
        "time_last_update_utc": "",
    },
    "time_last_update_utc cannot be empty.",
    ),
    (
    {
        "base_code": VALID_DATA["base_code"],
        "time_last_update_utc": VALID_DATA["time_last_update_utc"],
    },
    "Missing rates.",
    ),
    (
    {
        **VALID_DATA,
        "rates": [],
    },
    "Rates must be a dictionary.",
    ),
    (
    {
        **VALID_DATA,
        "rates": {},
    },
    "Rates dictionary is empty.",
),

]

#fixture-reusable test setup with flexible input
@pytest.fixture
def create_json_file(tmp_path):
    def _create_file(data):
        file = tmp_path / TEST_FILE
        with open(file, "w") as f:
            json.dump(data, f)
        return file
    return _create_file

#everytime you run this test give me data and expected error
@pytest.mark.parametrize(
    "data, expected_error",
    TEST_CASES,
    ids=[
        "missing_base_code",
        "base_code_not_string",
        "empty_base_code",
        "missing_timestamp",
        "timestamp_not_string",
        "empty_timestamp",
        "missing_rates",
        "rates_not_dictionary",
        "empty_rates",
    ],
)



def test_invalid_exchange_rate_data(create_json_file, data, expected_error):

    file = create_json_file(data)
    
    with pytest.raises(ValueError, match=expected_error):
        validate_exchange_rates(file)



def test_valid_exchange_rate_file(create_json_file):

    file = create_json_file(VALID_DATA)

    validate_exchange_rates(file)