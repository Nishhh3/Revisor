from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PRISM API"
    app_version: str = "0.1.0"

    environment: str = "development"
    debug: bool = True

    api_host: str = "127.0.0.1"
    api_port: int = 8000

    frontend_url: str = "http://localhost:3000"

    database_url: str

    secret_key: str
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()