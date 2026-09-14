"""Entités Preuve — EvidenceUnit, Citation, Provenance.

L'EvidenceUnit est la brique du RAG : un passage sourcé, daté, hiérarchisé.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from tropirag.core.enums import SourceAuthority


@dataclass(slots=True)
class SourceRef:
    """Référence d'une source institutionnelle."""

    source_id: str                 # 'who-malaria-2023'
    authority: SourceAuthority
    title: str
    publisher: str                 # 'OMS', 'MSF', 'CDC', 'Ministère de la Santé CI'
    edition_date: str | None = None  # ISO
    url: str | None = None
    jurisdiction: str = "INT"      # INT, CI, SN...
    document_type: str = "guideline"


@dataclass(slots=True)
class EvidenceUnit:
    """Passage clinique autonome, citable, traçable."""

    unit_id: str                    # 'eu-who-malaria-001'
    text: str
    source: SourceRef
    section: str | None = None
    page: int | None = None
    topics: list[str] = field(default_factory=list)   # malaria, dengue, severity...
    diseases: list[str] = field(default_factory=list)
    jurisdiction: str = "INT"
    valid_from: str | None = None
    valid_until: str | None = None
    superseded_by: str | None = None
    language: str = "fr"

    def citation(self) -> str:
        base = f"{self.source.publisher}. {self.source.title}"
        if self.section:
            base += f", section « {self.section} »"
        if self.source.edition_date:
            y = str(self.source.edition_date)[:4]
            base += f" ({y})"
        return base + f" [{self.unit_id}]"

    def is_current(self, ref: date | None = None) -> bool:
        today = ref or date.today()
        if self.superseded_by:
            return False
        if self.valid_from:
            try:
                if date.fromisoformat(str(self.valid_from)[:10]) > today:
                    return False
            except ValueError:
                pass
        if self.valid_until:
            try:
                if date.fromisoformat(str(self.valid_until)[:10]) < today:
                    return False
            except ValueError:
                pass
        return True

    def authority_rank(self) -> int:
        from tropirag.core.enums import AUTHORITY_RANK

        return AUTHORITY_RANK.get(self.source.authority, 9)


@dataclass(slots=True)
class Citation:
    """Citation rendue dans une réponse."""

    marker: str                     # [1]
    unit_id: str
    quote: str                      # extrait exact de l'EvidenceUnit
    full: str                       # citation complète


@dataclass(slots=True)
class EvidencePack:
    """Pack de preuves assemblé pour une requête clinique."""

    query: str
    units: list[EvidenceUnit] = field(default_factory=list)
    scores: dict[str, float] = field(default_factory=dict)  # unit_id → score
    retrieval_mode: str = "hybrid_deterministic"
    created_at: str | None = None
    total_candidates: int = 0

    def top(self, n: int | None = None) -> list[EvidenceUnit]:
        n = n or len(self.units)
        ranked = sorted(self.units, key=lambda u: self.scores.get(u.unit_id, 0.0), reverse=True)
        return ranked[:n]

    def get(self, unit_id: str) -> EvidenceUnit | None:
        for u in self.units:
            if u.unit_id == unit_id:
                return u
        return None

    def empty(self) -> bool:
        return not self.units

    def summary(self) -> str:
        if not self.units:
            return "Aucune preuve récupérée."
        auths = {}
        for u in self.units:
            auths[u.source.authority.value] = auths.get(u.source.authority.value, 0) + 1
        parts = ", ".join(f"{k}×{v}" for k, v in sorted(auths.items()))
        return f"{len(self.units)} unité(s) de preuve — sources : {parts}"
