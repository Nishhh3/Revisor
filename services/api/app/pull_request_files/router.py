from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.model import User
from app.database.dependencies import get_db

from app.pull_requests.repository import PullRequestRepository

from app.pull_request_files.repository import PullRequestFileRepository
from app.pull_request_files.schemas import (
    PullRequestFileResponse,
    PullRequestFileSyncResponse,
)
from app.pull_request_files.service import PullRequestFileService

router = APIRouter(
    prefix="/pull-requests",
    tags=["Changed Files"],
)


@router.post(
    "/{pull_request_id}/files/sync",
    response_model=PullRequestFileSyncResponse,
)
async def sync_changed_files(
    pull_request_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    pr_repository = PullRequestRepository(db)

    pull_request = pr_repository.get_by_id(
        pull_request_id
    )

    if pull_request is None:
        raise HTTPException(
            status_code=404,
            detail="Pull request not found",
        )

    service = PullRequestFileService(
        PullRequestFileRepository(db)
    )

    return await service.sync_changed_files(
        current_user,
        pull_request,
    )


@router.get(
    "/{pull_request_id}/files",
    response_model=list[PullRequestFileResponse],
)
def get_changed_files(
    pull_request_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    pr_repository = PullRequestRepository(db)

    pull_request = pr_repository.get_by_id(
        pull_request_id
    )

    if pull_request is None:
        raise HTTPException(
            status_code=404,
            detail="Pull request not found",
        )

    service = PullRequestFileService(
        PullRequestFileRepository(db)
    )

    return service.get_changed_files(
        pull_request
    )