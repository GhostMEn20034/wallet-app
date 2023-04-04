import datetime
from typing import List
import fastapi
import pydantic
from client import db
from bson import ObjectId
from services.records import increment_the_balance, decrement_the_balance, funds_transfer
from schemes import records
from schemes import auth
from schemes.users import PyObjectId
from dependencies import get_current_user
from utils import convert_decimal

pydantic.json.ENCODERS_BY_TYPE[ObjectId] = str

router = fastapi.APIRouter(
    prefix='/records',
    tags=['records']
)


@router.post("/create")
async def create_record(record_data: records.CreateRecordModel = fastapi.Body(...),
                        user_token: auth.UserId = fastapi.Depends(get_current_user)):
    record_data = convert_decimal(record_data.dict())
    account = await db["accounts"].find_one({"_id": record_data.get("account_id"), "user.id": user_token.id})
    if account:
        record_type = record_data.get("record_type")
        match record_type:
            case "Income":
                increase_the_balance = await increment_the_balance(account.get("_id"), record_data.get("amount"))
                if increase_the_balance == 1:
                    del record_data["receiver"]
                    record_data["created_at"] = datetime.datetime.now()
                    created_record = await db["records"].insert_one(record_data)
                    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK,
                                                          content={"status": "The income was credited to your account"})
            case "Expense":
                decrease_the_balance = await decrement_the_balance(account.get("_id"), record_data.get("amount"))
                if decrease_the_balance == 1:
                    del record_data["receiver"]
                    record_data["created_at"] = datetime.datetime.now()
                    created_record = await db["records"].insert_one(record_data)
                    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content={
                        "status": "Funds have been successfully withdrawn from your account"})
            case "Transfer":
                receiver = await db["accounts"].find_one(
                    {"_id": record_data.get("receiver"), "user.id": user_token.id})
                if receiver:
                    transfer = await funds_transfer(account.get("_id"), record_data.get("receiver"),
                                                    record_data.get("amount"))
                    if transfer == 1:
                        record_data["created_at"] = datetime.datetime.now()
                        created_record = await db["records"].insert_one(record_data)
                        return fastapi.responses.JSONResponse(
                            status_code=fastapi.status.HTTP_200_OK,
                            content={
                                "status": "The funds have been transferred successfully"
                            })
            case _:
                pass

    return {"status": "BAD"}


@router.get("/", response_model=List[records.Record], response_model_exclude_none=True)
async def get_records(user_token: auth.UserId = fastapi.Depends(get_current_user)):
    accounts = await db["accounts"].find({"user.id": user_token.id}).to_list(100)
    account_ids = [account["_id"] for account in accounts]
    records = await db["records"].find({"account_id": {"$in": account_ids}}).to_list(500)

    return records


@router.delete("/{record_id}/delete", status_code=fastapi.status.HTTP_204_NO_CONTENT)
async def delete_record(record_id: PyObjectId, user_token: auth.UserId = fastapi.Depends(get_current_user)):
    accounts = await db["accounts"].find({"user.id": user_token.id}).to_list(100)
    account_ids = [account["_id"] for account in accounts]
    if accounts:
        deleted_record = await db["records"].delete_one({"_id": record_id, "account_id": {"$in": account_ids}})

