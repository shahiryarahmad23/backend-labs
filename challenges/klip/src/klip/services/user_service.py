from datetime import UTC, datetime, timedelta

from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from klip.core import (
    create_access_token,
    create_refresh_token,
    hash_refresh_token,
    password_hash,
    settings,
    verify_password_hash,
)
from klip.models import RefreshTable, User
from klip.schemas import TokenPair, UserCreate


def register_user(user: UserCreate, db: Session):

    result = db.execute(
        select(User).where(User.email == user.email)
    ).scalar_one_or_none()

    if result:
        raise ValueError("Email already exist")

    hashed = password_hash(user.password)

    user = User(email=user.email, hashed_password=hashed)

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def login_user(form_data: OAuth2PasswordRequestForm, db: Session):

    user = db.execute(
        select(User).where(User.email == form_data.username)
    ).scalar_one_or_none()

    if user is None:
        raise ValueError("Invalid credentials")
    if not verify_password_hash(user.hashed_password, form_data.password):
        raise ValueError("Invalid credentials")

    access = create_access_token(str(user.id))
    raw_refresh_token = create_refresh_token()

    expire = timedelta(days=settings.refresh_token_expires) + datetime.now(UTC)

    refresh_token = RefreshTable(
        hashed_token=hash_refresh_token(raw_refresh_token),
        expire_at=expire,
        user_id=user.id,
    )

    db.add(refresh_token)
    db.commit()

    return TokenPair(access_token=access, refresh_token=raw_refresh_token)
