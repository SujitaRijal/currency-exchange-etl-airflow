import requests
from airflow.models import Variable
import logging

logger=logging.getLogger(__name__)

API_BASE_URL = Variable.get("API_BASE_URL")
BASE_CURRENCY=Variable.get("BASE_CURRENCY")

url=f"{API_BASE_URL}/{BASE_CURRENCY}"



def fetch_exchange_rate():
    """
    Fetch latest exchange rates from public API """
    logger.info(f"Fetching exchange rates from :{url}")
    response=requests.get(url,timeout=30) #waits max of 30 sec,if  there's no response,exception is raised and tasks fails
    response.raise_for_status() #error handling ,,If the HTTP status code isn't successful (2xx), stop immediately and raise an exception.
    return response.json() #api sends json text,response.json convert it into python obj ,dictionary which the dag receives