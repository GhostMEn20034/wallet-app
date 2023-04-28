from typing import Optional, List
from pydantic import BaseModel, condecimal, validator, Field
from .users import PyObjectId
from enum import Enum
import datetime


class RecordType(str, Enum):
    income = 'Income'
    expense = 'Expense'
    transfer = 'Transfer'


class CreateRecordModel(BaseModel):
    account_id: PyObjectId
    receiver: Optional[PyObjectId]
    amount: condecimal(decimal_places=2)
    category: str
    record_type: RecordType

    class Config:
        use_enum_values = True

    @validator('amount', pre=True, always=True)
    def set_ts_now(cls, v):
        return float(round(v, 2))


class Record(BaseModel):
    id: PyObjectId = Field(alias='_id')
    account_id: PyObjectId
    account_name: str
    receiver: Optional[PyObjectId]
    amount: condecimal(decimal_places=2)
    category: str
    record_type: RecordType
    created_at: datetime.datetime = datetime.datetime.now()


class AggregatedRecords(BaseModel):
    date: datetime.date
    records: List[Record]


class DeleteRecordsData(BaseModel):
    record_ids: List[PyObjectId]

