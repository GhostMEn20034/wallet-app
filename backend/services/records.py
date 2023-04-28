from client import db, client
from schemes.users import PyObjectId
from typing import List


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

            if 1 in {decrease_senders_balance.modified_count, increase_receivers_balance.modified_count}:
                return 1


async def aggregate_records(account_ids: List):
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
                "account_id": {"$in": account_ids}
            }
        },
        # Add a new field called date that only contains the year-month-day part of created_at
        {
            "$addFields": {
                "date": {
                    "$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}
                }
            }
        },
        # Group by date and push the records into an array called records
        {
            "$group": {
                "_id": "$date",
                "records": {"$push": "$$ROOT"}
            }
        },
        # Project only the fields that you need
        {
            "$project": {
                "_id": 0,
                "date": "$_id",
                "records": {
                    # Use $map to add account_name for each record
                    "$map": {
                        "input": "$records",
                        "as": "record",
                        "in": {
                            "_id": "$$record._id",
                            "account_id": "$$record.account_id",
                            "receiver": "$$record.receiver",
                            "amount": "$$record.amount",
                            "category": "$$record.category",
                            "record_type": "$$record.record_type",
                            "created_at": "$$record.created_at",
                            # Add account_name from account document
                            "account_name": "$$record.account.name"
                        }
                    }
                }
            }
        },
        {
            "$sort": {
                "date": -1
            }
        },
    ]

    aggregated_records = await db["records"].aggregate(pipeline).to_list(500)
    return aggregated_records
