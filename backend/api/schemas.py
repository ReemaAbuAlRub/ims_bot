"""Request/response models for the chat API."""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class ChatMessageSchema(BaseModel):
    """One stored turn of a conversation."""

    role: Literal["user", "assistant"]
    content: str

    model_config = {"from_attributes": True}


class ThreadSummarySchema(BaseModel):
    """A thread as shown in the sidebar list."""

    id: str
    title: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ThreadDetailSchema(ThreadSummarySchema):
    """A thread together with its full message history."""

    messages: list[ChatMessageSchema]


class CreateThreadRequest(BaseModel):
    """Payload for POST /threads."""

    session_id: str


class ChatRequest(BaseModel):
    """Payload for POST /chat."""

    thread_id: str
    question: str


class ChatResponse(BaseModel):
    """Payload returned from POST /chat."""

    answer: str
