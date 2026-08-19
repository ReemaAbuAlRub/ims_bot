"""Data model for a single retrievable piece of document text."""
from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentChunk:
    """One page-sized slice of a source PDF, with citation metadata."""

    text: str
    source_file: str
    page_number: int

    @property
    def citation(self) -> str:
        """Returns the human-readable citation tag for this chunk."""
        return f"{self.source_file}, p.{self.page_number}"

    def to_dict(self) -> dict:
        """Serializes this chunk to a JSON-compatible dict."""
        return {
            "text": self.text,
            "source_file": self.source_file,
            "page_number": self.page_number,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DocumentChunk":
        """Rebuilds a chunk from its serialized dict form."""
        return cls(
            text=data["text"],
            source_file=data["source_file"],
            page_number=data["page_number"],
        )
