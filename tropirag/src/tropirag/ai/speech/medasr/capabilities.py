"""Capacités MedASR — résolution dynamique depuis le Model Registry.

La déclaration statique n'est qu'un repli : la source de vérité est le
registre (configs/ai/model_registry.yaml + model_capabilities.yaml).
"""
from __future__ import annotations

from typing import Any

MODEL_ID = "medasr-quantized"

FALLBACK: dict[str, Any] = {'tasks': ['speech_dictation'], 'modalities': ['audio', 'text'], 'languages': ['fr', 'en'], 'clinical_risk_max': 'none', 'autonomous_diagnosis': False, 'evidence_required': False, 'local_execution': True, 'min_vram_gb': 0.0}


def capabilities() -> dict[str, Any]:
    """Capacités réelles du modèle, lues dans le registre."""
    from tropirag.ai.registry.model_registry import get_registry

    m = get_registry().get(MODEL_ID)
    if m is None:
        return dict(FALLBACK)
    return {
        "tasks": [t.value for t in m.capabilities.tasks],
        "modalities": [x.value for x in m.capabilities.modalities],
        "languages": list(m.capabilities.languages),
        "clinical_risk_max": m.capabilities.clinical_risk_max,
        "autonomous_diagnosis": m.capabilities.autonomous_diagnosis_allowed,
        "evidence_required": m.capabilities.evidence_required,
        "local_execution": m.capabilities.local_execution,
        "min_vram_gb": m.capabilities.min_vram_gb,
    }


CAPABILITIES = capabilities()


def can(task: str) -> bool:
    return task in capabilities()["tasks"]
