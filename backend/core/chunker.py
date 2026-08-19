"""Turns loaded PDF pages into citable DocumentChunk objects."""
from backend.models.chunk import DocumentChunk


class DocumentChunker:
    """Builds one chunk per non-empty page, so each chunk maps to one citation."""

    def chunk(self, source_file: str, pages: list[tuple[int, str]]) -> list[DocumentChunk]:
        """Converts (page_number, page_text) pairs into DocumentChunks."""
        return [
            DocumentChunk(text=text.strip(), source_file=source_file, page_number=page_number)
            for page_number, text in pages
            if text.strip()
        ]
