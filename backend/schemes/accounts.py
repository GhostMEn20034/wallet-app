from typing import Optional
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

    class Config:
        validate_assignment = True

    @validator('balance', pre=True, always=True)
    def set_balance(cls, v):
        return round(v, 2)


class CreateAccountModel(BaseModel):
    name: str
    balance: condecimal(decimal_places=2) = 0
    bank_account: Optional[str]
    primary_currency: str
    color: str


class UpdateAccountModel(BaseModel):
    name: Optional[str]
    balance: Optional[condecimal(decimal_places=2)]
    bank_account: Optional[str]
    color: Optional[str]
