"""Builds the FAISS index from the PDFs in artifacts/."""
from pathlib import Path

from backend.core.chunker import DocumentChunker
from backend.core.document_loader import PDFLoader
from backend.core.embedder import EmbeddingModel
from backend.core.vector_store import VectorStore


class IndexBuilder:
    """Runs load -> chunk -> embed -> persist over every PDF in artifacts_dir."""

    def __init__(self, loader: PDFLoader, chunker: DocumentChunker, embedder: EmbeddingModel):
        self._loader = loader
        self._chunker = chunker
        self._embedder = embedder

    def build(self, artifacts_dir: Path, index_dir: Path) -> None:
        """Ingests every PDF in artifacts_dir and saves the index to index_dir."""
        store = VectorStore(dimension=self._embedder.dimension)
        for pdf_path in sorted(artifacts_dir.glob("*.pdf")):
            chunks = self._chunker.chunk(pdf_path.name, self._loader.load(pdf_path))
            if chunks:
                vectors = self._embedder.embed_passages([chunk.text for chunk in chunks])
                store.add(vectors, chunks)
        store.save(index_dir)
