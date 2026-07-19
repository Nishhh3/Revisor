from urllib.parse import urlencode

from fastapi import APIRouter, Query
from fastapi.responses import RedirectResponse

from app.core.config import settings
from app.github.oauth.service import GitHubOAuthService

from fastapi import Depends
from sqlalchemy.orm import Session

from app.auth.repositories.user_repository import UserRepository
from app.auth.services.user_service import UserService
from app.database.dependencies import get_db
from app.auth.jwt.service import JWTService
from app.auth.schemas.login import LoginResponse


router = APIRouter(
    prefix="/auth/github",
    tags=["GitHub OAuth"],
)

oauth_service = GitHubOAuthService()


@router.get("/login")
async def github_login():

    params = {
        "client_id": settings.github_client_id,
        "scope": "read:user user:email",
    }

    github_url = (
        "https://github.com/login/oauth/authorize?"
        + urlencode(params)
    )

    return RedirectResponse(github_url)


@router.get(
    "/callback",
    response_model=LoginResponse,
    summary="GitHub OAuth Callback",
    description="Authenticates a GitHub user and returns a JWT.",
)
async def github_callback(
    code: str = Query(...),
    db: Session = Depends(get_db),
):
    token = await oauth_service.exchange_code_for_token(code)

    github_user = await oauth_service.get_github_user(
        token["access_token"]
    )

    repository = UserRepository(db)

    service = UserService(repository)

    user = service.get_or_create_user(github_user)

    jwt_service = JWTService()

    access_token = jwt_service.create_access_token(
    str(user.id)
    )

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "Bearer",
        "user": {
            "id": str(user.id),
            "github_id": user.github_id,
            "username": user.username,
            "name": user.name,
            "email": user.email,
            "avatar_url": user.avatar_url,
        },
    }