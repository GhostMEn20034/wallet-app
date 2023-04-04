from client import db
from schemes.users import PyObjectId


async def update_user(user_id: PyObjectId, update: dict) -> int:
    update_user_profile = await db["users"].update_one({"_id": user_id}, {"$set": update})

    if update["first_name"]:
        update_user_reference = await db["accounts"].update_many(
            {"user.id": user_id}, {"$set": {"user.first_name": update["first_name"]}})

    return update_user_profile.modified_count
