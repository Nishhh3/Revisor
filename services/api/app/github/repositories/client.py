import httpx


class GitHubRepositoryClient:

    BASE_URL = "https://api.github.com"

    async def get_repositories(
        self,
        access_token: str,
    ):

        async with httpx.AsyncClient() as client:

            response = await client.get(
                f"{self.BASE_URL}/user/repos",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                },
            )

        response.raise_for_status()

        return response.json()