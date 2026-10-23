import json
import pytest

from include.utils.file_utils import write_json

def test_write_json_success(tmp_path):
    data = {
        "base_currency": "USD",
        "target_currency": "EUR",
        "exchange_rate": 0.92
    }
    file_path= tmp_path / "raw" / "exchange.json"

    result = write_json(data,file_path)

    assert result == str(file_path)
    assert file_path.exists()

    with open(file_path, "r") as f:
        saved_data =json.load(f)

    assert saved_data == data

def test_write_json_invalid_data(tmp_path):
    data={
        "currencies":{1,2,3}
    }
    file_path= tmp_path / "invalid.json"

    with pytest.raises(TypeError):
        write_json(data,file_path)