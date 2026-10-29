import json

import pytest

from include.quality.quality_check import check_data_quality


def create_sample_data(count=100):
    data = []
    for i in range(count):
        data.append(
            {"base_currency": "USD", "target_currency": f"C{i}", "exchange_rate": i + 1}
        )
    return data


def test_check_data_quality_success(tmp_path):
    # Arrange
    data = create_sample_data(100)
    file_path = tmp_path / "processed.json"
    with open(file_path, "w") as f:
        json.dump(data, f)
    # Act
    check_data_quality(file_path)
    # Assert
    assert True


def test_check_data_quality_empty_dataset(tmp_path):
    # Arrange
    file_path = tmp_path / "processed.json"
    with open(file_path, "w") as f:
        json.dump([], f)

    with pytest.raises(ValueError, match="Processed dataset is empty."):
        check_data_quality(file_path)


def test_check_data_quality_duplicate_currency_pair(tmp_path):
    data = create_sample_data(100)
    # Make record 1 a duplicate of record 0
    data[1]["base_currency"] = "USD"
    data[1]["target_currency"] = "C0"

    file_path = tmp_path / "processed.json"
    with open(file_path, "w") as f:
        json.dump(data, f)
    with pytest.raises(ValueError, match="Duplicate currency pair"):
        check_data_quality(file_path)


def test_check_data_quality_invalid_exchange_rate(tmp_path):
    data = create_sample_data(100)
    data[0]["exchange_rate"] = 0
    file_path = tmp_path / "processed.json"
    with open(file_path, "w") as f:
        json.dump(data, f)
    with pytest.raises(ValueError, match="Invalid exchange rate"):
        check_data_quality(file_path)


def test_check_data_quality_insufficient_records(tmp_path):
    data = create_sample_data(50)

    file_path = tmp_path / "processed.json"
    with open(file_path, "w") as f:
        json.dump(data, f)

    with pytest.raises(ValueError, match="Insufficient currency records"):
        check_data_quality(file_path)
