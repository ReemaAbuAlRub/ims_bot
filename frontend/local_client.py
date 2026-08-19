"""In-process backend client, used when the app runs as a single deployment.

Mirrors BackendClient's interface but calls the backend package directly instead of
over HTTP, so the whole app can run as one Streamlit process. The backend package
itself stays free of any Streamlit or frontend imports.
"""
from backend.config import get_settings
from backend.core.chat_service import ChatService
from backend.core.factory import get_conversation_service
from backend.db.repository import ThreadRepository
from backend.db.session import get_session_factory, init_database


class LocalBackendClient:
    """Calls backend services directly, one database session per operation."""

    def __init__(self):
        init_database()
        self._session_factory = get_session_factory()

    def list_threads(self, session_id: str) -> list[dict]:
        """Returns the session's threads, newest first."""
        with self._session_factory() as session:
            threads = ThreadRepository(session).list_threads(session_id)
            return [self._thread_summary(thread) for thread in threads]

    def create_thread(self, session_id: str) -> dict:
        """Creates a new empty thread for the session."""
        with self._session_factory() as session:
            return self._thread_summary(ThreadRepository(session).create_thread(session_id))

    def get_thread(self, thread_id: str) -> dict:
        """Returns one thread including its stored messages."""
        with self._session_factory() as session:
            thread = ThreadRepository(session).get_thread(thread_id)
            if thread is None:
                raise KeyError(thread_id)
            summary = self._thread_summary(thread)
            summary["messages"] = [
                {"role": message.role, "content": message.content} for message in thread.messages
            ]
            return summary

    def delete_thread(self, thread_id: str) -> None:
        """Deletes a thread and its messages."""
        with self._session_factory() as session:
            ThreadRepository(session).delete_thread(thread_id)

    def send_message(self, thread_id: str, question: str) -> str:
        """Answers a question in a thread, persisting both sides of the turn."""
        settings = get_settings()
        with self._session_factory() as session:
            service = ChatService(
                ThreadRepository(session), get_conversation_service(), settings.max_history_turns
            )
            return service.answer(thread_id, question)

    def _thread_summary(self, thread) -> dict:
        """Converts a thread record into the same dict shape the HTTP API returns."""
        return {
            "id": thread.id,
            "title": thread.title,
            "created_at": thread.created_at.isoformat() if thread.created_at else None,
        }
