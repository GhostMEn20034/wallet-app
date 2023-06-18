import fastapi
import datetime
from typing import List
from client import db, client
from schemes.users import PyObjectId
from services.currency_utils import get_conversion_rates, get_converted_amount


async def increment_the_balance(account_id: PyObjectId, amount: float):
    account = await db["accounts"].update_one({"_id": account_id},
                                              {"$inc": {"balance": round(amount, 2)}})
    return account.modified_count


async def decrement_the_balance(account_id: PyObjectId, amount: float):
    account = await db["accounts"].update_one({"_id": account_id},
                                              {"$inc": {"balance": round(-amount, 2)}})
    return account.modified_count


async def funds_transfer(sender, receiver, record_data: dict):
    """
    :param sender - account where funds will be withdrawn
    :param receiver - account where funds will be transferred
    :param record_data - dictionary storing information that it used
    to form information about record


    Function transfers fund from one account to another account
    """
    is_the_same_currency = bool(sender.get("currency") == receiver.get("currency"))

    withdrawal_amount = record_data.get("amount")
    if not is_the_same_currency:
        """
        Converts the withdrawal amount into the currency of receiver 
        if there's no conversion_rate key in record_data
        else it converts amount at the conversion_rate
        """
        withdrawal_amount = await get_converted_amount(record_data.get("amount"), sender.get("currency"),
                                                       receiver.get("currency")) if not record_data.get(
            "conversion_rate") else record_data.get("amount") * record_data.get("conversion_rate")

    async with await client.start_session() as s:
        async with s.start_transaction():
            decrease_senders_balance = await db["accounts"].update_one({"_id": sender.get("_id")},
                                                                       {"$inc": {
                                                                           "balance": round(-record_data.get("amount"),
                                                                                            2)}},
                                                                       session=s)
            increase_receivers_balance = await db["accounts"].update_one({"_id": receiver.get("_id")},
                                                                         {"$inc": {
                                                                             "balance": withdrawal_amount}},
                                                                         session=s)

            common_fields = {"sender": sender.get("_id"),
                             "receiver": record_data.get("receiver"),
                             "category": "Transfer, withdraw", "created_at": datetime.datetime.utcnow()}

            sender_data = {"account_id": sender.get("_id"), "amount": record_data.get("amount"), **common_fields,
                           "record_type": "Transfer withdrawal"}

            receiver_data = {"account_id": record_data.get("receiver"), "amount": withdrawal_amount, **common_fields,
                             "record_type": "Transfer income"}

            receiver_record = await db["records"].insert_one(receiver_data, session=s)
            sender_record = await db["records"].insert_one(sender_data, session=s)

    return fastapi.responses.JSONResponse(
        status_code=fastapi.status.HTTP_200_OK,
        content={
            "status": "The funds have been transferred successfully"
        })


async def records_by_date(account_ids: List, primary_currency: str, filters: dict, reverse: bool):
    conversion_rates = await get_conversion_rates(primary_currency)

    pipeline = [
        # Sort the records by date in descending order
        {"$sort": {"created_at": -1 if reverse else 1}},
        {
            "$match": {
                "account_id": {"$in": account_ids}, **filters
            }
        },
        # Join the records collection with the accounts collection
        {"$lookup": {
            "from": "accounts",
            "localField": "account_id",
            "foreignField": "_id",
            "as": "account"
        }},
        # Unwind the account array
        {"$unwind": "$account"},
        # Project only the account_name field and rename the currency and color fields
        {"$project": {
            "_id": 1,
            "account_id": 1,
            "amount": 1,
            "category": 1,
            "record_type": 1,
            "created_at": 1,
            "account_name": "$account.name",
            "account_currency": "$account.currency",
            "account_color": "$account.color",
            "converted_currency": {
                "$round": [
                    {"$multiply": ["$amount", {"$divide": [1,
                                                           {"$arrayElemAt": [list(conversion_rates.values()), {
                                                               "$indexOfArray": [list(conversion_rates.keys()),
                                                                                 "$account.currency"]}]}]}]}, 2]
            }
        }},
        # Group the records by date
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
            "records": {"$push": "$$ROOT"},
            # Use $cond to separate amounts based on the record_type
            # Calculate the sum of income and transfer income
            "income_amount": {
                "$sum": {
                    "$cond": [
                        {
                            "$in": [
                                "$record_type",
                                ["Income"]
                            ]
                        },
                        "$converted_currency",
                        0
                    ]
                }
            },
            # Calculate the sum of expense and transfer withdrawal
            "expense_amount": {
                "$sum": {
                    "$cond": [
                        {
                            "$in": [
                                "$record_type",
                                ["Expense"]
                            ]
                        },
                        "$converted_currency",
                        0
                    ]
                }
            }
        }},
        # Project the fields to match the desired format
        {"$project": {
            "_id": 0,
            "date": "$_id",
            "records": 1,
            "total_amount": {
                "$round": [
                    {
                        "$subtract": [
                            "$income_amount",
                            "$expense_amount"
                        ]
                    },
                    2
                ]
            }
        }},
        {
            "$sort": {
                "date": -1 if reverse else 1,
            }
        },
    ]

    aggregated_records = await db["records"].aggregate(pipeline).to_list(100)
    return aggregated_records


async def create_record(record_data: dict, account: dict, user_id):
    record_type = record_data.get("record_type")
    match record_type:
        case "Income":
            increase_the_balance = await increment_the_balance(account.get("_id"), record_data.get("amount"))
            if increase_the_balance == 1:
                record_data["created_at"] = datetime.datetime.utcnow()
                created_record = await db["records"].insert_one(record_data)
                return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK,
                                                      content={"status": "The income was credited to your account"})
        case "Expense":
            decrease_the_balance = await decrement_the_balance(account.get("_id"), record_data.get("amount"))
            if decrease_the_balance == 1:
                record_data["created_at"] = datetime.datetime.utcnow()
                created_record = await db["records"].insert_one(record_data)
                return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content={
                    "status": "Funds have been successfully withdrawn from your account"})
        case "Transfer":
            receiver = await db["accounts"].find_one(
                {"_id": record_data.get("receiver"), "user_id": user_id})
            if receiver:
                return await funds_transfer(account, receiver, record_data)

            return fastapi.responses.JSONResponse(status_code=400, content={"Status": "Invalid receiver"})

        case _:
            return fastapi.responses.JSONResponse(status_code=400, content={"Status": "Something went wrong"})


async def records_by_amount(account_ids: List, primary_currency: str, filters: dict, reverse: bool):
    conversion_rates = await get_conversion_rates(primary_currency)

    pipeline = [
        {
            "$match": {
                "account_id": {"$in": account_ids}, **filters
            }
        },
        {
            "$lookup": {
                "from": "accounts",
                "localField": "account_id",
                "foreignField": "_id",
                "as": "account"
            }
        },
        {
            "$unwind": "$account"
        },
        {"$addFields": {
            "account_name": "$account.name",
            "account_currency": "$account.currency",
            "account_color": "$account.color",
            "converted_currency": {
                "$round": [
                    {"$multiply": ["$amount", {"$divide": [1,
                                                           {"$arrayElemAt": [list(conversion_rates.values()), {
                                                               "$indexOfArray": [list(conversion_rates.keys()),
                                                                                 "$account.currency"]}]}]}]}, 2]
            },
        }},
        {"$sort": {"converted_currency": -1 if reverse else 1}},
        {"$group": {
            "_id": None,
            "records": {"$push": "$$ROOT"},
            "income_amount": {
                "$sum": {
                    "$cond": [
                        {
                            "$in": [
                                "$record_type",
                                ["Income"]
                            ]
                        },
                        "$converted_currency",
                        0
                    ]
                }
            },
            # Calculate the sum of expense and transfer withdrawal
            "expense_amount": {
                "$sum": {
                    "$cond": [
                        {
                            "$in": [
                                "$record_type",
                                ["Expense"]
                            ]
                        },
                        "$converted_currency",
                        0
                    ]
                }
            }
        }},
        {"$addFields": {
            "total": {
                "$subtract": [
                    "$income_amount",
                    "$expense_amount"
                ]
            },
        }}
    ]

    records = await db["records"].aggregate(pipeline).to_list(100)
    return records


def create_filter_dict(properties: dict):
    start_date = properties.get("start_date", datetime.datetime.utcnow() - datetime.timedelta(days=30))
    end_date = properties.get("end_date", datetime.datetime.utcnow())

    filter_dict = {
        key: value for key, value in [
            ("category", {"$in": properties.get("categories")} if properties.get("categories") else None),
            ("amount", {"$gte": properties.get("min_amount"),
                        "$lte": properties.get("max_amount")} if properties.get(
                "min_amount") and properties.get("max_amount") else None),

            ("record_type", {"$in": properties.get("record_types") if properties.get("record_types") else None}),
            ("created_at", {"$gte": start_date, "$lte": end_date} if start_date and end_date else None)

        ] if value is not None}

    return filter_dict
