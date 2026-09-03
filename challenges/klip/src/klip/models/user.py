import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, func
from sqlalchemy import Enum as SQLenum
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base


class UserRole(str, Enum):  # noqa : UP042
    ADMIN = "admin"
    USER = "user"


class User(Base):
    __tablename__ = "User"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SQLenum(UserRole), nullable=False, default=UserRole.USER
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
