"""Wraps a local multilingual sentence-embedding model."""
import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    """Embeds text with an E5-family multilingual model (Arabic + English)."""

    def __init__(self, model_name: str):
        self._model = SentenceTransformer(model_name)

    @property
    def dimension(self) -> int:
        """Returns the embedding vector size produced by this model."""
        return self._model.get_embedding_dimension()

    def embed_passages(self, texts: list[str]) -> np.ndarray:
        """Embeds document chunks for indexing, using the E5 'passage:' prefix."""
        return self._encode([f"passage: {text}" for text in texts])

    def embed_query(self, text: str) -> np.ndarray:
        """Embeds a user query for search, using the E5 'query:' prefix."""
        return self._encode([f"query: {text}"])[0]

    def _encode(self, texts: list[str]) -> np.ndarray:
        return self._model.encode(
            texts, normalize_embeddings=True, convert_to_numpy=True
        ).astype("float32")
