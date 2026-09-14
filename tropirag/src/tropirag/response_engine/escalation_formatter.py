"""Formatage des escalades pour l'affichage clinique."""
from __future__ import annotations

_LEVEL_LABELS = {
    "isolation": "⚠ ISOLEMENT IMMÉDIAT REQUIS",
    "emergency_transfer": "TRANSFERT UR GENT —监督 médicalisé requis".replace(" UR GENT", " URGENT").replace("监督", "surveillance"),
    "refer_hospital": "RÉFÉRENCE HOSPITALIÈRE recommandée",
    "senior_clinician": "AVIS MÉDECIN SENIOR recommandé",
    "notify_public_health": "NOTIFICATION SANTÉ PUBLIQUE",
}


def format_escalations(escalations: list[dict]) -> list[str]:
    out = []
    for e in escalations:
        label = _LEVEL_LABELS.get(e.get("level", ""), e.get("level", ""))
        out.append(f"{label} — {e.get('message', '')}")
    return out
