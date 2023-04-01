import datetime
from typing import List
import pydantic
import fastapi
from bson import ObjectId
from client import db
from schemes.account import Account, CreateAccountModel, UpdateAccountModel
from dependencies import get_current_user
from schemes.auth import UserId
from schemes.user import PyObjectId
from fastapi.responses import JSONResponse
from utils import convert_decimal

pydantic.json.ENCODERS_BY_TYPE[ObjectId] = str

router = fastapi.APIRouter(
    prefix='/accounts',
    tags=['accounts'],
)


@router.post("/create", response_description="Add new account", response_model=Account,
             status_code=fastapi.status.HTTP_201_CREATED)
async def create_an_account(user_token: UserId = fastapi.Depends(get_current_user),
                            account: CreateAccountModel = fastapi.Body(...)):
    user = await db["users"].find_one({"_id": user_token.id})
    if user:
        account = account.dict()
        account.update({"user": {"id": user.get("_id"), "first_name": user.get("first_name")},
                        "created_at": str(datetime.datetime.now()), "modified_at": str(datetime.datetime.now())})
        inserted_account = await db["accounts"].insert_one(convert_decimal(account))
        return account


@router.get("/", response_description="Account list", response_model=List[Account])
async def account_list(user_token: UserId = fastapi.Depends(get_current_user)):
    accounts = await db["accounts"].find({"user.id": user_token.id}).to_list(10000)

    return accounts


@router.put("/{account_id}/update")
async def update_bank_account(account_id: PyObjectId, user_token: UserId = fastapi.Depends(get_current_user),
                         account: UpdateAccountModel = fastapi.Body(...)):
    account = {k: v for k, v in account.dict().items() if v is not None}
    account["modified_at"] = datetime.datetime.now()

    user_id = user_token.id
    if len(account) >= 1:
        update_account = await db["accounts"].update_one({"user.id": user_id, "_id": account_id},
                                                         {"$set": convert_decimal(account)})

        if update_account.modified_count == 1 and (
                updated_account := await db["accounts"].find_one({"user.id": user_id, "_id": account_id})
        ) is not None:
            return updated_account

    if (
            existing_account := await db["accounts"].find_one({"user.id": user_id, "_id": account_id})
    ) is not None:
        return existing_account

    return JSONResponse(status_code=fastapi.status.HTTP_404_NOT_FOUND, content={"error": "account didn't found"})


@router.delete("/{account_id}/delete", status_code=fastapi.status.HTTP_204_NO_CONTENT)
async def delete_account(account_id: PyObjectId, user_token: UserId = fastapi.Depends(get_current_user)):
    deleted_account = await db["accounts"].delete_one({"_id": account_id, "user.id": user_token.id})
