"""HTTP routes for the chat API."""
from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.api.dependencies import get_chat_service, get_thread_repository
from backend.api.schemas import (
    ChatRequest,
    ChatResponse,
    CreateThreadRequest,
    ThreadDetailSchema,
    ThreadSummarySchema,
)
from backend.core.chat_service import ChatService, ThreadNotFoundError
from backend.db.repository import ThreadRepository

router = APIRouter()


@router.get("/health")
def health() -> dict:
    """Liveness check."""
    return {"status": "ok"}


@router.get("/threads", response_model=list[ThreadSummarySchema])
def list_threads(
    session_id: str = Query(..., min_length=1),
    repository: ThreadRepository = Depends(get_thread_repository),
) -> list[ThreadSummarySchema]:
    """Lists a session's threads, newest first."""
    return repository.list_threads(session_id)


@router.post("/threads", response_model=ThreadSummarySchema, status_code=status.HTTP_201_CREATED)
def create_thread(
    request: CreateThreadRequest,
    repository: ThreadRepository = Depends(get_thread_repository),
) -> ThreadSummarySchema:
    """Creates an empty thread for a session."""
    return repository.create_thread(request.session_id)


@router.get("/threads/{thread_id}", response_model=ThreadDetailSchema)
def get_thread(
    thread_id: str,
    repository: ThreadRepository = Depends(get_thread_repository),
) -> ThreadDetailSchema:
    """Returns one thread with its full message history."""
    thread = repository.get_thread(thread_id)
    if thread is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thread not found")
    return thread


@router.delete("/threads/{thread_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_thread(
    thread_id: str,
    repository: ThreadRepository = Depends(get_thread_repository),
) -> None:
    """Deletes a thread and all of its messages."""
    if not repository.delete_thread(thread_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thread not found")


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    """Answers a question in a thread, persisting both sides of the turn."""
    try:
        answer = service.answer(request.thread_id, request.question)
    except ThreadNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thread not found")
    return ChatResponse(answer=answer)
