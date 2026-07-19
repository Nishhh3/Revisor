from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import relationship

from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.database.mixins import TimestampMixin
from app.database.mixins import UUIDMixin


class PullRequest(UUIDMixin, TimestampMixin, Base):

    __tablename__ = "pull_requests"

    github_pr_id: Mapped[int] = mapped_column(
        Integer,
        unique=True,
        nullable=False,
        index=True,
    )

    number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    body: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    state: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    draft: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    merged: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    author: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    base_branch: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    head_branch: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    html_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    created_at_github: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    updated_at_github: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    merged_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    repository_id: Mapped[str] = mapped_column(
        ForeignKey("repositories.id"),
        nullable=False,
    )

    repository = relationship(
        "Repository",
        back_populates="pull_requests",
    )
    
    files = relationship(
    "PullRequestFile",
    back_populates="pull_request",
    cascade="all, delete-orphan",
    )