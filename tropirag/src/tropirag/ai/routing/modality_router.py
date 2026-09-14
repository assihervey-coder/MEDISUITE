"""Modality Router — répartit selon la modalité d'entrée."""
from __future__ import annotations

from tropirag.core.enums import Modality

MODALITY_TASKS = {
    Modality.AUDIO: ["dictation", "conversation"],
    Modality.IMAGE: ["image_analysis", "image_triage", "segmentation"],
    Modality.TEXT: ["clinical_synthesis", "biomedical_synthesis", "logical_audit"],
}


def tasks_for_modality(modality: Modality) -> list[str]:
    return MODALITY_TASKS.get(modality, [])
