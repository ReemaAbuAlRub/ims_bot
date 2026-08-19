"""Extracts per-page text from PDF files."""
from pathlib import Path

from pypdf import PdfReader


class PDFLoader:
    """Reads a PDF and returns its text broken down by page."""

    def load(self, pdf_path: Path) -> list[tuple[int, str]]:
        """Returns a list of (1-indexed page_number, page_text) tuples."""
        reader = PdfReader(str(pdf_path))
        return [
            (page_number, page.extract_text() or "")
            for page_number, page in enumerate(reader.pages, start=1)
        ]
