"""Filtres de métadonnées sur les unités de preuve."""
from __future__ import annotations

from tropirag.core.enums import SourceAuthority
from tropirag.domain.evidence.entities import EvidenceUnit


class MetadataFilter:
    """Filtre par autorité, juridiction, validité temporelle."""

    def by_authority(self, units: list[EvidenceUnit],
                     allowed: list[SourceAuthority] | None = None) -> list[EvidenceUnit]:
        if not allowed:
            return units
        allow = {a.value for a in allowed}
        return [u for u in units if u.source.authority.value in allow]

    def by_jurisdiction(self, units: list[EvidenceUnit], jurisdiction: str) -> list[EvidenceUnit]:
        # INT = applicable partout ; sinon correspondance exacte
        return [u for u in units if u.jurisdiction in ("INT", jurisdiction)]

    def current_only(self, units: list[EvidenceUnit]) -> list[EvidenceUnit]:
        return [u for u in units if u.is_current()]

    def by_disease(self, units: list[EvidenceUnit], diseases: list[str]) -> list[EvidenceUnit]:
        if not diseases:
            return units
        dset = set(diseases)
        return [u for u in units if u.diseases and (set(u.diseases) & dset)]
