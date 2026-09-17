"""
Application configuration loaded from environment variables.
Uses pydantic-settings for type validation and .env support.
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # ── App ────────────────────────────────────────────────────────────────
    APP_NAME: str = "SEAON Manufacturing"
    DEBUG: bool = False
    API_PREFIX: str = "/api"

    # ── Security ───────────────────────────────────────────────────────────
    SECRET_KEY: str = "change-me-in-production-please-use-a-long-random-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # ── Database ───────────────────────────────────────────────────────────
    DATABASE_URL: str = "sqlite:///./seaon.db"

    # ── CORS ───────────────────────────────────────────────────────────────
    CORS_ORIGINS: List[str] = [
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8000",
        "http://localhost:3000",
    ]
    ALLOWED_HOSTS: List[str] = ["*"]

    # ── Default admin (seeded on first run) ────────────────────────────────
    DEFAULT_ADMIN_EMAIL: str = "admin@seaon.com"
    DEFAULT_ADMIN_PASSWORD: str = "admin123"
    DEFAULT_ADMIN_NAME: str = "John Smith"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance (avoids re-parsing .env on every call)."""
    return Settings()


settings = get_settings()