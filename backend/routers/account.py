import datetime
from typing import List

import pydantic
import fastapi
from bson import ObjectId
from client import db
from schemes.account import Account, CreateAccountModel
from dependencies import get_current_user
from schemes.auth import UserId


pydantic.json.ENCODERS_BY_TYPE[ObjectId] = str


router = fastapi.APIRouter(
    prefix="/accounts"
)


@router.post("/create", response_description="Add new account", response_model=Account,
             status_code=fastapi.status.HTTP_201_CREATED)
async def create_an_account(user_token: UserId = fastapi.Depends(get_current_user),
                            account: CreateAccountModel = fastapi.Body(...)):
    user = await db["users"].find_one({"_id": user_token.id})
    if user:
        account = account.dict()
        account["balance"] = float(account["balance"])
        account.update({"user": {"id": user.get("_id"), "first_name": user.get("first_name")},
                        "created_at": str(datetime.datetime.now()), "modified_at": str(datetime.datetime.now())})
        inserted_account = await db["accounts"].insert_one(account)
        return account


@router.get("/", response_description="Account list", response_model=List[Account])
async def account_list(user_token: UserId = fastapi.Depends(get_current_user)):
    accounts = await db["accounts"].find({"user.id": user_token.id}).to_list(10000)

    return accounts
