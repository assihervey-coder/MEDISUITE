"""Validateur de chunks — barrière qualité avant création d'unités de preuve.

Contrôles (tous déterministes) :
    - bornes de taille (min/max),
    - non-vide après nettoyage,
    - unicité par empreinte SHA-256 (déduplication intra-document),
    - ratio lettres/caractères (exclut les tables numériques brutes),
    - présence minimale de signal clinique (terme du domaine OU section utile).
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

from tropirag.evidence_engine.chunking.clinical_chunker import ClinicalChunk


@dataclass(slots=True)
class ChunkValidation:
    """Verdict de validation d'un lot de chunks."""

    valid: list[ClinicalChunk] = field(default_factory=list)
    rejected: list[tuple[int, str]] = field(default_factory=list)   # (index, motif)

    @property
    def passed(self) -> bool:
        return bool(self.valid)

    def summary(self) -> str:
        return (f"{len(self.valid)} chunk(s) valide(s), "
                f"{len(self.rejected)} rejeté(s)")


class ChunkValidator:
    """Valide les chunks cliniques avant ingestion."""

    def __init__(self, min_chars: int = 80, max_chars: int = 1400,
                 min_letter_ratio: float = 0.55) -> None:
        self.min_chars = min_chars
        self.max_chars = max_chars
        self.min_letter_ratio = min_letter_ratio

    def validate(self, chunks: list[ClinicalChunk]) -> ChunkValidation:
        out = ChunkValidation()
        seen_hashes: set[str] = set()
        for i, chunk in enumerate(chunks):
            text = chunk.text.strip()
            if len(text) < self.min_chars:
                out.rejected.append((i, f"trop court ({len(text)} < {self.min_chars} caractères)"))
                continue
            if len(text) > self.max_chars:
                out.rejected.append((i, f"trop long ({len(text)} > {self.max_chars} caractères)"))
                continue
            letters = sum(c.isalpha() or c.isspace() for c in text)
            if text and letters / len(text) < self.min_letter_ratio:
                out.rejected.append((i, "table numérique brute (ratio lettres insuffisant)"))
                continue
            h = hashlib.sha256(
                f"{chunk.source_id}::{chunk.section_path}::{text}".encode("utf-8")
            ).hexdigest()
            if h in seen_hashes:
                out.rejected.append((i, "doublon (hash identique)"))
                continue
            seen_hashes.add(h)
            has_signal = (bool(chunk.diseases) or bool(chunk.symptom_codes)
                          or bool(chunk.drug_codes) or bool(chunk.test_codes)
                          or chunk.recommendation_strength != "none")
            if not has_signal:
                out.rejected.append((i, "aucun signal clinique (terme/section/recommandation)"))
                continue
            out.valid.append(chunk)
        return out
