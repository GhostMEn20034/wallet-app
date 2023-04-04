import fastapi
from dependencies import get_current_user
from schemes.users import UserProfile, UpdateUserProfile
from schemes.auth import (
    SignUpResponse,
    UserAuth,
    UserId,
)
from client import db
from utils import get_hashed_password
from services import users as usr
from services.delete_documents import delete_accounts_and_records

router = fastapi.APIRouter(
    prefix='/user',
    tags=['users'],
)


@router.post('/signup', summary="Create new user", response_model=SignUpResponse,
             status_code=fastapi.status.HTTP_201_CREATED)
async def create_user(data: UserAuth):
    # querying database to check if user already exist
    user = await db["users"].find_one({"email": data.email})
    if user is not None:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exist"
        )
    user_data = {
        'email': data.email,
        'password': get_hashed_password(data.password),
        'first_name': data.email,
    }

    user = UserProfile(**user_data)
    inserted_user = await db["users"].insert_one(user.dict())
    response = {"id": inserted_user.inserted_id}
    return response


@router.get("/profile", response_model=UserProfile)
async def profile(user_token: UserId = fastapi.Depends(get_current_user)):
    user = await db["users"].find_one({"_id": user_token.id})
    return user


@router.put("/profile/update", response_model=UserProfile)
async def update_profile(user_token: UserId = fastapi.Depends(get_current_user),
                         user_profile: UpdateUserProfile = fastapi.Body(...)):
    user_profile = {k: v for k, v in user_profile.dict().items() if v is not None}

    user_id = user_token.id

    if len(user_profile) >= 1:
        update_user_profile = await usr.update_user(user_id, user_profile)
        if update_user_profile == 1:
            if (
                    updated_user := await db["users"].find_one({"_id": user_id})
            ) is not None:
                return updated_user

    if (existing_user := await db["users"].find_one({"_id": user_id})) is not None:
        return existing_user


@router.delete("/profile/delete", status_code=fastapi.status.HTTP_204_NO_CONTENT)
async def delete_profile(user_token: UserId = fastapi.Depends(get_current_user)):
    user = await db["users"].delete_one({"_id": user_token.id})
    accounts = await db["accounts"].find({"user.id": user_token.id}).to_list(100)
    account_ids = [account["_id"] for account in accounts]
    if account_ids:
        delete_related = await delete_accounts_and_records(account_ids)
