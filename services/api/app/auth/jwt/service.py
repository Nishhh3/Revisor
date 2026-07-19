from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt

from app.core.config import settings


class JWTService:

    def create_access_token(self, user_id: str) -> str:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.access_token_expire_minutes
        )

        payload = {
            "sub": user_id,
            "exp": expire,
        }

        return jwt.encode(
            payload,
            settings.secret_key,
            algorithm=settings.algorithm,
        )

    def verify_token(self, token: str) -> dict | None:
        try:
            return jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.algorithm],
            )
        except JWTError:
            return None