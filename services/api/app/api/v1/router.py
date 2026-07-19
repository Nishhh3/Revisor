from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.github.oauth.router import router as github_oauth_router
from app.auth.router import router as auth_router

router = APIRouter()

router.include_router(auth_router)

router.include_router(
    health_router,
    tags=["Health"]
)

router.include_router(
    github_oauth_router
)