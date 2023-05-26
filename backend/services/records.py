import fastapi
import datetime
from typing import List
from client import db, client
from schemes.users import PyObjectId


async def increment_the_balance(account_id: PyObjectId, amount: float):
    account = await db["accounts"].update_one({"_id": account_id},
                                              {"$inc": {"balance": round(amount, 2)}})
    return account.modified_count


async def decrement_the_balance(account_id: PyObjectId, amount: float):
    account = await db["accounts"].update_one({"_id": account_id},
                                              {"$inc": {"balance": round(-amount, 2)}})
    return account.modified_count


async def funds_transfer(sender: PyObjectId, receiver: PyObjectId, amount: float):
    async with await client.start_session() as s:
        async with s.start_transaction():
            decrease_senders_balance = await db["accounts"].update_one({"_id": sender},
                                                                       {"$inc": {"balance": round(-amount, 2)}},
                                                                       session=s)
            increase_receivers_balance = await db["accounts"].update_one({"_id": receiver},
                                                                         {"$inc": {"balance": round(amount, 2)}},
                                                                         session=s)

            if decrease_senders_balance.modified_count == 1 and increase_receivers_balance.modified_count == 1:
                return 1


async def records_by_date(account_ids: List, filters: dict, reverse: bool):
    pipeline = [
        # Sort the records by date in descending order
        {"$sort": {"created_at": -1 if reverse else 1}},
        # Join the records collection with the accounts collection
        {"$lookup": {
            "from": "accounts",
            "localField": "account_id",
            "foreignField": "_id",
            "as": "account"
        }},
        # Unwind the account array
        {"$unwind": "$account"},
        {
            "$match": {
                "account_id": {"$in": account_ids}, **filters
            }
        },
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
            "account_color": "$account.color"
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
                        "$amount",
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
                        "$amount",
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
                del record_data["receiver"]
                record_data["created_at"] = datetime.datetime.utcnow()
                created_record = await db["records"].insert_one(record_data)
                return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK,
                                                      content={"status": "The income was credited to your account"})
        case "Expense":
            decrease_the_balance = await decrement_the_balance(account.get("_id"), record_data.get("amount"))
            if decrease_the_balance == 1:
                del record_data["receiver"]
                record_data["created_at"] = datetime.datetime.utcnow()
                created_record = await db["records"].insert_one(record_data)
                return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content={
                    "status": "Funds have been successfully withdrawn from your account"})
        case "Transfer":
            receiver = await db["accounts"].find_one(
                {"_id": record_data.get("receiver"), "user.id": user_id})
            if receiver:
                transfer = await funds_transfer(account.get("_id"), record_data.get("receiver"),
                                                record_data.get("amount"))
                if transfer == 1:
                    common_fields = {"sender": account.get("_id"),
                                     "receiver": record_data.get("receiver"), "amount": record_data.get("amount"),
                                     "category": "Transfer, withdraw", "created_at": datetime.datetime.utcnow()}

                    sender_data = {"account_id": account.get("_id"), **common_fields,
                                   "record_type": "Transfer withdrawal"}

                    receiver_data = {"account_id": record_data.get("receiver"), **common_fields,
                                     "record_type": "Transfer income"}

                    receiver_record = await db["records"].insert_one(receiver_data)
                    sender_record = await db["records"].insert_one(sender_data)
                    return fastapi.responses.JSONResponse(
                        status_code=fastapi.status.HTTP_200_OK,
                        content={
                            "status": "The funds have been transferred successfully"
                        })

        case _:
            return fastapi.responses.JSONResponse(status_code=400, content={"Status": "Something went wrong"})


async def records_by_amount(account_ids: List, filters: dict, reverse: bool):
    pipeline = [
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
        {
            "$match": {
                "account_id": {"$in": account_ids}, **filters
            }
        },
        {"$addFields": {"account_name": "$account.name", "account_currency": "$account.currency",
                        "account_color": "$account.color"}},
        {"$sort": {"amount": -1 if reverse else 1}},
        {"$limit": 100}
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
            ("created_at", {"$gte": start_date, "$lte": end_date} if properties.get("start_date") and properties.get(
                "end_date") else None)

        ] if value is not None}

    return filter_dict
