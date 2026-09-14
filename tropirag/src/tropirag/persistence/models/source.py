"""Table ORM `sources` — registre SQL des sources institutionnelles du corpus."""
from __future__ import annotations

from tropirag.persistence.models.base import Column

SOURCE_TABLE = "sources"

SOURCE_COLUMNS = [
    Column("source_id", "TEXT", primary_key=True),
    Column("authority", "TEXT", nullable=False, index=True),
    Column("title", "TEXT"),
    Column("publisher", "TEXT"),
    Column("edition_date", "TEXT", index=True),
    Column("jurisdiction", "TEXT", index=True),
    Column("url", "TEXT"),
    Column("document_type", "TEXT", default="guideline"),
]


def row_from_source(source_id: str, meta: dict) -> dict:
    """métadonnées YAML de source → ligne sources."""
    return {
        "source_id": source_id,
        "authority": meta.get("authority", "unknown"),
        "title": meta.get("title", source_id),
        "publisher": meta.get("publisher", source_id),
        "edition_date": meta.get("edition_date"),
        "jurisdiction": meta.get("jurisdiction", "INT"),
        "url": meta.get("url"),
        "document_type": meta.get("document_type", "guideline"),
    }


def to_domain(row) -> dict:
    return dict(row)
