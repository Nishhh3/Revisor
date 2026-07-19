from datetime import UTC
from datetime import datetime

from app.auth.model import User
from app.auth.repositories.user_repository import UserRepository


class UserService:

    def __init__(self, repository: UserRepository):
        self.repository = repository

    def get_or_create_user(self, github_user: dict) -> User:

        user = self.repository.get_by_github_id(
            github_user["id"]
        )

        if user:
            user.username = github_user["login"]
            user.name = github_user["name"]
            user.email = github_user["email"]
            user.avatar_url = github_user["avatar_url"]
            user.last_login = datetime.now(UTC)

            return self.repository.update(user)

        user = User(
            github_id=github_user["id"],
            username=github_user["login"],
            name=github_user["name"],
            email=github_user["email"],
            avatar_url=github_user["avatar_url"],
            last_login=datetime.now(UTC),
        )

        return self.repository.create(user)