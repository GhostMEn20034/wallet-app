import datetime
from typing import List, Tuple, Optional, Union
import fastapi
import pydantic
from client import db
from bson import ObjectId
from services.records import (records_by_date,
                              records_by_amount,
                              create_record,
                              create_filter_dict)
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


@router.get("/", response_model=Union[List[records.AggregatedRecords], List[records.Record]],
            response_model_exclude_none=True, response_model_by_alias=True)
async def get_records(user_token: auth.UserId = fastapi.Depends(get_current_user),
                      sort_by: str = fastapi.Query("date", enum=["date", "amount"]),
                      order: str = fastapi.Query("desc", enum=["asc", "desc"]),
                      record_filter: records.RecordFilter = fastapi.Depends(records.RecordFilter),
                      account_ids: Optional[List[PyObjectId]] = fastapi.Query([], style="commaDelimited")):
    accounts = await db["accounts"].find({"user.id": user_token.id}).to_list(100)

    record_filter = record_filter.dict(exclude_none=True)

    if account_ids:
        account_ids = [account["_id"] for account in accounts if account["_id"] in account_ids]
    else:
        account_ids = [account["_id"] for account in accounts]

    filter_dict = create_filter_dict(record_filter)

    reverse = bool(order == "desc")

    match sort_by:
        case "date":
            return await records_by_date(account_ids, filter_dict, reverse)
        case "amount":
            return await records_by_amount(account_ids, filter_dict, reverse)


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
