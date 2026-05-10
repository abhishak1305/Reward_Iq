"""
Application configuration using Pydantic BaseSettings.
"""

import ast
import json
import secrets
from functools import lru_cache
from pathlib import Path
from typing import Literal, Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ───────────────────────────────────────────────────────────
    APP_NAME: str = "RewardIQ"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False

    # ── Database ──────────────────────────────────────────────────────
    DATABASE_URL: str = "sqlite+aiosqlite:///./rewardiq.db"

    # ── JWT ───────────────────────────────────────────────────────────
    JWT_SECRET_KEY: str = Field(default_factory=lambda: secrets.token_hex(32))
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── CORS ──────────────────────────────────────────────────────────
    # Accepts any of these formats from env vars:
    #   JSON array:          ["https://a.com","https://b.com"]
    #   Python list:         ['https://a.com','https://b.com']
    #   Comma-separated:     https://a.com,https://b.com
    #   Single URL:          https://a.com
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
    ]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v: Any) -> list[str]:
        if isinstance(v, list):
            return v
        if not isinstance(v, str):
            return v
        v = v.strip()
        # 1. Try JSON: ["https://..."]
        try:
            parsed = json.loads(v)
            if isinstance(parsed, list):
                return parsed
        except (json.JSONDecodeError, ValueError):
            pass
        # 2. Try Python literal: ['https://...']
        try:
            parsed = ast.literal_eval(v)
            if isinstance(parsed, list):
                return parsed
        except (ValueError, SyntaxError):
            pass
        # 3. Comma-separated: https://a.com,https://b.com
        if "," in v:
            return [u.strip() for u in v.split(",") if u.strip()]
        # 4. Single URL
        if v.startswith("http"):
            return [v]
        return [v]

    # ── Pagination ────────────────────────────────────────────────────
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # ── AI ────────────────────────────────────────────────────────────
    AI_MODEL_RETRAIN_INTERVAL_HOURS: int = 24
    MIN_TRAINING_SAMPLES: int = 10
    OPENROUTER_API_KEY: str | None = None
    OPENROUTER_MODEL: str = "openai/gpt-oss-120b:free"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
