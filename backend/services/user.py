from client import db


async def update_user(user_id, update: dict) -> int:
    update_user_profile = await db["users"].update_one({"_id": user_id}, {"$set": dict(update)})

    if update["first_name"]:
        update_user_reference = await db["accounts"].update_one(
            {"user.id": user_id}, {"$set": {"user.first_name": update["first_name"]}})

    return update_user_profile.modified_count
