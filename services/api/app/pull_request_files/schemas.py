from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PullRequestFileResponse(BaseModel):

    id: UUID

    github_file_sha: str

    filename: str

    status: str

    additions: int

    deletions: int

    changes: int

    patch: str | None

    blob_url: str | None

    raw_url: str | None

    contents_url: str | None

    model_config = ConfigDict(
        from_attributes=True
    )


class PullRequestFileSyncResponse(BaseModel):

    total: int

    created: int

    updated: int