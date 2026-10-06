from unittest.mock import patch, Mock
from include.extract.api_client import fetch_exchange_rate
import pytest
import requests
import json

#mock-creates fake obj,always records what happens
#  patch-temporarily replace the actual function
#Assertions only inspect the recorded history.They do not create the history.


@pytest.fixture
def fake_response():
    response = Mock()
    response.raise_for_status.return_value = None
    return response

API_BASE_URL = "https://open.er-api.com/v6/latest"
BASE_CURRENCY = "USD"
EXPECTED_URL = f"{API_BASE_URL}/{BASE_CURRENCY}"

@pytest.fixture
def mock_variables():
    with patch("include.extract.api_client.Variable.get") as mock_variable:
        mock_variable.side_effect = [
            API_BASE_URL,
            BASE_CURRENCY,
        ]
        yield mock_variable


@patch("include.extract.api_client.requests.get")
#patch -temporarily replace request.get inside include.extract.api_client 
#mock_get-because of @patch pytest automatically give the mocked version of request.get() so inside test,request.get()->mock_get
def test_fetch_exchange_rate_success(mock_get , fake_response, mock_variables):
    #Does API work normally?
    #Now we can teach it to behave like a real response:
    expected_data = {
         "base_code" : "USD",
         "rates" : {
             "NPR":137.2}

    }
    #Arrange-prepare the object
    fake_response.json.return_value = expected_data
    mock_get.return_value = fake_response

    #Act-call the function
    result = fetch_exchange_rate()

    #check result= "Did my function return the correct output?"
    #Assert-Verify
    assert result == expected_data
    
    #behaviour-"Did my function behave correctly?"-Did I actually call the API?-mock_get.assert_called_once()-Was requests.get() called exactly once?
    mock_get.assert_called_once_with(EXPECTED_URL, timeout=30)
    #checked two things ,called exactly once and called the correct url
    fake_response.raise_for_status.assert_called_once()
    fake_response.json.assert_called_once()


@patch("include.extract.api_client.requests.get")
def test_fetch_exchange_rate_timeout(mock_get, mock_variables):
    # What if internet is slow?
    mock_get.side_effect = requests.Timeout ("Request Timed Out")
    with pytest.raises(requests.Timeout):
        fetch_exchange_rate()

    mock_get.assert_called_once_with(EXPECTED_URL, timeout=30)


@patch("include.extract.api_client.requests.get")
def test_fetch_exchange_rate_http_error(mock_get,fake_response,mock_variables):
   #What if server returns 404/500?
    fake_response.raise_for_status.side_effect = requests.HTTPError("HTTP Response error")

    mock_get.return_value = fake_response

    with pytest.raises(requests.HTTPError):
        fetch_exchange_rate()
    
    mock_get.assert_called_once_with(EXPECTED_URL, timeout=30)
    fake_response.raise_for_status.assert_called_once()

@patch("include.extract.api_client.requests.get")
def test_fetch_exchange_rate_invalid_json(mock_get,fake_response, mock_variables):
    #What if API sends bad JSON?
    fake_response.json.side_effect = json.JSONDecodeError("Invalid Json", "", 0)
    mock_get.return_value = fake_response

    with pytest.raises(json.JSONDecodeError):
        fetch_exchange_rate()

    mock_get.assert_called_once_with(EXPECTED_URL, timeout=30)
    fake_response.raise_for_status.assert_called_once()
    fake_response.json.assert_called_once()

@patch("include.extract.api_client.requests.get")
def test_fetch_exchange_rate_connection_error(mock_get,mock_variables):
     #What if internet is disconnected?
    mock_get.side_effect = requests.ConnectionError("Unable to connect")

    with pytest.raises(requests.ConnectionError):
        fetch_exchange_rate()

    mock_get.assert_called_once_with(EXPECTED_URL, timeout=30)

@patch("include.extract.api_client.requests.get")
def test_fetch_exchange_rate_too_many_redirects(mock_get,mock_variables):

    #What if server redirects forever?
    mock_get.side_effect = requests.TooManyRedirects("Too many redirects")

    with pytest.raises(requests.TooManyRedirects):
        fetch_exchange_rate()

    mock_get.assert_called_once_with(EXPECTED_URL, timeout=30)

@patch("include.extract.api_client.requests.get")
def test_fetch_exchange_rate_request_exception(mock_get,mock_variables):
   
    #Generic request failure.
    mock_get.side_effect = requests.RequestException("Request Failed")

    with pytest.raises(requests.RequestException):
        fetch_exchange_rate()

    mock_get.assert_called_once_with(EXPECTED_URL, timeout=30)























#Why do we patch include.extract.api_client.requests.get instead of requests.get? #patch=temporary replacing smthg #mock-smthg that behaves like that obj-can teach it how to behave
#Because fetch_exchange_rate() looks up requests.get inside include.extract.api_client.
#  Mocking must replace the object where it is used, not where it was originally defined.