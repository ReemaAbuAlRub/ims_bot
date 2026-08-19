"""Database engine, session factory, and schema creation."""
from functools import lru_cache
from pathlib import Path

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.config import get_settings
from backend.db.models import Base


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """Returns the process-wide engine, pre-pinging so idle Neon connections recover."""
    settings = get_settings()
    url = settings.database_url
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, pool_pre_ping=True, connect_args=connect_args)


@lru_cache(maxsize=1)
def get_session_factory() -> sessionmaker[Session]:
    """Returns the process-wide session factory."""
    return sessionmaker(bind=get_engine(), expire_on_commit=False)


def init_database() -> None:
    """Creates any missing tables; safe to call on every startup."""
    settings = get_settings()
    if settings.database_url.startswith("sqlite:///"):
        sqlite_path = settings.database_url.removeprefix("sqlite:///")
        Path(sqlite_path).parent.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(get_engine())
