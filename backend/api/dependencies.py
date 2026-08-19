"""FastAPI dependency providers for the HTTP layer."""
from collections.abc import Iterator
from functools import lru_cache

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.config import get_settings
from backend.core.chat_service import ChatService
from backend.core.factory import get_conversation_service
from backend.db.repository import ThreadRepository
from backend.db.session import get_session_factory


def get_db_session() -> Iterator[Session]:
    """Yields a per-request database session."""
    with get_session_factory()() as session:
        yield session


def get_thread_repository(session: Session = Depends(get_db_session)) -> ThreadRepository:
    """Returns a repository bound to the current request's session."""
    return ThreadRepository(session)


def get_chat_service(
    repository: ThreadRepository = Depends(get_thread_repository),
) -> ChatService:
    """Combines per-request persistence with the cached answering pipeline."""
    return ChatService(repository, get_conversation_service(), get_settings().max_history_turns)
