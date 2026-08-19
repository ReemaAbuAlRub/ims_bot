"""Turns a user question, plus recent context, into relevant chunks."""
from backend.core.embedder import EmbeddingModel
from backend.core.vector_store import VectorStore
from backend.models.chunk import DocumentChunk
from backend.models.message import ChatMessage, Role


class Retriever:
    """Retrieves top-k chunks across all documents for a query."""

    def __init__(self, embedder: EmbeddingModel, store: VectorStore, top_k: int):
        self._embedder = embedder
        self._store = store
        self._top_k = top_k

    def retrieve(self, question: str, history: list[ChatMessage]) -> list[DocumentChunk]:
        """Embeds the (context-expanded) question and searches the vector store."""
        expanded_query = self._expand_with_last_user_turn(question, history)
        query_vector = self._embedder.embed_query(expanded_query)
        return self._store.search(query_vector, self._top_k)

    def _expand_with_last_user_turn(self, question: str, history: list[ChatMessage]) -> str:
        """Prepends the previous user turn so follow-ups retrieve the right topic."""
        previous_user_turns = [m.content for m in history if m.role == Role.USER]
        if not previous_user_turns:
            return question
        return f"{previous_user_turns[-1]} {question}"
