from __future__ import annotations

from datetime import datetime

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


class PullRequestFile(UUIDMixin, TimestampMixin, Base):

    __tablename__ = "pull_request_files"

    github_file_sha: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    filename: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    additions: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    deletions: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    changes: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    patch: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    blob_url: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    raw_url: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    contents_url: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    pull_request_id = mapped_column(
        ForeignKey("pull_requests.id"),
        nullable=False,
    )

    pull_request = relationship(
        "PullRequest",
        back_populates="files",
    )