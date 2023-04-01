from client import db


async def delete_accounts(filter):
    deleted_accounts = await db["accounts"].delete_many({"user.id": filter})
    return deleted_accounts.deleted_count
