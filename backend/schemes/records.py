from typing import Optional, List, Dict, Union
from pydantic import BaseModel, condecimal, validator, Field
from .users import PyObjectId
from enum import Enum
import fastapi
import datetime
import decimal


class RecordType(str, Enum):
    income = 'Income'
    expense = 'Expense'
    transfer_withdrawal = 'Transfer withdrawal'
    transfer_income = 'Transfer income'


class RecordTypeCreate(str, Enum):
    income = 'Income'
    expense = 'Expense'
    transfer = 'Transfer'


class CreateRecordModel(BaseModel):
    account_id: PyObjectId
    receiver: Optional[PyObjectId]
    amount: condecimal(decimal_places=2, ge=decimal.Decimal(0.0099))
    category: Optional[str]
    record_type: RecordTypeCreate

    class Config:
        use_enum_values = True


class Record(BaseModel):
    id: PyObjectId = Field(alias='_id')
    account_id: PyObjectId
    account_name: str
    sender: Optional[PyObjectId]
    receiver: Optional[PyObjectId]
    amount: condecimal(decimal_places=2, ge=decimal.Decimal(0.0099))
    category: str
    record_type: RecordType
    created_at: datetime.datetime


class AggregatedRecords(BaseModel):
    agg_date: datetime.date = Field(alias='date')
    agg_records: List[Record] = Field(alias='records')


class DeleteRecordsData(BaseModel):
    record_ids: List[PyObjectId]


class RecordFilter(BaseModel):
    categories: Optional[List[str]] = Field(fastapi.Query([]))
    min_amount: Optional[int] = None
    max_amount: Optional[int] = None
    record_types: Optional[List[RecordType]] = Field(fastapi.Query([]))

    @validator("record_types")
    def record_types_default(cls, v):
        if not v:
            return list(RecordType)
        return v

    class Config:
        use_enum_values = True

    class Config:
        query_model = True
        schema_extra = {
            "example": {
                "categories": ["Dwelling", "Entertainment"],
                "min_amount": 10.00,
                "max_amount": 100.00
            },
            "description": "A filter for records based on category and amount"
        }


class Accounts(BaseModel):
    id: PyObjectId
    name: str


class ResponseOfRecords(BaseModel):
    response: Union[List[AggregatedRecords], List[Record]]
    accounts: List[Accounts]
