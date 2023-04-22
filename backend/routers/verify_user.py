import asyncio
import fastapi
from pydantic import EmailStr
from twilio.base.exceptions import TwilioRestException
from utils import create_access_token, get_hashed_password
from client import db
from schemes.auth import UserAuth
from schemes.verify_user import VerificationData, ResetPasswordData
from services.users import validate_user
from services.verify_user import (send_verification_code, check_verification_code,
                                  send_pwd_reset_code, check_pwd_reset_code, encode_reset_pwd_token)

router = fastapi.APIRouter(
    tags=['verify_email']
)


@router.post('/signup/validate-credentials')
async def validate_credentials(data: UserAuth):
    is_validated_credentials = await validate_user(data.email, data.password1, data.password2)

    if is_validated_credentials:
        await asyncio.get_event_loop().run_in_executor(None, send_verification_code, data.email)
        return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content={"status": "valid"})


@router.post('/signup/verify-email')
async def verify_email(data: VerificationData):
    try:
        verified = await asyncio.get_event_loop().run_in_executor(
            None, check_verification_code, data.email, data.code
        )
    except TwilioRestException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail="a code message has not been sent to this email"
        )
    if verified:
        return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content={"status": "verified"})

    raise fastapi.HTTPException(
        status_code=fastapi.status.HTTP_400_BAD_REQUEST,
        detail="The code is incorrect"
    )


@router.post('/pwd-reset/verify-email')
async def validate_email(email: EmailStr = fastapi.Form(...)):
    user = await db["users"].find_one({"email": email})
    if user is None:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail="User with this email doesn't exist"
        )

    await asyncio.get_event_loop().run_in_executor(None, send_pwd_reset_code, email)
    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content={"status": "valid"})


@router.post('/pwd-reset/check-otp')
async def check_otp(data: VerificationData):
    try:
        verified = await asyncio.get_event_loop().run_in_executor(
            None, check_pwd_reset_code, data.email, data.code
        )
    except TwilioRestException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail="a code message has not been sent to this email"
        )

    if verified:
        subject = {
            "email": data.email,
            "reset_password": True
        }

        return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK,
                                              content={"reset_pwd_token": create_access_token(subject, 5)})

    raise fastapi.HTTPException(
        status_code=fastapi.status.HTTP_400_BAD_REQUEST,
        detail="The code is incorrect"
    )


@router.post("/reset-password")
async def reset_pwd(data: ResetPasswordData):
    payload = await encode_reset_pwd_token(data.token)

    user = await db["users"].find_one({"email": payload.get("email")})

    if not user:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )

    update_pwd = await db["users"].update_one({"email": payload.get("email")},
                                              {"$set": {"password": get_hashed_password(data.new_password)}})

    if update_pwd.modified_count == 1:
        return fastapi.responses.JSONResponse(status_code=200,
                                              content={"status": "Password has been changed successful"})
