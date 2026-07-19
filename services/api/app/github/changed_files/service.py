import httpx


class GitHubChangedFilesService:

    BASE_URL = "https://api.github.com"

    async def fetch_changed_files(
        self,
        owner: str,
        repository: str,
        pull_number: int,
        access_token: str,
    ) -> list[dict]:

        url = (
            f"{self.BASE_URL}/repos/"
            f"{owner}/{repository}/pulls/{pull_number}/files"
        )

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
        }

        async with httpx.AsyncClient() as client:

            response = await client.get(
                url,
                headers=headers,
            )

            response.raise_for_status()

            return response.json()