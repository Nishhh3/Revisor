from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import BigInteger
from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.database.base import Base
from app.database.mixins import TimestampMixin
from app.database.mixins import UUIDMixin
from sqlalchemy.orm import relationship
from sqlalchemy import Text


class User(UUIDMixin, TimestampMixin, Base):
    
    """
    GitHub authenticated PRISM user.
    """

    __tablename__ = "users"

    id: Mapped[UUID]

    github_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        nullable=False,
        index=True,
    )

    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
        index=True,
    )

    avatar_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from app.repositories.model import Repository

    repositories: Mapped[list["Repository"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    github_access_token: Mapped[str] = mapped_column(
    Text,
    nullable=True,
    )

    github_token_type: Mapped[str] = mapped_column(
        String(50),
        default="bearer",
        nullable=True,
    )

    github_scope: Mapped[str | None] = mapped_column(
    Text,
    nullable=True,
    )