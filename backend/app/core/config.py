"""
Core configuration module.

Reads values from .env file via pydantic-settings.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# .env lives one level above the backend/ directory
_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_name: str = "Library Management System"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "production"

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    database_url: str = "sqlite+aiosqlite:///./library.db"

    borrowing_period_days: int = 14      # default loan period
    max_renewals: int = 2                # maximum number of renewals per borrowing
    fine_per_day: float = 5000.0         # fine in VND per overdue day
    max_active_borrowings: int = 5       # max concurrent borrowings per user

    admin_username: str = "admin"
    admin_email: str = "admin@library.local"
    admin_password: str = "Admin@123456"
    admin_full_name: str = "System Administrator"

    allowed_origins: List[str] = ["http://localhost:3000"]

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [origin.strip() for origin in v.split(",")]
        return v


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings singleton."""
    return Settings()
