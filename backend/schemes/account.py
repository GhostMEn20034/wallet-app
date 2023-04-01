from typing import Dict, Optional
from pydantic import BaseModel, condecimal, root_validator, Field
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
    user: ReferenceToUser
    created_at: str = datetime.datetime.now()
    modified_at: str = datetime.datetime.now()

    class Config:
        validate_assignment = True

    @root_validator
    def number_validator(cls, values):
        values["modified_at"] = datetime.datetime.now()
        return values


class CreateAccountModel(BaseModel):
    name: str
    balance: condecimal(decimal_places=2)
