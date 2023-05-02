import datetime
from typing import List
import fastapi
import pydantic
from client import db
from bson import ObjectId
from services.records import (increment_the_balance,
                              decrement_the_balance,
                              funds_transfer,
                              aggregate_records,
                              create_record)
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
async def route_create_record(record_data: records.CreateRecordModel = fastapi.Body(...),
                              user_token: auth.UserId = fastapi.Depends(get_current_user)):
    record_data = convert_decimal(record_data.dict())
    account = await db["accounts"].find_one({"_id": record_data.get("account_id"), "user.id": user_token.id})
    if account:
        return await create_record(record_data, account, user_token.id)


@router.get("/", response_model=List[records.AggregatedRecords], response_model_exclude_none=True)
async def get_records(user_token: auth.UserId = fastapi.Depends(get_current_user)):
    accounts = await db["accounts"].find({"user.id": user_token.id}).to_list(100)
    account_ids = [account["_id"] for account in accounts]

    aggregated_records = await aggregate_records(account_ids)

    return aggregated_records


@router.delete("/delete")
async def delete_record(record_ids: records.DeleteRecordsData,
                        user_token: auth.UserId = fastapi.Depends(get_current_user)):
    record_ids = record_ids.record_ids
    accounts = await db["accounts"].find({"user.id": user_token.id}).to_list(100)
    account_ids = [account["_id"] for account in accounts]

    if accounts and len(record_ids) == 1:
        record_id = record_ids[0]
        deleted_record = await db["records"].delete_one({"_id": record_id, "account_id": {"$in": account_ids}})

        if deleted_record.deleted_count == 1:
            return fastapi.responses.Response(status_code=204)

    if accounts:
        deleted_records = await db["records"].delete_many(
            {"_id": {"$in": record_ids}, "account_id": {"$in": account_ids}})

        if deleted_records.deleted_count >= 1:
            return fastapi.responses.Response(status_code=204)

    return fastapi.responses.JSONResponse(status_code=400,
                                          content={"status": "Impossible to delete records that doesn't exists"})
