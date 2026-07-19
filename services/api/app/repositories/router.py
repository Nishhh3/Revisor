from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.model import User
from app.database.dependencies import get_db
from app.repositories.repository import RepositoryRepository
from app.repositories.service import RepositoryService
from app.repositories.schemas import RepositorySyncResponse
from app.repositories.schemas import RepositoryResponse

router = APIRouter(
    prefix="/repositories",
    tags=["Repositories"],
)


@router.post(
    "/sync",
    response_model=RepositorySyncResponse,
    summary="Sync GitHub repositories",
)
async def sync_repositories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    repository = RepositoryRepository(db)

    service = RepositoryService(repository)

    result = await service.sync_repositories(current_user)

    return result

@router.get(
    "",
    response_model=list[RepositoryResponse],
    summary="List repositories",
)
async def get_repositories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    repository = RepositoryRepository(db)

    service = RepositoryService(repository)

    return service.get_repositories(current_user)