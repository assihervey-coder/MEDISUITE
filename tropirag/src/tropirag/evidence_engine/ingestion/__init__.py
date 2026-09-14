"""Ingestion documentaire — chargement de sources brutes vers le RAG.

Chaîne : document brut (PDF/HTML/TXT/MD) → RawDocument → normalisation
→ sections → chunks cliniques → unités de preuve (quarantine → validation).

Imports paresseux (PEP 562) pour casser les cycles d'import avec
``normalization`` et ``chunking``.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from tropirag.evidence_engine.ingestion.document_loader import (
        DocumentLoader,
        LoadError,
        RawDocument,
    )
    from tropirag.evidence_engine.ingestion.metadata_extractor import (
        ExtractedMetadata,
        MetadataExtractor,
    )
    from tropirag.evidence_engine.ingestion.pipeline import (
        DocumentIngestionPipeline,
        IngestionReport,
    )

_LAZY = {
    "DocumentLoader": "document_loader",
    "LoadError": "document_loader",
    "RawDocument": "document_loader",
    "ExtractedMetadata": "metadata_extractor",
    "MetadataExtractor": "metadata_extractor",
    "DocumentIngestionPipeline": "pipeline",
    "IngestionReport": "pipeline",
}

__all__ = list(_LAZY)


def __getattr__(name: str):
    if name in _LAZY:
        import importlib

        mod = importlib.import_module(f"{__name__}.{_LAZY[name]}")
        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} n'a pas d'attribut {name!r}")
