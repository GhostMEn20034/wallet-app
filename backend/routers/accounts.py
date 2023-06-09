import datetime
from typing import List
import pydantic
import fastapi
from bson import ObjectId
from client import db
from schemes.accounts import Account, CreateAccountModel, UpdateAccountModel, AggregatedAccount
from dependencies import get_current_user
from schemes.auth import UserId
from schemes.users import PyObjectId
from services.accounts import get_accounts, get_account, update_account, create_account
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
    return await create_account(user, account)


@router.get("/", response_description="Account list", response_model=List[Account], response_model_exclude_none=True)
async def account_list(user_token: UserId = fastapi.Depends(get_current_user),
                       sort_by: str = fastapi.Query("name", enum=["name", "balance"]),
                       order: str = fastapi.Query("asc", enum=["asc", "desc"]),
                       ):
    user = await db["users"].find_one({"_id": user_token.id})
    reverse = bool(order == "desc")
    accounts = await get_accounts(user_token.id, user.get("primary_currency"), reverse, sort_by)
    return accounts


@router.get("/{account_id}", response_model=AggregatedAccount)
async def account_detail(account_id: PyObjectId, user_token: UserId = fastapi.Depends(get_current_user)):
    account = await get_account(user_token.id, account_id)
    return account if account else []


@router.put("/{account_id}/update")
async def update_bank_account(account_id: PyObjectId, user_token: UserId = fastapi.Depends(get_current_user),
                              account: UpdateAccountModel = fastapi.Body(...)):
    account = {k: v for k, v in account.dict().items() if v is not None}
    account["modified_at"] = datetime.datetime.utcnow()

    user_id = user_token.id
    if len(account) >= 1:
        await update_account(user_id, account_id, account)

    updated_account = await db["accounts"].find_one({"_id": account_id})

    if updated_account:
        return updated_account

    return JSONResponse(status_code=fastapi.status.HTTP_404_NOT_FOUND, content={"error": "account didn't found"})


@router.delete("/{account_id}/delete", status_code=fastapi.status.HTTP_204_NO_CONTENT)
async def delete_account(account_id: PyObjectId, user_token: UserId = fastapi.Depends(get_current_user)):
    deleted_account = await db["accounts"].delete_one({"_id": account_id, "user_id": user_token.id})
    deleted_related_records = await db["records"].delete_many({"account_id": account_id})
    delete_balance_trend = db["balanceTrend"].delete_many({"account_id": account_id})
