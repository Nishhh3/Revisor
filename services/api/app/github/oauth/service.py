import httpx

from app.core.config import settings


class GitHubOAuthService:

    TOKEN_URL = "https://github.com/login/oauth/access_token"

    USER_URL = "https://api.github.com/user"

    EMAIL_URL = "https://api.github.com/user/emails"

    async def exchange_code_for_token(self, code: str) -> dict:

        async with httpx.AsyncClient(timeout=30.0) as client:

            response = await client.post(
                self.TOKEN_URL,
                headers={
                    "Accept": "application/json",
                },
                data={
                    "client_id": settings.github_client_id,
                    "client_secret": settings.github_client_secret,
                    "code": code,
                },
            )

        response.raise_for_status()

        return response.json()
    
    async def get_github_user(self, access_token: str) -> dict:

        async with httpx.AsyncClient(timeout=30.0) as client:

            response = await client.get(
                self.USER_URL,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json",
                },
            )

        response.raise_for_status()

        return response.json()