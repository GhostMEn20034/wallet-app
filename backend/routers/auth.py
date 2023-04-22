from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, exceptions
from pydantic import ValidationError

from schemes.auth import TokenScheme, RefreshToken, TokenPayload
from client import db
from settings import REFRESH_SECRET_KEY, ALGORITHM
from utils import (
    verify_password,
    create_access_token,
    create_refresh_token,
)

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


@router.post('/token', summary="Create access and refresh tokens for user", response_model=TokenScheme)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await db["users"].find_one({"email": form_data.username})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    hashed_pass = user.get("password")
    if not verify_password(form_data.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    subject = {
        "id": str(user["_id"]),
        "first_name": user["first_name"],
    }

    return {
        "access_token": create_access_token(subject),
        "refresh_token": create_refresh_token(subject),
    }


@router.post("/token/refresh", response_model=TokenScheme)
async def refresh_tokens(refresh_token: RefreshToken):

    refresh_token = refresh_token.dict().get("refresh_token")

    try:
        payload = jwt.decode(
            refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except(jwt.JWTError, ValidationError, exceptions.ExpiredSignatureError) as ex:
        match type(ex):
            case exceptions.ExpiredSignatureError:
                print(type(ex))
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                    detail="Unauthorized",
                                    headers={"WWW-Authenticate": "Bearer"},
                                    )

            case _:
                print(type(ex))
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )

    user = await db["users"].find_one({"_id": token_data.id})

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )

    subject = {
        "id": str(user["_id"]),
    }

    return {
        "access_token": create_access_token(subject),
        "refresh_token": create_refresh_token(subject)
    }
