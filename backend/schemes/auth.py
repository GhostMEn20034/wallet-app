from pydantic import BaseModel, EmailStr
from .user import PyObjectId
from bson import ObjectId


class TokenPayload(BaseModel):
    type: str
    exp: int
    id: PyObjectId


class TokenScheme(BaseModel):
    access_token: str
    refresh_token: str


class UserAuth(BaseModel):
    email: EmailStr
    password: str


class SignUpResponse(BaseModel):
    id: PyObjectId

    class Config:
        json_encoders = {ObjectId: str}


class UserId(BaseModel):
    id: PyObjectId
