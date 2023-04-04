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
            decrease_senders_balance = await db["accounts"].update_one({"_id": sender}, {"$inc": {"balance": round(-amount, 2)}}, session=s)
            increase_receivers_balance = await db["accounts"].update_one({"_id": receiver}, {"$inc": {"balance": round(amount, 2)}}, session=s)

            if 1 in {decrease_senders_balance.modified_count, increase_receivers_balance.modified_count}:
                return 1
