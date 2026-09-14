"""Adapter MedGemma — observations visuelles FILTRÉES de tout contenu prescriptif.

Défense en profondeur : un modèle de vision ne produit QUE des observations.
Toute phrase ressemblant à une posologie, un dosage ou une conduite à tenir
est retirée AVANT même le passage des guards — la sortie d'un adaptateur
vision ne peut jamais contenir d'ordre thérapeutique.
"""
from __future__ import annotations

import re
from typing import Any

# motifs prescriptifs interdits en sortie vision
_FORBIDDEN_IN_OBSERVATIONS = [
    r"\b\d+\s?(?:mg|µg|ml|g)\b",
    r"\b\d+\s?(?:fois|jour|heures)\b[^.]{0,20}\b(?:prise|administration|dose)\b",
    r"\b(?:administrer|injecter|prescri|donner)\b",
    r"\b(?:dose|posologie)\b",
]


def is_prescriptive(text: str) -> bool:
    low = text.lower()
    return any(re.search(p, low) for p in _FORBIDDEN_IN_OBSERVATIONS)


def parse_vision(structured: Any) -> dict:
    if not isinstance(structured, dict):
        return {"description": "", "observations": [], "concerning_features": [],
                "context_elements": [], "filtered": [], "parse_ok": False}
    description = str(structured.get("description", ""))
    raw_observations = [str(x) for x in structured.get("observations", [])]
    raw_concerning = [str(x) for x in structured.get("concerning_features", [])]
    observations = [o for o in raw_observations if not is_prescriptive(o)]
    concerning = [o for o in raw_concerning if not is_prescriptive(o)]
    filtered = [o for o in raw_observations + raw_concerning if is_prescriptive(o)]
    return {
        "description": description,
        "observations": observations,
        "concerning_features": concerning,
        "context_elements": [str(x) for x in structured.get("context_elements", [])],
        "filtered": filtered,   # piste d'audit : ce qui a été retiré et pourquoi
        "parse_ok": True,
    }
