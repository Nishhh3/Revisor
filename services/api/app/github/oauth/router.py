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


@router.get("/callback")
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

    return {
        "message": "Login successful",
        "user": {
            "id": str(user.id),
            "github_id": user.github_id,
            "username": user.username,
            "name": user.name,
            "email": user.email,
            "avatar_url": user.avatar_url,
        },
    }