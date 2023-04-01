from typing import Optional
from pydantic import BaseModel, condecimal, root_validator
import datetime

from .user import PyObjectId


class ReferenceToUser(BaseModel):
    id: PyObjectId
    first_name: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {PyObjectId: str}


class Account(BaseModel):
    name: str
    balance: condecimal(decimal_places=2)
    bank_account_number: Optional[str]
    user: ReferenceToUser
    created_at: datetime.datetime = datetime.datetime.now()
    modified_at: datetime.datetime = datetime.datetime.now()

    class Config:
        validate_assignment = True

    @root_validator
    def number_validator(cls, values):
        values["modified_at"] = datetime.datetime.now()
        return values


class CreateAccountModel(BaseModel):
    name: str
    balance: condecimal(decimal_places=2)
    bank_account_number: str


class UpdateAccountModel(BaseModel):
    name: Optional[str]
    balance: Optional[condecimal(decimal_places=2)]
    bank_account: Optional[str]
