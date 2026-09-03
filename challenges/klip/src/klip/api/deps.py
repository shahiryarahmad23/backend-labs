import uuid

import jwt
from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from klip.core import decode_access_token
from klip.db import get_db
from klip.models import User,UserRole

credential_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid credential",
    headers={"WWW-Authenticate": "Bearer"},
)
oauth_schema = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth_schema), db: Session = Depends(get_db)):

    try:
        payload = decode_access_token(token)
    except jwt.InvalidTokenError:
        raise credential_exception from None

    if payload is None:
        raise credential_exception from None

    user_id = payload["sub"]

    if user_id is None:
        raise credential_exception from None
    try:
        user_uuid = uuid.UUID(user_id)
    except TypeError:
        raise credential_exception from None

    user = db.execute(select(User).where(User.id == user_uuid)).scalar_one_or_none()

    if user is None:
        raise credential_exception from None

    return user

def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Admin access required!")
    return current_user
