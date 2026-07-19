from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth.jwt.service import JWTService
from app.auth.repositories.user_repository import UserRepository
from app.database.dependencies import get_db

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    jwt_service = JWTService()

    payload = jwt_service.verify_token(credentials.credentials)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )

    repository = UserRepository(db)

    user = repository.get_by_id(payload["sub"])

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )

    return user