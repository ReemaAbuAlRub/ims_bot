"""Builds the expensive, process-wide service objects.

Framework-agnostic on purpose: both the FastAPI layer and the in-process Streamlit
client build their services from here, so neither depends on the other.
"""
from functools import lru_cache

from backend.config import get_settings
from backend.core.chunker import DocumentChunker
from backend.core.conversation_service import ConversationService
from backend.core.document_loader import PDFLoader
from backend.core.embedder import EmbeddingModel
from backend.core.index_builder import IndexBuilder
from backend.core.llm_client import ClaudeClient
from backend.core.prompt_builder import PromptBuilder
from backend.core.retriever import Retriever
from backend.core.vector_store import VectorStore


@lru_cache
def get_embedder() -> EmbeddingModel:
    """Returns the process-wide embedding model instance."""
    return EmbeddingModel(get_settings().embedding_model)


@lru_cache
def get_vector_store() -> VectorStore:
    """Loads the FAISS index, building it from the PDFs first if it is missing."""
    settings = get_settings()
    if not VectorStore.exists(settings.index_dir):
        builder = IndexBuilder(PDFLoader(), DocumentChunker(), get_embedder())
        builder.build(settings.artifacts_dir, settings.index_dir)
    return VectorStore.load(settings.index_dir)


@lru_cache
def get_conversation_service() -> ConversationService:
    """Wires the retriever, prompt builder, and LLM client into one service."""
    settings = get_settings()
    retriever = Retriever(get_embedder(), get_vector_store(), settings.top_k)
    llm_client = ClaudeClient(settings.anthropic_api_key, settings.llm_model, settings.llm_max_tokens)
    return ConversationService(retriever, PromptBuilder(), llm_client)
