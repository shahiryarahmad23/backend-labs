import hashlib
import secrets
from datetime import UTC, datetime, timedelta

import jwt, uuid, base64
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from klip.core import settings

password_hasher = PasswordHasher()


def password_hash(password: str):
    return password_hasher.hash(password)


def verify_password_hash(hash: str, password: str):
    try:
        return password_hasher.verify(hash, password)
    except VerifyMismatchError:
        return False


def create_access_token(user_id: str):
    now = datetime.now(UTC)
    expire = timedelta(minutes=settings.access_token_expires)
    payload = {"sub": user_id, "exp": now + expire}
    return jwt.encode(payload, settings.secretkey, algorithm="HS256")


def decode_access_token(token: str):
    try:
        return jwt.decode(token, settings.secretkey, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        raise jwt.InvalidTokenError("Invalid token") from None


def create_refresh_token():
    return secrets.token_urlsafe(32)


def hash_refresh_token(token: str):
    return hashlib.sha256(token.encode()).hexdigest()


def cursor_encode(created_at: datetime, id: uuid.UUID):
    return base64.urlsafe_b64encode(
        (f"{created_at.isoformat()}:{id}").encode()
    ).decode()


def cursor_decode(cursor: str):
    value = base64.urlsafe_b64decode(cursor.encode()).decode()

    created_at, id = value.split(":")

    return datetime.fromisoformat(created_at), uuid.UUID(id)
