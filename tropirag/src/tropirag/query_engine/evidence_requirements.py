"""Exigences de preuve par intention — contrôle de suffisance du pack.

Chaque intention a un contrat minimal : nombre d'unités, autorités admises.
Si le pack assemblé ne satisfait pas le contrat, la synthèse IA est
refusée — le doute bénéficie au patient.
"""
from __future__ import annotations

from dataclasses import dataclass

REQUIREMENTS = {
    "clinical_analysis": {"min_units": 1, "authority": ["who", "national", "msf", "cdc"]},
    "drug_check": {"min_units": 1, "authority": ["who", "national", "msf", "cdc", "institutional"]},
    "info": {"min_units": 1, "authority": ["who", "msf", "cdc", "scientific"]},
    "evidence_search": {"min_units": 1, "authority": None},   # toute autorité
    "unsafe": {"min_units": 0, "authority": []},              # refus d'emblée
    "unknown": {"min_units": 1, "authority": None},
}


@dataclass(slots=True)
class EvidenceRequirementCheck:
    intent: str
    passed: bool
    units_in_pack: int
    units_accepted: int
    reason: str = ""


def requirement_for(intent: str) -> dict:
    return REQUIREMENTS.get(intent, REQUIREMENTS["unknown"])


def check_evidence_requirement(pack, intent: str) -> EvidenceRequirementCheck:
    """Vérifie que le pack satisfait le contrat minimal de l'intention.

    pack : EvidencePack (domaine). Une unité est comptée si son autorité est
    admise pour l'intention (None = toutes admises).
    """
    req = requirement_for(intent)
    units = list(getattr(pack, "units", []) or [])
    if not units:
        return EvidenceRequirementCheck(
            intent, False, 0, 0,
            "aucune preuve récupérée — pas de preuve, pas de synthèse")
    if req["authority"] is None:
        accepted = len(units)
    else:
        allowed = {a.lower() for a in req["authority"]}
        accepted = sum(1 for u in units
                       if str(u.source.authority.value).lower() in allowed)
    if accepted < int(req["min_units"]):
        return EvidenceRequirementCheck(
            intent, False, len(units), accepted,
            f"pack insuffisant : {accepted} unité(s) d'autorité admise "
            f"({', '.join(req['authority'])}) pour {intent}, {req['min_units']} requise(s)")
    return EvidenceRequirementCheck(intent, True, len(units), accepted)
