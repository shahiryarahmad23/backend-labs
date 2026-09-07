import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from ..models import UserRole, VisibleValue


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: uuid.UUID
    email: EmailStr
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshToken(BaseModel):
    refresh_token: str


class SnippetCreate(BaseModel):
    title: str
    body: str
    visibility: VisibleValue
    expires_at: datetime | None = None


class SnippetRead(BaseModel):
    owner_id: uuid.UUID
    title: str
    body: str
    visibility: VisibleValue
    created_at: datetime
    expires_at: datetime | None = None
