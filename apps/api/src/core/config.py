from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    PROJECT_NAME: str = "bg-removal"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    CORS_ORIGINS: list[str] = ["*"]

    REDIS_URL: str = "redis://redis:6379/0"
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"

    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    MAX_FILE_SIZE: int = 10 * 1024 * 1024

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: object) -> list[str]:
        if isinstance(v, str):
            return [x.strip() for x in v.split(",")]
        if isinstance(v, list):
            return v
        return [str(v)]


settings = Settings()
