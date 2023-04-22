from pydantic import BaseModel, EmailStr


class VerificationData(BaseModel):
    email: EmailStr
    code: str


class ResetPasswordData(BaseModel):
    token: str
    new_password: str
