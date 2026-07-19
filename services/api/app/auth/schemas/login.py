from uuid import UUID

from pydantic import BaseModel


class UserResponse(BaseModel):
    id: UUID
    github_id: int
    username: str
    name: str | None = None
    email: str | None = None
    avatar_url: str | None = None


class LoginResponse(BaseModel):
    message: str
    access_token: str
    token_type: str
    user: UserResponse