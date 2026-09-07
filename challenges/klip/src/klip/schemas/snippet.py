import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from ..models import VisibleValue


class SnippetCreate(BaseModel):
    title: str
    body: str
    visibility: VisibleValue
    expires_at: datetime | None = None


class SnippetRead(BaseModel):
    owner_id: uuid.UUID
    title: str
    body: str
    public_id: str
    visibility: VisibleValue
    created_at: datetime
    expires_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class SnippetListRead(BaseModel):
    snippets: list[SnippetRead]
    cursor: str | None
