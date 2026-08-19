"""Data model for a single turn in a chat conversation."""
from dataclasses import dataclass
from enum import Enum


class Role(str, Enum):
    """Speaker role for a chat message."""

    USER = "user"
    ASSISTANT = "assistant"


@dataclass(frozen=True)
class ChatMessage:
    """One turn of conversation history."""

    role: Role
    content: str
