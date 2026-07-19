from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.pull_request_files.model import PullRequestFile


class PullRequestFileRepository:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def get_by_sha(
        self,
        github_file_sha: str,
    ) -> PullRequestFile | None:

        return self.db.scalar(
            select(PullRequestFile).where(
                PullRequestFile.github_file_sha == github_file_sha
            )
        )

    def get_by_id(
        self,
        file_id: UUID,
    ) -> PullRequestFile | None:

        return self.db.get(
            PullRequestFile,
            file_id,
        )

    def list_by_pull_request(
        self,
        pull_request_id: UUID,
    ) -> list[PullRequestFile]:

        return list(
            self.db.scalars(
                select(PullRequestFile)
                .where(
                    PullRequestFile.pull_request_id == pull_request_id
                )
                .order_by(
                    PullRequestFile.filename
                )
            ).all()
        )

    def create(
        self,
        file: PullRequestFile,
    ) -> PullRequestFile:

        self.db.add(file)
        self.db.commit()
        self.db.refresh(file)

        return file

    def update(
        self,
        file: PullRequestFile,
    ) -> PullRequestFile:

        self.db.commit()
        self.db.refresh(file)

        return file