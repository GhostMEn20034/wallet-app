from pydantic import BaseModel, EmailStr
from .users import PyObjectId
from bson import ObjectId
from typing import Optional


class TokenPayload(BaseModel):
    type: str
    exp: int
    id: PyObjectId
    first_name: Optional[str]


class TokenScheme(BaseModel):
    access_token: str
    refresh_token: str


class SignUp(BaseModel):
    email: EmailStr
    primary_currency: str
    password1: str
    password2: str


class SignUpResponse(BaseModel):
    id: PyObjectId

    class Config:
        json_encoders = {ObjectId: str}


class UserId(BaseModel):
    id: PyObjectId


class RefreshToken(BaseModel):
    refresh_token: str
