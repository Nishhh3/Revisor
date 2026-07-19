from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

class RepositoryResponse(BaseModel):

    id: UUID

    github_repo_id: int

    owner: str
    name: str
    full_name: str
    description: str | None

    private: bool
    visibility: str

    default_branch: str

    language: str | None

    stargazers_count: int
    forks_count: int
    watchers_count: int
    open_issues_count: int
    size: int

    html_url: str
    clone_url: str

    created_at_github: datetime | None
    updated_at_github: datetime | None
    pushed_at: datetime | None

    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class RepositorySyncResponse(BaseModel):
    total: int
    created: int
    updated: int