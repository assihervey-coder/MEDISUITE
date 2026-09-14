"""Schéma API preuves."""
from __future__ import annotations

from pydantic import BaseModel


class EvidenceQueryIn(BaseModel):
    query: str
    diseases: list[str] | None = None
    top_k: int = 5
