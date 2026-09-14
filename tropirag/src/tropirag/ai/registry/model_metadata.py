"""Fiche d'identité des modèles — construction, sérialisation, validation.

Miroir riche de ``model_registry.ModelMetadata`` : fonctions utilitaires pour
créer/valider/sérialiser les métadonnées d'un modèle du mesh.
"""
from __future__ import annotations

from typing import Any

from tropirag.ai.registry.model_registry import ModelCapabilities, ModelMetadata  # noqa: F401

_REQUIRED_FIELDS = ("model_id", "display_name", "family", "provider_gateway")
_VALID_FAMILIES = {"text", "vision", "speech", "embeddings", "reranking"}
_VALID_GATEWAYS = {"ollama", "vllm", "deterministic"}


def metadata_from_dict(data: dict[str, Any]) -> ModelMetadata:
    """Dictionnaire (YAML/JSON) → ModelMetadata avec invariants garantis."""
    missing = [f for f in _REQUIRED_FIELDS if not data.get(f)]
    if missing:
        raise ValueError(f"métadonnées incomplètes : champs manquants {missing}")
    if data["family"] not in _VALID_FAMILIES:
        raise ValueError(f"famille inconnue : {data['family']!r} "
                         f"(valides : {sorted(_VALID_FAMILIES)})")
    if data["provider_gateway"] not in _VALID_GATEWAYS:
        raise ValueError(f"gateway inconnue : {data['provider_gateway']!r} "
                         f"(valides : {sorted(_VALID_GATEWAYS)})")
    caps = ModelCapabilities()
    raw_caps = data.get("capabilities", {}) or {}
    from tropirag.core.enums import ClinicalTask, Modality

    caps.tasks = [ClinicalTask(t) for t in raw_caps.get("tasks", [])]
    caps.modalities = [Modality(x) for x in raw_caps.get("modalities", ["text"])]
    caps.languages = list(raw_caps.get("languages", ["en"]))
    caps.clinical_risk_max = str(raw_caps.get("clinical_risk_max", "assisted"))
    caps.autonomous_diagnosis_allowed = False   # INVARIANT — jamais surchargé
    caps.evidence_required = bool(raw_caps.get("evidence_required", False))
    caps.local_execution = bool(raw_caps.get("local_execution", True))
    caps.context_required = list(raw_caps.get("context_required", []))
    caps.min_vram_gb = float(raw_caps.get("min_vram_gb", 0) or 0)
    caps.notes = str(raw_caps.get("notes", ""))
    return ModelMetadata(
        model_id=str(data["model_id"]),
        display_name=str(data.get("display_name", data["model_id"])),
        family=str(data["family"]),
        provider_gateway=str(data["provider_gateway"]),
        capabilities=caps,
        vram_gb=float(data.get("vram_gb", 0) or 0),
        priority=int(data.get("priority", 50)),
        deployment=str(data.get("deployment", "local")),
        clinically_validated=bool(data.get("clinically_validated", False)),
        validated_with=str(data.get("validated_with", "")),
        fallback_for=list(data.get("fallback_for", [])),
    )


def validate_metadata(m: ModelMetadata) -> list[str]:
    """Contrôles de cohérence d'une fiche modèle — liste de violations."""
    violations: list[str] = []
    if m.family not in _VALID_FAMILIES:
        violations.append(f"{m.model_id}: famille invalide {m.family!r}")
    if m.provider_gateway not in _VALID_GATEWAYS:
        violations.append(f"{m.model_id}: gateway invalide {m.provider_gateway!r}")
    if m.capabilities.min_vram_gb > m.vram_gb > 0:
        violations.append(f"{m.model_id}: min_vram_gb > vram_gb déclaré")
    if m.vram_gb > 48.0:
        violations.append(f"{m.model_id}: {m.vram_gb} Go dépasse un GPU de 48 Go "
                          "(TP requis — vérifier la topologie)")
    if m.priority < 0 or m.priority > 100:
        violations.append(f"{m.model_id}: priorité hors bornes [0,100]")
    if m.capabilities.autonomous_diagnosis_allowed:
        violations.append(f"{m.model_id}: autonomous_diagnosis doit rester false")
    return violations


def summarize(m: ModelMetadata) -> str:
    """Ligne résumée lisible — tableaux de bord et logs."""
    return (f"{m.model_id} [{m.family}/{m.provider_gateway}] "
            f"{m.vram_gb:.0f}Go prio={m.priority} "
            f"risque≤{m.capabilities.clinical_risk_max} "
            f"langues={','.join(m.capabilities.languages)}")
