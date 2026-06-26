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


settings = Settings()
