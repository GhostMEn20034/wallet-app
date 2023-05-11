from decimal import Decimal

from fastapi import HTTPException, status
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Dict
from jose import jwt

from schemes.auth import TokenPayload
from settings import ALGORITHM, ACCESS_SECRET_KEY, REFRESH_SECRET_KEY

ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
# REFRESH_TOKEN_EXPIRE_MINUTES = 20


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def get_hashed_password(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(subject: Dict, expires_minutes=None, expires_delta: timedelta = None) -> str:

    minutes = ACCESS_TOKEN_EXPIRE_MINUTES if expires_minutes is None else expires_minutes

    expires_delta = datetime.now() + timedelta(minutes=minutes)
    print(datetime.utcnow())
    to_encode = {"type": "access", "exp": expires_delta, **subject}
    encoded_jwt = jwt.encode(to_encode, ACCESS_SECRET_KEY, ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: Dict, expires_delta: timedelta = None) -> str:

    if expires_delta is not None:
        expires = datetime.now(timezone.utc) + expires_delta
    else:
        expires = datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
        print(expires)

    to_encode = {"type": "refresh", "exp": expires, "id": subject["id"]}
    encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, ALGORITHM)
    return encoded_jwt


def convert_decimal(dict_item):
    # This function iterates a dictionary looking for types of Decimal and converts them to Decimal128
    # Embedded dictionaries and lists are called recursively.
    if dict_item is None:
        return None

    for k, v in list(dict_item.items()):
        if isinstance(v, dict):
            convert_decimal(v)
        elif isinstance(v, list):
            for l in v:
                convert_decimal(l)
        elif isinstance(v, Decimal):
            dict_item[k] = float(str(v))

    return dict_item
