"""Interactions médicamenteuses — table déterministe (non exhaustive, V1)."""
from __future__ import annotations

INTERACTIONS: dict[tuple[str, str], str] = {
    ("aspirin", "ibuprofen"): "Potentialisation du risque hémorragique gastrique",
    ("warfarin", "paracetamol"): "Augmentation de l'INR à doses répétées de paracétamol",
    ("warfarin", "ibuprofen"): "Risque hémorragique majeur (AINS + AVK)",
    ("warfarin", "aspirin"): "Risque hémorragique majeur",
    ("ciprofloxacin", "artemether_lumefantrine"): "Allongement QT — surveillance ECG",
    ("quinine_iv", "artemether_lumefantrine"): "Ne pas associer — QT prolongé",
    ("metoclopramide", "ciprofloxacin"): "Allongement QT combiné",
    ("rifampicin", "artemether_lumefantrine"): "Baisse des concentrations d'artéméther (induction enzymatique)",
}


def check_interaction(a: str, b: str) -> str | None:
    return INTERACTIONS.get((a, b)) or INTERACTIONS.get((b, a))
