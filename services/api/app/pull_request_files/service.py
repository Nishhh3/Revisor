from app.auth.model import User
from app.github.changed_files.service import GitHubChangedFilesService
from app.pull_request_files.model import PullRequestFile
from app.pull_request_files.repository import PullRequestFileRepository
from app.pull_requests.model import PullRequest


class PullRequestFileService:

    def __init__(
        self,
        repository: PullRequestFileRepository,
    ):
        self.repository = repository
        self.github = GitHubChangedFilesService()

    async def sync_changed_files(
        self,
        user: User,
        pull_request: PullRequest,
    ) -> dict:

        github_files = await self.github.fetch_changed_files(
            owner=pull_request.repository.owner,
            repository=pull_request.repository.name,
            pull_number=pull_request.number,
            access_token=user.github_access_token,
        )

        created = 0
        updated = 0

        for file in github_files:

            existing = self.repository.get_by_sha(
                file["sha"]
            )

            if existing:

                existing.filename = file["filename"]
                existing.status = file["status"]

                existing.additions = file["additions"]
                existing.deletions = file["deletions"]
                existing.changes = file["changes"]

                existing.patch = file.get("patch")

                existing.blob_url = file.get("blob_url")
                existing.raw_url = file.get("raw_url")
                existing.contents_url = file.get("contents_url")

                self.repository.update(existing)

                updated += 1

                continue

            changed_file = PullRequestFile(
                github_file_sha=file["sha"],

                filename=file["filename"],
                status=file["status"],

                additions=file["additions"],
                deletions=file["deletions"],
                changes=file["changes"],

                patch=file.get("patch"),

                blob_url=file.get("blob_url"),
                raw_url=file.get("raw_url"),
                contents_url=file.get("contents_url"),

                pull_request_id=pull_request.id,
            )

            self.repository.create(
                changed_file
            )

            created += 1

        return {
            "total": len(github_files),
            "created": created,
            "updated": updated,
        }

    def get_changed_files(
        self,
        pull_request: PullRequest,
    ):
        return self.repository.list_by_pull_request(
            pull_request.id
        )