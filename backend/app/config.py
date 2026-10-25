from pydantic import field_validator
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
    qdrant_api_key: str = ""
    qdrant_collection: str = "prism_repo_index"
    

    github_webhook_secret: str = ""
    github_api_token: str = ""

    openai_api_key: str = ""
    groq_api_key: str = ""
    groq_model: str = "openai/gpt-oss-120b"
    google_api_key: str = ""

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:3b"
    review_model_provider: str = "groq"

    openrouter_api_key: str = ""
    openrouter_model: str = "openrouter/free"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    @field_validator("*", mode="before")
    @classmethod
    def strip_strings(cls, v):
        """Defensive: a stray newline/whitespace in any credential
        (copy-paste artifact) shouldn't silently corrupt every HTTP
        call that uses it -- strip it once, here, for every field."""
        if isinstance(v, str):
            return v.strip()
        return v


settings = Settings()