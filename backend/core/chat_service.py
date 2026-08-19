"""Persists a chat turn and returns the grounded answer for it."""
from backend.core.conversation_service import ConversationService
from backend.db.repository import ThreadRepository
from backend.models.message import ChatMessage, Role

_MAX_TITLE_LENGTH = 40
_DEFAULT_TITLE = "New chat"


class ThreadNotFoundError(Exception):
    """Raised when a chat turn targets a thread that does not exist."""


class ChatService:
    """Loads history, delegates answering, and stores both sides of the turn."""

    def __init__(
        self,
        repository: ThreadRepository,
        conversation_service: ConversationService,
        max_history_turns: int,
    ):
        self._repository = repository
        self._conversation_service = conversation_service
        self._max_history_turns = max_history_turns

    def answer(self, thread_id: str, question: str) -> str:
        """Answers a question in a thread, persisting the user turn and the reply."""
        thread = self._repository.get_thread(thread_id)
        if thread is None:
            raise ThreadNotFoundError(thread_id)

        history = self._recent_history(thread.messages)
        self._repository.add_message(thread_id, Role.USER.value, question)
        if thread.title == _DEFAULT_TITLE:
            self._repository.set_title(thread_id, self._derive_title(question))

        answer = self._conversation_service.answer(question, history)
        self._repository.add_message(thread_id, Role.ASSISTANT.value, answer)
        return answer

    def _recent_history(self, messages: list) -> list[ChatMessage]:
        """Converts stored messages to domain objects, capping how far back we go."""
        recent = messages[-self._max_history_turns:] if self._max_history_turns else messages
        return [ChatMessage(Role(message.role), message.content) for message in recent]

    def _derive_title(self, first_message: str) -> str:
        """Builds a short thread title from the first user message."""
        single_line = " ".join(first_message.split())
        if len(single_line) <= _MAX_TITLE_LENGTH:
            return single_line
        return single_line[:_MAX_TITLE_LENGTH].rstrip() + "…"
