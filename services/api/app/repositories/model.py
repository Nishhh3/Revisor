from __future__ import annotations
from datetime import datetime

from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Text

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import Integer
from sqlalchemy import DateTime

from app.database.base import Base
from app.database.mixins import TimestampMixin
from app.database.mixins import UUIDMixin

class Repository(UUIDMixin, TimestampMixin, Base):
    

    __tablename__ = "repositories"

    github_repo_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        nullable=False,
        index=True,
    )

    owner: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    full_name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    private: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    default_branch: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    html_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    clone_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    language: Mapped[str | None] = mapped_column(
    String(100),
    nullable=True,
    )

    stargazers_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    forks_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    watchers_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    open_issues_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    size: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    visibility: Mapped[str] = mapped_column(
        String(20),
        default="public",
    )

    created_at_github: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    updated_at_github: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    pushed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    owner_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from app.auth.model import User

    user: Mapped["User"] = relationship(
        back_populates="repositories",
    )

    pull_requests = relationship(
    "PullRequest",
    back_populates="repository",
    cascade="all, delete-orphan",
)