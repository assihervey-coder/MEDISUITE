"""Capacités des modèles — chargement YAML + vérification d'invariants.

Source déclarative : configs/ai/model_capabilities.yaml (générée depuis le
registre). Ce module fournit la couche de lecture/vérification utilisée par
le routeur et la gouvernance.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from tropirag.ai.registry.model_registry import ModelCapabilities  # noqa: F401

# invariants NON négociables — jamais surchargeables par YAML
_HARD_INVARIANTS = {"autonomous_diagnosis": False}

# tâches dont la sortie alimente une décision clinique → evidence obligatoire
_EVIDENCE_MANDATORY_TASKS = {"clinical_reasoning", "biomedical_synthesis", "logical_audit"}


@lru_cache(maxsize=1)
def load_capabilities_yaml(path: Path | None = None) -> dict[str, dict[str, Any]]:
    """Charge capabilities par model_id depuis model_capabilities.yaml."""
    from tropirag.core.config import CONFIGS_DIR

    p = Path(path or (CONFIGS_DIR / "ai" / "model_capabilities.yaml"))
    if not p.exists():
        return {}
    with open(p, encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    return data.get("capabilities", {}) or {}


def capabilities_of(model_id: str) -> dict[str, Any] | None:
    return load_capabilities_yaml().get(model_id)


def check_invariants(model_id: str, caps: dict[str, Any] | None = None) -> list[str]:
    """Vérifie les invariants de gouvernance sur les capacités déclarées.

    - autonomous_diagnosis est TOUJOURS false (invariant absolu),
    - evidence_required est requis pour les tâches de synthèse clinique
      (clinical_reasoning, biomedical_synthesis, logical_audit) — PAS pour
      vision/parole/embeddings/reranking dont les sorties sont des
      observations, jamais des décisions.
    """
    caps = dict(caps or capabilities_of(model_id) or {})
    violations: list[str] = []
    for key, expected in _HARD_INVARIANTS.items():
        if caps.get(key, expected) is not expected:
            violations.append(f"{model_id}: {key} doit être {expected} "
                              "(invariant de gouvernance non surchargeable)")
    tasks = set(caps.get("tasks", []))
    if tasks & _EVIDENCE_MANDATORY_TASKS and not caps.get("evidence_required"):
        violations.append(f"{model_id}: tâche de synthèse clinique "
                          f"{sorted(tasks & _EVIDENCE_MANDATORY_TASKS)} sans "
                          "evidence_required=true")
    return violations


def all_invariant_violations() -> dict[str, list[str]]:
    """Vérifie tous les modèles déclarés — {model_id: [violations]}."""
    out: dict[str, list[str]] = {}
    for model_id, caps in load_capabilities_yaml().items():
        v = check_invariants(model_id, caps)
        if v:
            out[model_id] = v
    return out


def tasks_matrix() -> dict[str, list[str]]:
    """Matrice tâche → modèles capables (pour le routeur)."""
    matrix: dict[str, list[str]] = {}
    for model_id, caps in load_capabilities_yaml().items():
        for task in caps.get("tasks", []):
            matrix.setdefault(task, []).append(model_id)
    return matrix
