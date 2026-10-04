from unittest.mock import patch, Mock
from include.extract.api_client import( fetch_exchange_rate, API_BASE_URL,BASE_CURRENCY)
#mock-creates fake obj,always records what happens
#  patch-temporarily replace the actual function
#Assertions only inspect the recorded history.They do not create the history.



expected_url = f"{API_BASE_URL}/{BASE_CURRENCY}"
@patch("include.extract.api_client.request.get")
#patch -temporarily replace request.get inside include.extract.api_client 
#mock_get-because of @patch pytest automatically give the mocked version of request.get() so inside test,request.get()->mock_get
def test_fetch_exchange_rate_success(mock_get):
    
    fake_response = Mock()
    #Now we can teach it to behave like a real response:
    fake_response.json.return_value = {
        "base_code" : "USD",
        "rates" : {
            "NPR":137.2}
    }

    fake_response.raise_for_status.return_value = None

    mock_get.return_value = fake_response

    result = fetch_exchange_rate()

    #check result= "Did my function return the correct output?"
    assert result == {
    "base_code": "USD",
    "rates": {
        "NPR": 137.2
    }
    }
    #behaviour-"Did my function behave correctly?"-Did I actually call the API?-mock_get.assert_called_once()-Was requests.get() called exactly once?
    mock_get.assert_called_once_with(expected_url)
    #checked two things ,called exactly once and called the correct url





















#Why do we patch include.extract.api_client.requests.get instead of requests.get? #patch=temporary replacing smthg #mock-smthg that behaves like that obj-can teach it how to behave
#Because fetch_exchange_rate() looks up requests.get inside include.extract.api_client.
#  Mocking must replace the object where it is used, not where it was originally defined.