from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import date, datetime
from enum import Enum


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class GenderEnum(str, Enum):
    male = 'Male'
    female = 'Female'
    unspecified = 'Unspecified'


class UserProfile(BaseModel):
    first_name: str
    last_name: Optional[str]
    email: EmailStr
    date_of_birth: Optional[date]
    gender: Optional[GenderEnum]
    password: str

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "user@exampe.com",
                "date_of_birth": "2004-05-14",
                "gender": "Male",
                'password': 'xxxx3333',
            }
        }


class UpdateUserProfile(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[EmailStr]
    date_of_birth: Optional[str]
    gender: Optional[GenderEnum]

    class Config:
        use_enum_values = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
           "example": {
               "first_name": "John",
               "last_name": "Doe",
               "email": "user@exampe.com",
               "date_of_birth": "2004-05-14",
               "gender": "Female",
           }
        }

    @validator("date_of_birth", pre=True)
    def parse_date_of_birth(cls, value):
        return str(datetime.strptime(
            value,
            "%Y-%m-%d"
        ).date())


# user = {
#     "email": "eee@example.com",
#     "password": "some_password",
#     "first_name": "eee@example.com",
# }
#
# user_one = UserProfile(**user)
# print(user_one.dict())
