"""FAISS-backed similarity index paired with chunk metadata."""
import json
from pathlib import Path

import faiss
import numpy as np

from backend.models.chunk import DocumentChunk

_INDEX_FILE = "chunks.faiss"
_METADATA_FILE = "chunks.json"


class VectorStore:
    """Cosine-similarity search over normalized chunk embeddings."""

    def __init__(self, dimension: int):
        self._index = faiss.IndexFlatIP(dimension)
        self._chunks: list[DocumentChunk] = []

    def add(self, vectors: np.ndarray, chunks: list[DocumentChunk]) -> None:
        """Adds embedded vectors and their matching chunks to the index."""
        self._index.add(vectors)
        self._chunks.extend(chunks)

    def search(self, query_vector: np.ndarray, top_k: int) -> list[DocumentChunk]:
        """Returns the top_k chunks most similar to the query vector."""
        if self._index.ntotal == 0:
            return []
        top_k = min(top_k, self._index.ntotal)
        _, indices = self._index.search(np.expand_dims(query_vector, axis=0), top_k)
        return [self._chunks[i] for i in indices[0] if i != -1]

    def save(self, directory: Path) -> None:
        """Persists the index and chunk metadata to directory."""
        directory.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self._index, str(directory / _INDEX_FILE))
        metadata = [chunk.to_dict() for chunk in self._chunks]
        (directory / _METADATA_FILE).write_text(json.dumps(metadata, ensure_ascii=False, indent=2))

    @classmethod
    def load(cls, directory: Path) -> "VectorStore":
        """Rebuilds a VectorStore from a previously saved directory."""
        index = faiss.read_index(str(directory / _INDEX_FILE))
        metadata = json.loads((directory / _METADATA_FILE).read_text())
        store = cls(dimension=index.d)
        store._index = index
        store._chunks = [DocumentChunk.from_dict(item) for item in metadata]
        return store

    @staticmethod
    def exists(directory: Path) -> bool:
        """Checks whether a persisted index is present at directory."""
        return (directory / _INDEX_FILE).exists() and (directory / _METADATA_FILE).exists()
