"""FastAPI application entrypoint: uvicorn backend.main:app"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.api.dependencies import get_embedder
from backend.api.routes import router
from backend.config import get_settings
from backend.core.chunker import DocumentChunker
from backend.core.document_loader import PDFLoader
from backend.core.index_builder import IndexBuilder
from backend.core.vector_store import VectorStore
from backend.db.session import init_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Creates database tables and builds the vector index if either is missing."""
    settings = get_settings()
    init_database()
    if not VectorStore.exists(settings.index_dir):
        builder = IndexBuilder(PDFLoader(), DocumentChunker(), get_embedder())
        builder.build(settings.artifacts_dir, settings.index_dir)
    yield


def create_app() -> FastAPI:
    """Builds and configures the FastAPI application."""
    app = FastAPI(title="Almamlaka TV Chatbot API", lifespan=lifespan)
    app.include_router(router)
    return app

app = create_app()
