"""CLI entrypoint to (re)build the vector index: python -m backend.scripts.ingest"""
from backend.config import get_settings
from backend.core.chunker import DocumentChunker
from backend.core.document_loader import PDFLoader
from backend.core.embedder import EmbeddingModel
from backend.core.index_builder import IndexBuilder


def main() -> None:
    """Rebuilds the FAISS index from the configured artifacts directory."""
    settings = get_settings()
    builder = IndexBuilder(
        loader=PDFLoader(),
        chunker=DocumentChunker(),
        embedder=EmbeddingModel(settings.embedding_model),
    )
    builder.build(settings.artifacts_dir, settings.index_dir)
    print(f"Index built at {settings.index_dir}")


if __name__ == "__main__":
    main()
