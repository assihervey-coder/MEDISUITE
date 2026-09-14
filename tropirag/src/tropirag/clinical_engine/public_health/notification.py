"""Notification aux autorités sanitaires (RSI — maladies à déclaration obligatoire)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PublicHealthNotification:
    reason: str
    urgency: str = "immediate"
    reporting_entity: str = "TropiRAG node"
    authorities: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"reason": self.reason, "urgency": self.urgency,
                "authorities": self.authorities or ["direction-departementale-sante"]}


NOTIFIABLE_DISEASES = {
    "yellow_fever": "Fièvre jaune — déclaration OBLIGATOIRE (RSI 2005)",
    "ebola": "Maladie à virus Ebola — alerte immédiate OMS",
    "marburg": "Maladie à virus Marburg — alerte immédiate OMS",
    "lassa": "Fièvre de Lassa — déclaration obligatoire",
    "meningococcal": "Méningite à méningocoque — déclaration obligatoire",
}


def notification_for(disease: str) -> PublicHealthNotification | None:
    if disease in NOTIFIABLE_DISEASES:
        return PublicHealthNotification(reason=NOTIFIABLE_DISEASES[disease])
    return None
