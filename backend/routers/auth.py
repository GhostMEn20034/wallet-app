from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from schemes.auth import TokenScheme
from client import db
from utils import (
    verify_password,
    create_access_token,
    create_refresh_token
    )

router = APIRouter(prefix="/auth")


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

    return {
        "access_token": create_access_token(user['_id']),
        "refresh_token": create_refresh_token(user['_id']),
    }
