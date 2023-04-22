from fastapi import HTTPException, status
from jose import jwt, exceptions
from pydantic import ValidationError
from twilio.rest import Client
from settings import SERVICE_SID, TWILIO_AUTH_TOKEN, ACCOUNT_SID, SERVICE_SID_RESET_PWD, ACCESS_SECRET_KEY, ALGORITHM

client = Client(ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def send_code(service_sid, email):
    verification = client.verify.v2.services(
        service_sid).verifications.create(
        to=email, channel='email'
    )
    assert verification.status == 'pending'


def check_code(service_sid, email, code):
    verification = client.verify.v2.services(
        service_sid).verification_checks.create(
        to=email, code=code
    )
    return verification.status == 'approved'


def send_verification_code(email):
    send_code(SERVICE_SID, email)


def check_verification_code(email, code):
    return check_code(SERVICE_SID, email, code)


def send_pwd_reset_code(email):
    send_code(SERVICE_SID_RESET_PWD, email)


def check_pwd_reset_code(email, code):
    return check_code(SERVICE_SID_RESET_PWD, email, code)


async def encode_reset_pwd_token(token):
    try:
        payload = jwt.decode(
            token, ACCESS_SECRET_KEY, algorithms=[ALGORITHM]
        )
        reset_password = payload.get("reset_password")

        if not reset_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Invalid OTP code, please send email to get new one")

    except(jwt.JWTError, ValidationError, exceptions.ExpiredSignatureError) as ex:
        match type(ex):
            case exceptions.ExpiredSignatureError:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                    detail="OTP code expired, please send email to get new one",
                                    headers={"WWW-Authenticate": "Bearer"},
                                    )

            case _:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
    return payload
