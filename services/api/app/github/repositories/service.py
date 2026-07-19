import httpx


class GitHubRepositoryService:
    BASE_URL = "https://api.github.com"

    async def fetch_repositories(
        self,
        access_token: str,
    ) -> list[dict]:

        async with httpx.AsyncClient() as client:

            response = await client.get(
                f"{self.BASE_URL}/user/repos",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                },
                params={
                    "per_page": 100,
                    "sort": "updated",
                },
            )

        response.raise_for_status()

        return response.json()