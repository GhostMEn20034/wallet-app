import aiohttp
from settings import EXCHANGE_RATE_API_KEY
import httpx


async def get_conversion_rates(primary_currency="USD"):
    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_RATE_API_KEY}/latest/{primary_currency}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        result = response.json()
        rates = result.get("conversion_rates")
        return rates


async def get_converted_amount(amount, currency_from, currency_to):
    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_RATE_API_KEY}/pair/{currency_from}/{currency_to}/{amount}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        print(response)
        result = await response.json()
        converted_amount = result.get("conversion_result")
        return round(converted_amount, 2)
