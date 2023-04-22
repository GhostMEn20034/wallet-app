import fastapi

from client import db
from schemes.users import PyObjectId


async def update_user(user_id: PyObjectId, update: dict) -> int:
    update_user_profile = await db["users"].update_one({"_id": user_id}, {"$set": update})

    if update.get("first_name"):
        update_user_reference = await db["accounts"].update_many(
            {"user.id": user_id}, {"$set": {"user.first_name": update["first_name"]}})

    return update_user_profile.modified_count


def compare_passwords(password1, password2):
    return True if password1 == password2 else False


async def validate_user(email, password1, password2):
    user = await db["users"].find_one({"email": email})
    if user is not None:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exist"
        )

    if not compare_passwords(password1, password2):
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )

    return True


# async def reset_password(password1, password2):
    
