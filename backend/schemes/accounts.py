from typing import Optional, List
from pydantic import BaseModel, condecimal, root_validator, validator, Field
import datetime

from .users import PyObjectId


class ReferenceToUser(BaseModel):
    id: PyObjectId
    first_name: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {PyObjectId: str}


class Account(BaseModel):
    id: PyObjectId = Field(alias="_id")
    name: str
    balance: condecimal(decimal_places=2)
    bank_account: Optional[str]
    currency: str
    color: str
    converted_balance: Optional[float]
    created_at: datetime.datetime

    class Config:
        validate_assignment = True

    @validator('balance', pre=True, always=True)
    def set_balance(cls, v):
        return round(v, 2)


class CreateAccountModel(BaseModel):
    name: str
    balance: condecimal(decimal_places=2) = 0
    currency: str
    color: str


class UpdateAccountModel(BaseModel):
    name: Optional[str]
    balance: Optional[condecimal(decimal_places=2)]
    color: Optional[str]


class BalanceTrend(BaseModel):
    account_id: PyObjectId
    initial: bool
    balance: float
    date: datetime.datetime

    @validator('balance', pre=True, always=True)
    def set_balance(cls, v):
        return round(v, 2)


class AggregatedAccount(BaseModel):
    id: PyObjectId = Field(alias="_id")
    name: str
    balance: condecimal(decimal_places=2)
    bank_account: Optional[str]
    currency: str
    color: str
    created_at: datetime.datetime
    current_period: List[BalanceTrend]
    percentage_change: float

    @validator('balance', pre=True, always=True)
    def set_balance(cls, v):
        return round(v, 2)
