"""FastAPI application entrypoint: uvicorn backend.main:app"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.api.routes import router
from backend.core.factory import get_vector_store
from backend.db.session import init_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Creates database tables and loads (building if needed) the vector index."""
    init_database()
    get_vector_store()
    yield


def create_app() -> FastAPI:
    """Builds and configures the FastAPI application."""
    app = FastAPI(title="Almamlaka TV Chatbot API", lifespan=lifespan)
    app.include_router(router)
    return app


app = create_app()
