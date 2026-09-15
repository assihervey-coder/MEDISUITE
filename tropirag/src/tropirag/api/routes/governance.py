"""Routes gouvernance — état public du verrou + garde de décision (451).

GET  /api/v1/governance         état réglementaire (descripteur + calendrier
                                M+18) — consommé par le portail et la
                                simulation ; aucune donnée patient.
POST /api/v1/decision/finalize  matérialisation d'une décision clinique à
                                partir d'une sortie CDS → 451 Unavailable
                                For Legal Reasons tant que l'investigation
                                MEDISUITE-CI-01 est ouverte (fail-closed,
                                journalisé via l'audit middleware).
"""
from __future__ import annotations

from datetime import date, datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from tropirag.governance.investigation import (
    default_m0,
    finalize_denial,
    is_decisional_use_allowed,
    m18_status,
    stamp,
)

router = APIRouter()


class FinalizeRequest(BaseModel):
    """Charge d'une tentative de matérialisation de décision — toujours refusée
    en régime d'investigation ; le schéma existe pour journaliser CE qui a été
    tenté (traçabilité DSMB / audits ANOC-CI)."""

    case_id: str | None = Field(default=None, description="cas CDS à l'origine")
    decision: str | None = Field(default=None, description="décision tentée (libre)")
    destinataire: str | None = Field(default=None, description="cible (prescription, ordonnance…)")


@router.get("/governance")
async def governance_state() -> dict:
    """État public du verrou — descripteur + calendrier M+18."""
    today = date.today()
    m0 = default_m0()
    cal = m18_status(today, m0)
    return {
        **stamp(),
        "calendrier": cal,
        "finalize": {
            "route": "POST /api/v1/decision/finalize",
            "disponible": is_decisional_use_allowed(),
            "refus_code": 451,
        },
        "serveur_ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


@router.post("/decision/finalize")
async def finalize_decision(req: FinalizeRequest) -> dict:
    """Garde fail-closed — l'interdiction est TECHNIQUE, pas décorative."""
    denial = finalize_denial(req.case_id)
    raise HTTPException(
        status_code=451,
        detail=denial,
        headers={
            "X-Governance-Status": "investigation",
            "X-Governance-Lock": "M+18",
            "X-Governance-Decision": "interdite",
            "Retry-After": "86400",  # réévalué au prochain cycle monitoring
        },
    )
