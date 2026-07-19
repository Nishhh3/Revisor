from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PullRequestResponse(BaseModel):

    id: UUID

    github_pr_id: int

    number: int

    title: str

    body: str | None

    state: str

    draft: bool

    merged: bool

    author: str

    base_branch: str

    head_branch: str

    html_url: str

    created_at_github: datetime | None

    updated_at_github: datetime | None

    closed_at: datetime | None

    merged_at: datetime | None

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class PullRequestSyncResponse(BaseModel):

    total: int

    created: int

    updated: int