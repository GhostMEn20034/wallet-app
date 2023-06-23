import aiohttp
from settings import EXCHANGE_RATE_API_KEY


async def get_conversion_rates(primary_currency="USD"):
    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_RATE_API_KEY}/latest/{primary_currency}"
    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.get(url) as response:
            result = await response.json()
            rates = result.get("conversion_rates")
            return rates


async def get_converted_amount(amount, currency_from, currency_to):
    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_RATE_API_KEY}/pair/{currency_from}/{currency_to}/{amount}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            result = await response.json()
            converted_amount = result.get("conversion_result")
            return round(converted_amount, 2)
