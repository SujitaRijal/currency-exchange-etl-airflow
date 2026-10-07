import json
import pytest


from include.transform.transform_rates import transform_exchange_rates

BASE_SAMPLE_DATA = {
     "base_code": "USD",
    "time_last_update_utc": "Wed, 07 Oct 2026 00:02:31 +0000",
    "rates": {
        "NPR": 137.2,
        "EUR": 0.91,
        "INR": 86.4,
    },
}

@pytest.fixture
def transform_paths(tmp_path):
    return (
        tmp_path / "test_input.json",
        tmp_path / "test_output.json",
        "2026-10-07"
    )


def test_transform_success(transform_paths):
    input_file, output_file, ds=transform_paths
    #Arrange
    sample_data = BASE_SAMPLE_DATA
    
    with open(input_file,"w") as f:
        json.dump(sample_data,f)

    #Act-what are we testing?
    result=transform_exchange_rates(input_file,output_file,ds)

    #Assert
    ## 1. Did it return the correct path?
    assert result == str(output_file)

    #Was the file created?
    assert output_file.exists()

    # Does the file contain the correct transformed records?
    with open(output_file,"r") as f:
        transformed_data=json.load(f)

    assert len(transformed_data) == 3

    expected_first_record = {
        "load_date" : ds,
        "source_timestamp":BASE_SAMPLE_DATA["time_last_update_utc"],
        "base_currency":"USD",
        "target_currency":"NPR",
        "exchange_rate":137.2,
    }
    assert transformed_data[0] == expected_first_record


def test_transform_none_rate(transform_paths):
    input_file, output_file, ds=transform_paths
    sample_data = {
        **BASE_SAMPLE_DATA,
        "rates": {
             "NPR": 137.2,
            "EUR": None,
            "INR": 86.4,
        },

    }

    with open(input_file,"w") as f:
            json.dump(sample_data,f)

    
    result = transform_exchange_rates(input_file,output_file,ds)

    #Assert
    assert result == str(output_file)
    assert output_file.exists()

    with open(output_file,"r") as f:
         transformed_data=json.load(f)

    #only two valid records should remain
    assert len(transformed_data) == 2

    currencies =[record["target_currency"] for record in transformed_data]
    assert "EUR" not in currencies

def test_transform_invalid_rate_type(transform_paths):
    input_file,output_file,ds=transform_paths
    sample_data = {
        **BASE_SAMPLE_DATA,
        "rates": {
            "NPR": 137.2,
            "EUR": "invalid",
            "INR": 86.4
        },
    }
    with open(input_file, "w") as f:
        json.dump(sample_data, f)


    result = transform_exchange_rates(input_file, output_file, ds)

    # Assert
    assert result == str(output_file)
    assert output_file.exists()

    with open(output_file, "r") as f:
        transformed_data = json.load(f)

    assert len(transformed_data) == 2
    currencies =[record["target_currency"] for record in transformed_data]
    assert "NPR" in currencies
    assert "INR" in currencies
    assert "EUR" not in currencies


def test_transform_invalid_rate_value(transform_paths):
    input_file,output_file,ds=transform_paths
    sample_data = {
        **BASE_SAMPLE_DATA,
        "rates": {
            "NPR": 137.2,
            "EUR": 0,
            "INR": 86.4
        },
    }


    with open(input_file, "w") as f:
        json.dump(sample_data, f)


    #Act
    result = transform_exchange_rates(input_file, output_file, ds)

    # Assert
    assert result == str(output_file)
    assert output_file.exists()

    with open(output_file, "r") as f:
        transformed_data = json.load(f)

    assert len(transformed_data) == 2
    currencies =[record["target_currency"] for record in transformed_data]
    assert "NPR" in currencies
    assert "INR" in currencies
    assert "EUR" not in currencies


def test_transform_no_valid_rates(transform_paths):
    input_file,output_file,ds=transform_paths
     # Arrange
    sample_data = {
        **BASE_SAMPLE_DATA,
        "rates": {
            "NPR": None,
            "EUR": "invalid",
            "INR": 0
        },
    }

    with open(input_file, "w") as f:
        json.dump(sample_data, f)


    #Act+Assert
    with pytest.raises(
        ValueError,
        match="No valid exchange rates found after transformation."
    ):
        transform_exchange_rates(input_file,output_file,ds)

    # Output file should not exist because the function failed
    assert not output_file.exists()

