import uuid
from enum import Enum
from datetime import datetime

from sqlalchemy import DateTime, func, ForeignKey
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column

from klip.db import Base


class VisibleValue(str, Enum):
    PUBLIC = "public"
    UNLISTED = "unlisted"
    PRIVATE = "private"


class SnippetTable(Base):
    __tablename__ = "snippets"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("User.id", ondelete="CASCADE"), nullable=False, index=True
    )
    public_id: Mapped[str] = mapped_column(nullable=False, index=True)
    body: Mapped[str] = mapped_column(nullable=False, default="")
    title: Mapped[str] = mapped_column(nullable=False, index=True)
    visibility: Mapped[VisibleValue] = mapped_column(
        SqlEnum(VisibleValue), nullable=False, default=VisibleValue.PUBLIC
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
