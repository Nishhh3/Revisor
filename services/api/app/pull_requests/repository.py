from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.pull_requests.model import PullRequest


class PullRequestRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_github_pr_id(
        self,
        github_pr_id: int,
    ) -> PullRequest | None:

        return self.db.scalar(
            select(PullRequest).where(
                PullRequest.github_pr_id == github_pr_id
            )
        )

    def get_by_id(
        self,
        pull_request_id: UUID,
    ) -> PullRequest | None:

        return self.db.get(
            PullRequest,
            pull_request_id,
        )

    def list_by_repository(
        self,
        repository_id: UUID,
    ) -> list[PullRequest]:

        return list(
            self.db.scalars(
                select(PullRequest)
                .where(
                    PullRequest.repository_id == repository_id
                )
                .order_by(PullRequest.number.desc())
            ).all()
        )

    def create(
        self,
        pull_request: PullRequest,
    ) -> PullRequest:

        self.db.add(pull_request)
        self.db.commit()
        self.db.refresh(pull_request)

        return pull_request

    def update(
        self,
        pull_request: PullRequest,
    ) -> PullRequest:

        self.db.commit()
        self.db.refresh(pull_request)

        return pull_request