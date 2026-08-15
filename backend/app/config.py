from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "local"
    log_level: str = "info"

    database_url: str = "postgresql://prism:prism@postgres:5432/prism"

    redis_url: str = "redis://redis:6379/0"
    celery_broker_url: str = "redis://redis:6379/1"
    celery_result_backend: str = "redis://redis:6379/2"

    qdrant_url: str = "http://qdrant:6333"
    qdrant_collection: str = "prism_repo_index"

    github_webhook_secret: str = ""
    github_api_token: str = ""

    openai_api_key: str = ""
    groq_api_key: str = ""
    google_api_key: str = ""


settings = Settings()