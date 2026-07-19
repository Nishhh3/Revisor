from datetime import UTC
from datetime import datetime

from app.auth.model import User
from app.auth.repositories.user_repository import UserRepository


class UserService:

    def __init__(self, repository: UserRepository):
        self.repository = repository

    def get_or_create_user(
        self,
        github_user: dict,
        github_token: dict,
    ) -> User:

        user = self.repository.get_by_github_id(
            github_user["id"]
        )

        if user:
            user.username = github_user["login"]
            user.name = github_user.get("name")
            user.email = github_user.get("email")
            user.avatar_url = github_user["avatar_url"]

            user.github_access_token = github_token["access_token"]
            user.github_token_type = github_token.get(
                "token_type",
                "bearer",
            )
            user.github_scope = github_token.get(
                "scope",
                "",
            )

            user.last_login = datetime.now(UTC)

            return self.repository.update(user)

        user = User(
            github_id=github_user["id"],
            username=github_user["login"],
            name=github_user.get("name"),
            email=github_user.get("email"),
            avatar_url=github_user["avatar_url"],

            github_access_token=github_token["access_token"],
            github_token_type=github_token.get(
                "token_type",
                "bearer",
            ),
            github_scope=github_token.get(
                "scope",
                "",
            ),

            last_login=datetime.now(UTC),
        )

        return self.repository.create(user)