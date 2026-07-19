from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.github.oauth.router import router as github_oauth_router
from app.auth.router import router as auth_router
from app.repositories.router import router as repository_router
from app.pull_requests.router import router as pull_request_router

router = APIRouter()

router.include_router(auth_router)

router.include_router(
    health_router,
    tags=["Health"]
)

router.include_router(
    github_oauth_router
)

router.include_router(
    repository_router
)

router.include_router(
    pull_request_router
)