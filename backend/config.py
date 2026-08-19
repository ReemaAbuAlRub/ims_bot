"""Centralized backend configuration read from environment variables."""
from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
_SQLITE_FALLBACK_URL = f"sqlite:///{BACKEND_DIR / 'data' / 'chat.db'}"


class Settings(BaseSettings):
    """Typed application settings, loaded from env vars / a .env file."""

    anthropic_api_key: str
    database_url: str = _SQLITE_FALLBACK_URL
    max_history_turns: int = 12
    llm_model: str = "claude-sonnet-5"
    embedding_model: str = "intfloat/multilingual-e5-base"
    llm_max_tokens: int = 1024
    top_k: int = 8

    artifacts_dir: Path = PROJECT_ROOT / "artifacts"
    index_dir: Path = BACKEND_DIR / "index"

    @field_validator("database_url")
    @classmethod
    def _fall_back_when_blank(cls, value: str) -> str:
        """Treats an empty DATABASE_URL the same as an unset one."""
        return value.strip() or _SQLITE_FALLBACK_URL

    class Config:
        env_file = PROJECT_ROOT / ".env"


@lru_cache
def get_settings() -> Settings:
    """Returns a process-wide cached Settings instance."""
    return Settings()
