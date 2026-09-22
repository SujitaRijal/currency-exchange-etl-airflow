import requests

BASE_URL="https://open.er-api.com/v6/latest/USD"


def fetch_exchange_rate():
    """
    Fetch latest exchange rates from public API """

    response=requests.get(BASE_URL,timeout=30) #waits max of 30 sec,if  there's no response,exception is raised and tasks fails
    response.raise_for_status() #error handling ,,If the HTTP status code isn't successful (2xx), stop immediately and raise an exception.
    return response.json() #api sends json text,response.json convert it into python obj ,dictionary which the dag receives