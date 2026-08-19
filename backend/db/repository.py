"""Data access for chat threads and messages."""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.db.models import MessageRecord, ThreadRecord


class ThreadRepository:
    """CRUD operations over threads and their messages."""

    def __init__(self, session: Session):
        self._session = session

    def list_threads(self, session_id: str) -> list[ThreadRecord]:
        """Returns a session's threads, newest first."""
        statement = (
            select(ThreadRecord)
            .where(ThreadRecord.session_id == session_id)
            .order_by(ThreadRecord.created_at.desc(), ThreadRecord.id.desc())
        )
        return list(self._session.scalars(statement))

    def create_thread(self, session_id: str) -> ThreadRecord:
        """Creates and persists an empty thread for the given session."""
        thread = ThreadRecord(id=str(uuid.uuid4()), session_id=session_id, title="New chat")
        self._session.add(thread)
        self._session.commit()
        return thread

    def get_thread(self, thread_id: str) -> ThreadRecord | None:
        """Returns one thread with its messages loaded, or None if it doesn't exist."""
        return self._session.get(ThreadRecord, thread_id)

    def delete_thread(self, thread_id: str) -> bool:
        """Deletes a thread and its messages, reporting whether it existed."""
        thread = self._session.get(ThreadRecord, thread_id)
        if thread is None:
            return False
        self._session.delete(thread)
        self._session.commit()
        return True

    def add_message(self, thread_id: str, role: str, content: str) -> MessageRecord:
        """Appends a message to a thread."""
        message = MessageRecord(thread_id=thread_id, role=role, content=content)
        self._session.add(message)
        self._session.commit()
        return message

    def set_title(self, thread_id: str, title: str) -> None:
        """Updates a thread's display title."""
        thread = self._session.get(ThreadRecord, thread_id)
        if thread is not None:
            thread.title = title
            self._session.commit()
