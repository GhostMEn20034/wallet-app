from client import db
from typing import List


async def delete_accounts_and_records(account_ids: List):
    await db["accounts"].delete_many({"_id": {"$in": account_ids}})
    await db["records"].delete_many({"account_id": {"$in": account_ids}})
    await db["balanceTrend"].delete_many({"account_id": {"$in": account_ids}})
