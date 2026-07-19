import httpx


class GitHubPullRequestService:

    BASE_URL = "https://api.github.com"

    async def fetch_pull_requests(
        self,
        owner: str,
        repository: str,
        access_token: str,
    ) -> list[dict]:

        url = (
            f"{self.BASE_URL}/repos/"
            f"{owner}/{repository}/pulls"
        )

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
        }

        params = {
            "state": "all",
            "per_page": 100,
        }

        async with httpx.AsyncClient() as client:

            response = await client.get(
                url,
                headers=headers,
                params=params,
            )

            response.raise_for_status()

            return response.json()