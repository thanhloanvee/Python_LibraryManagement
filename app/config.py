"""
app/config.py — Pydantic Settings.
All values can be overridden via environment variables or the .env file.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ── App ───────────────────────────────────────────────────
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "dev-secret-key-replace-in-production"

    # ── Database ──────────────────────────────────────────────
    DATABASE_URL: str = "sqlite:///./library.db"

    # ── JWT ───────────────────────────────────────────────────
    JWT_SECRET_KEY: str = "dev-jwt-secret-replace-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRES_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRES_DAYS: int = 30

    # ── Business rules ────────────────────────────────────────
    MAX_BORROW_LIMIT: int = 5
    BORROW_PERIOD_DAYS: int = 14
    FINE_PER_DAY: float = 1.00

    # ── Logging ───────────────────────────────────────────────
    LOG_LEVEL: str = "DEBUG"
    LOG_FILE: str = "logs/app.log"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (reads .env once)."""
    return Settings()
