from client import db
from typing import List


async def delete_accounts_and_records(account_ids: List):
    deleted_accounts = await db["accounts"].delete_many({"_id": {"$in": account_ids}})
    deleted_records = await db["records"].delete_many({"account_id": {"$in": account_ids}})

    if 1 in {deleted_records.deleted_count, deleted_accounts.deleted_count}:
        return 1
