from datetime import datetime

from app.auth.model import User
from app.github.pull_requests.service import GitHubPullRequestService
from app.pull_requests.model import PullRequest
from app.pull_requests.repository import PullRequestRepository
from app.repositories.model import Repository


class PullRequestService:

    def __init__(
        self,
        repository: PullRequestRepository,
    ):
        self.repository = repository
        self.github = GitHubPullRequestService()

    async def sync_pull_requests(
        self,
        user: User,
        repository: Repository,
    ) -> dict:

        github_pull_requests = await self.github.fetch_pull_requests(
            owner=repository.owner,
            repository=repository.name,
            access_token=user.github_access_token,
        )

        created = 0
        updated = 0

        for pr in github_pull_requests:

            existing = self.repository.get_by_github_pr_id(
                pr["id"]
            )

            if existing:

                existing.number = pr["number"]
                existing.title = pr["title"]
                existing.body = pr["body"]
                existing.state = pr["state"]
                existing.draft = pr["draft"]
                existing.merged = pr.get("merged", False)

                existing.author = pr["user"]["login"]

                existing.base_branch = pr["base"]["ref"]
                existing.head_branch = pr["head"]["ref"]

                existing.html_url = pr["html_url"]

                existing.created_at_github = datetime.fromisoformat(
                    pr["created_at"].replace("Z", "+00:00")
                )

                existing.updated_at_github = datetime.fromisoformat(
                    pr["updated_at"].replace("Z", "+00:00")
                )

                existing.closed_at = (
                    datetime.fromisoformat(
                        pr["closed_at"].replace("Z", "+00:00")
                    )
                    if pr["closed_at"]
                    else None
                )

                existing.merged_at = (
                    datetime.fromisoformat(
                        pr["merged_at"].replace("Z", "+00:00")
                    )
                    if pr["merged_at"]
                    else None
                )

                self.repository.update(existing)

                updated += 1

                continue

            pull_request = PullRequest(
                github_pr_id=pr["id"],
                number=pr["number"],
                title=pr["title"],
                body=pr["body"],
                state=pr["state"],
                draft=pr["draft"],
                merged=pr.get("merged", False),

                author=pr["user"]["login"],

                base_branch=pr["base"]["ref"],
                head_branch=pr["head"]["ref"],

                html_url=pr["html_url"],

                created_at_github=datetime.fromisoformat(
                    pr["created_at"].replace("Z", "+00:00")
                ),

                updated_at_github=datetime.fromisoformat(
                    pr["updated_at"].replace("Z", "+00:00")
                ),

                closed_at=(
                    datetime.fromisoformat(
                        pr["closed_at"].replace("Z", "+00:00")
                    )
                    if pr["closed_at"]
                    else None
                ),

                merged_at=(
                    datetime.fromisoformat(
                        pr["merged_at"].replace("Z", "+00:00")
                    )
                    if pr["merged_at"]
                    else None
                ),

                repository_id=repository.id,
            )

            self.repository.create(
                pull_request
            )

            created += 1

        return {
            "total": len(github_pull_requests),
            "created": created,
            "updated": updated,
        }

    def get_pull_requests(
        self,
        repository: Repository,
    ):
        return self.repository.list_by_repository(
            repository.id
        )