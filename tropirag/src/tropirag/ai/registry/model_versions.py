"""Gestion des versions de modèles — gouvernance des mises à jour.

Chaque version d'un modèle embarqué dans le mesh DOIT être enregistrée avec :
    - l'empreinte du binaire (GGUF/safetensors — vérifiée au démarrage),
    - le statut de validation clinique,
    - le hash du jeu d'évaluation qui a servi à la validation.

Règle : un modèle non validé cliniquement ne peut servir que des tâches
à risque ≤ assisted, jamais la synthèse clinique finale.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(slots=True)
class ModelVersion:
    model_id: str
    version: str
    sha256: str
    clinically_validated: bool
    validated_on: str | None = None       # date ISO
    eval_set_hash: str = ""
    notes: str = ""

    @property
    def key(self) -> str:
        return f"{self.model_id}@{self.version}"


VERSIONS: dict[str, ModelVersion] = {}


def _seed_known_versions() -> None:
    """Versions initiales du mesh V1 — non validées cliniquement par défaut."""
    known = [
        ("med42-v2-70b", "v2", "fp16-70b"),
        ("openbiollm-70b", "v1", "fp16-70b"),
        ("deepseek-r1-distill-32b", "r1-distill", "q4-k-m-32b"),
        ("medgemma-4b-it", "it4b", "bf16-4b"),
        ("minicpm-v-2.6", "2.6", "q4-8b"),
        ("sam2-medical", "sam2.1-hiera-large", "fp16"),
        ("medasr-quantized", "q5", "q5-k-m"),
        ("whisper-large-v3", "large-v3", "fp16-1.5b"),
        ("bge-m3", "v1.5", "fp16-568m"),
        ("qwen-reranker", "v2-0.5b", "fp16-0.5b"),
    ]
    for model_id, version, quant in known:
        v = ModelVersion(model_id=model_id, version=version,
                         sha256=f"pending-deployment:{quant}",
                         clinically_validated=False,
                         notes="empreinte à fixer au déploiement "
                               "(deployment/ollama/pull_models.sh)")
        VERSIONS[v.key] = v


_seed_known_versions()


def register_version(v: ModelVersion) -> None:
    VERSIONS[v.key] = v


def get_version(model_id: str, version: str) -> ModelVersion | None:
    return VERSIONS.get(f"{model_id}@{version}")


def latest(model_id: str) -> ModelVersion | None:
    """Dernière version enregistrée d'un modèle (ordre d'insertion)."""
    cands = [v for v in VERSIONS.values() if v.model_id == model_id]
    return cands[-1] if cands else None


def validated_versions() -> list[ModelVersion]:
    return [v for v in VERSIONS.values() if v.clinically_validated]


def validate(model_id: str, version: str, eval_set_hash: str,
             validated_on: str | None = None) -> ModelVersion | None:
    """Marque une version cliniquement validée (décision de gouvernance)."""
    v = get_version(model_id, version)
    if v is None:
        return None
    v.clinically_validated = True
    v.eval_set_hash = eval_set_hash
    v.validated_on = validated_on or date.today().isoformat()
    return v


def snapshot() -> list[dict]:
    return [{"model_id": v.model_id, "version": v.version,
             "sha256": v.sha256, "validated": v.clinically_validated,
             "validated_on": v.validated_on, "eval_set_hash": v.eval_set_hash}
            for v in VERSIONS.values()]
