import fastapi
from dependencies import get_current_user
from schemes.users import UserProfile, UpdateUserProfile
from schemes.auth import (
    SignUpResponse,
    SignUp,
    UserId,
)
from client import db
from utils import get_hashed_password
from services import users as usr
from services.delete_related_info import delete_accounts_and_records


router = fastapi.APIRouter(
    prefix='/user',
    tags=['users'],
)


@router.post('/signup', summary="Create new user", response_model=SignUpResponse,
             status_code=fastapi.status.HTTP_201_CREATED)
async def create_user(data: SignUp):
    # querying database to check if user already exist
    is_validated_credentials = await usr.validate_user(data.email, data.password1, data.password2)

    if is_validated_credentials:
        user_data = {
            'email': data.email,
            'first_name': data.email,
            'primary_currency': data.primary_currency
        }

        user = UserProfile(**user_data).dict()
        user["password"] = get_hashed_password(data.password1)
        inserted_user = await db["users"].insert_one(user)
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
        await usr.update_user(user_id, user_profile)

    user = await db["users"].find_one({"_id": user_id})
    return user


@router.delete("/profile/delete", status_code=fastapi.status.HTTP_204_NO_CONTENT)
async def delete_profile(user_token: UserId = fastapi.Depends(get_current_user)):
    accounts = await db["accounts"].find({"user.id": user_token.id}).to_list(100)
    delete_user = await db["users"].delete_one({"_id": user_token.id})
    account_ids = [account["_id"] for account in accounts]
    if account_ids:
        await delete_accounts_and_records(account_ids)
