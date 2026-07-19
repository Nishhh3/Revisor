from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.repositories.model import Repository


class RepositoryRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(
        self,
        repository_id: UUID,
    ) -> Repository | None:

        return self.db.get(
            Repository,
            repository_id,
        )

    def get_by_github_repo_id(
        self,
        github_repo_id: int,
    ) -> Repository | None:

        statement = (
            select(Repository)
            .where(
                Repository.github_repo_id == github_repo_id
            )
        )

        return self.db.scalar(statement)

    def create(
        self,
        repository: Repository,
    ) -> Repository:

        self.db.add(repository)
        self.db.commit()
        self.db.refresh(repository)

        return repository

    def update(
        self,
        repository: Repository,
    ) -> Repository:

        self.db.commit()
        self.db.refresh(repository)

        return repository

    def list_all_by_owner(
        self,
        owner_id: str,
    ) -> list[Repository]:

        statement = (
            select(Repository)
            .where(
                Repository.owner_id == owner_id
            )
            .order_by(
                Repository.name
            )
        )

        return list(
            self.db.scalars(statement)
        )