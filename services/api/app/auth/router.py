from fastapi import APIRouter
from fastapi import Depends

from app.auth.dependencies import get_current_user
from app.auth.model import User
from app.auth.schemas.login import UserResponse

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Current User",
    description="Returns the authenticated user's profile.",
)
async def me(
    current_user: User = Depends(get_current_user),
):
    return {
        "id": str(current_user.id),
        "github_id": current_user.github_id,
        "username": current_user.username,
        "name": current_user.name,
        "email": current_user.email,
        "avatar_url": current_user.avatar_url,
    }


@router.post("/logout")
async def logout():
    return {
        "message": "Logged out successfully"
    }


@router.post("/refresh")
async def refresh():
    return {
        "message": "Refresh token support coming soon"
    }