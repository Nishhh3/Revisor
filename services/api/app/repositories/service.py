from datetime import datetime

from app.auth.model import User
from app.github.repositories.service import GitHubRepositoryService
from app.repositories.model import Repository
from app.repositories.repository import RepositoryRepository


class RepositoryService:

    def __init__(
        self,
        repository: RepositoryRepository,
    ):
        self.repository = repository
        self.github = GitHubRepositoryService()

    async def sync_repositories(
        self,
        user: User,
    ) -> dict:

        github_repositories = await self.github.fetch_repositories(
            user.github_access_token
        )

        created = 0
        updated = 0

        for repo in github_repositories:

            existing = self.repository.get_by_github_repo_id(
                repo["id"]
            )

            if existing:

                existing.owner = repo["owner"]["login"]
                existing.name = repo["name"]
                existing.full_name = repo["full_name"]
                existing.description = repo["description"]
                existing.private = repo["private"]
                existing.default_branch = repo["default_branch"]
                existing.html_url = repo["html_url"]
                existing.clone_url = repo["clone_url"]

                existing.language = repo["language"]
                existing.stargazers_count = repo["stargazers_count"]
                existing.forks_count = repo["forks_count"]
                existing.watchers_count = repo["watchers_count"]
                existing.open_issues_count = repo["open_issues_count"]
                existing.size = repo["size"]
                existing.visibility = repo["visibility"]

                existing.created_at_github = datetime.fromisoformat(
                    repo["created_at"].replace("Z", "+00:00")
                )

                existing.updated_at_github = datetime.fromisoformat(
                    repo["updated_at"].replace("Z", "+00:00")
                )

                existing.pushed_at = datetime.fromisoformat(
                    repo["pushed_at"].replace("Z", "+00:00")
                )

                self.repository.update(existing)

                updated += 1

                continue

            repository = Repository(
                github_repo_id=repo["id"],
                owner=repo["owner"]["login"],
                name=repo["name"],
                full_name=repo["full_name"],
                description=repo["description"],
                private=repo["private"],
                default_branch=repo["default_branch"],
                html_url=repo["html_url"],
                clone_url=repo["clone_url"],

                language=repo["language"],
                stargazers_count=repo["stargazers_count"],
                forks_count=repo["forks_count"],
                watchers_count=repo["watchers_count"],
                open_issues_count=repo["open_issues_count"],
                size=repo["size"],
                visibility=repo["visibility"],

                created_at_github=datetime.fromisoformat(
                    repo["created_at"].replace("Z", "+00:00")
                ),
                updated_at_github=datetime.fromisoformat(
                    repo["updated_at"].replace("Z", "+00:00")
                ),
                pushed_at=datetime.fromisoformat(
                    repo["pushed_at"].replace("Z", "+00:00")
                ),

                owner_id=user.id,
            )

            self.repository.create(repository)

            created += 1

        return {
            "total": len(github_repositories),
            "created": created,
            "updated": updated,
        }

    def get_repositories(
        self,
        user: User,
    ):
        return self.repository.list_all_by_owner(
            user.id
        )