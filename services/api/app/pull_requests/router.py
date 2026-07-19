from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.model import User
from app.database.dependencies import get_db
from app.pull_requests.repository import PullRequestRepository
from app.pull_requests.schemas import PullRequestResponse
from app.pull_requests.schemas import PullRequestSyncResponse
from app.pull_requests.service import PullRequestService
from app.repositories.repository import RepositoryRepository

router = APIRouter(
    prefix="/repositories",
    tags=["Pull Requests"],
)


@router.post(
    "/{repository_id}/pull-requests/sync",
    response_model=PullRequestSyncResponse,
)
async def sync_pull_requests(
    repository_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    repository_repository = RepositoryRepository(db)

    repository = repository_repository.get_by_id(
        repository_id
    )

    if repository is None:
        raise HTTPException(
            status_code=404,
            detail="Repository not found",
        )

    service = PullRequestService(
        PullRequestRepository(db)
    )

    return await service.sync_pull_requests(
        current_user,
        repository,
    )


@router.get(
    "/{repository_id}/pull-requests",
    response_model=list[PullRequestResponse],
)
def get_pull_requests(
    repository_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    repository_repository = RepositoryRepository(db)

    repository = repository_repository.get_by_id(
        repository_id
    )

    if repository is None:
        raise HTTPException(
            status_code=404,
            detail="Repository not found",
        )

    service = PullRequestService(
        PullRequestRepository(db)
    )

    return service.get_pull_requests(
        repository
    )