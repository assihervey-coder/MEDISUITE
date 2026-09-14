"""Validation d'un EvidencePack avant consommation par la synthèse."""
from __future__ import annotations

from dataclasses import dataclass

from tropirag.domain.evidence.entities import EvidencePack
from tropirag.core.enums import SourceAuthority


@dataclass(slots=True)
class PackValidation:
    passed: bool
    reason: str = ""
    min_authority: str | None = None


def validate_pack(pack: EvidencePack, min_units: int = 1,
                  min_authority: SourceAuthority = SourceAuthority.SCIENTIFIC) -> PackValidation:
    if len(pack.units) < min_units:
        return PackValidation(False, f"{len(pack.units)} unités < {min_units} requis")
    ranks = [u.authority_rank() for u in pack.units]
    best = min(ranks)
    if best > AUTHORITY_RANK_LIMIT.get(min_authority, 4):
        return PackValidation(False, "aucune source d'autorité suffisante dans le pack")
    return PackValidation(True, min_authority=None)


AUTHORITY_RANK_LIMIT = {
    SourceAuthority.WHO: 1, SourceAuthority.NATIONAL: 2, SourceAuthority.MSF: 2,
    SourceAuthority.CDC: 2, SourceAuthority.INSTITUTIONAL: 3,
    SourceAuthority.SCIENTIFIC: 4,
}
