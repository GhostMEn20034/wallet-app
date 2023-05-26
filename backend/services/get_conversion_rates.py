import requests
from settings import EXCHANGE_RATE_API_KEY


def get_conversion_rates(primary_currency="USD"):
    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_RATE_API_KEY}/latest/{primary_currency}"
    r = requests.request("GET", url)
    result = r.json()
    rates = result.get("conversion_rates")
    return rates

