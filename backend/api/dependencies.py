"""FastAPI dependency providers, wired as cached singletons where possible."""
from collections.abc import Iterator
from functools import lru_cache

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.config import get_settings
from backend.core.chat_service import ChatService
from backend.core.conversation_service import ConversationService
from backend.core.embedder import EmbeddingModel
from backend.core.llm_client import ClaudeClient
from backend.core.prompt_builder import PromptBuilder
from backend.core.retriever import Retriever
from backend.core.vector_store import VectorStore
from backend.db.repository import ThreadRepository
from backend.db.session import get_session_factory


@lru_cache
def get_embedder() -> EmbeddingModel:
    """Returns the process-wide embedding model instance."""
    return EmbeddingModel(get_settings().embedding_model)


@lru_cache
def get_vector_store() -> VectorStore:
    """Loads the persisted FAISS index from disk."""
    return VectorStore.load(get_settings().index_dir)


@lru_cache
def get_conversation_service() -> ConversationService:
    """Wires the retriever, prompt builder, and LLM client into one service."""
    settings = get_settings()
    retriever = Retriever(get_embedder(), get_vector_store(), settings.top_k)
    llm_client = ClaudeClient(settings.anthropic_api_key, settings.llm_model, settings.llm_max_tokens)
    return ConversationService(retriever, PromptBuilder(), llm_client)


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
