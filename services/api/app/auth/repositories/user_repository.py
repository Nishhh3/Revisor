from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.model import User


class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_github_id(self, github_id: int) -> User | None:
        return self.db.scalar(
            select(User).where(User.github_id == github_id)
        )

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User) -> User:
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_by_id(self, user_id: str) -> User | None:
     return self.db.get(User, user_id)
