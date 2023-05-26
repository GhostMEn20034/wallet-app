from client import db
from services.get_conversion_rates import get_conversion_rates
import bson.json_util


def convert_to_primary_currency(account, rates, primary_currency):
    # Get the currency rate for the primary currency
    primary_rate = rates[primary_currency]
    # Get the account balance and currency
    balance = account["balance"]
    currency = account["currency"]
    # Get the currency rate for the account currency
    rate = rates[currency]
    # Convert the balance to primary currency by multiplying by the ratio of rates
    converted_balance = balance * (rate / primary_rate)
    # Add a new field to store the converted balance
    account["converted_balance"] = converted_balance
    return account


async def get_accounts(user_id, primary_currency, reverse: bool, sort_by="name"):
    conversion_rates = get_conversion_rates(primary_currency) if sort_by == "balance" else {}
    # conversion_rates = {"USD": 1, "UAH": 36.8}
    pipeline = [
        {
            "$match": {
                "user.id": user_id
            }
        },
        {
            "$project": {
                "name": 1,
                "balance": {"$round": ["$balance", 2]},
                "bank_account": 1,
                "currency": 1,
                "color": 1,
                "converted_balance": {
                    "$round": [
                        {"$multiply": ["$balance", {"$divide": [conversion_rates[primary_currency],
                                                                {"$arrayElemAt": [list(conversion_rates.values()), {
                                                                    "$indexOfArray": [list(conversion_rates.keys()),
                                                                                      "$currency"]}]}]}]}, 2]
                } if sort_by == "balance" else None
            }
        },
        {
            "$sort": {"converted_balance": -1 if reverse else 1} if sort_by == "balance" else {
                sort_by: -1 if reverse else 1}
        }
    ]

    accounts = await db["accounts"].aggregate(pipeline).to_list(50)
    return accounts
