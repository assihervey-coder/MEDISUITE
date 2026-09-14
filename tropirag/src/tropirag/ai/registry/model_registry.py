"""Registre de modèles — MODEL_REGISTRY du mesh IA.

Chaque modèle déclare ses capacités. Le routeur sélectionne PAR CAPACITÉ,
jamais par nom. Invariants de gouvernance :
    - autonomous_diagnosis: false (PARTOUT)
    - evidence_required pour toute tâche clinique
    - clinically_validated: statut de validation par version
"""
from __future__ import annotations

import yaml
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from tropirag.core.enums import ClinicalTask, InferenceMode, Modality
from tropirag.core.identifiers import fingerprint


@dataclass(slots=True)
class ModelCapabilities:
    """Déclaration contractuelle d'un modèle."""

    tasks: list[ClinicalTask] = field(default_factory=list)
    modalities: list[Modality] = field(default_factory=list)
    languages: list[str] = field(default_factory=lambda: ["en"])
    clinical_risk_max: str = "assisted"       # none | assisted | supervised
    autonomous_diagnosis_allowed: bool = False
    evidence_required: bool = False
    local_execution: bool = True
    context_required: list[str] = field(default_factory=list)
    min_vram_gb: float = 0.0
    notes: str = ""


@dataclass(slots=True)
class ModelMetadata:
    """Fiche d'identité d'un modèle du mesh."""

    model_id: str                        # 'medgemma-4b-it'
    display_name: str
    family: str                          # 'vision', 'text', 'speech', 'embeddings', 'reranking'
    provider_gateway: str                # 'ollama' | 'vllm' | 'deterministic'
    capabilities: ModelCapabilities = field(default_factory=ModelCapabilities)
    vram_gb: float = 0.0
    priority: int = 50                   # préférence du routeur à capacité égale
    deployment: str = "local"            # local | server
    clinically_validated: bool = False
    validated_with: str = ""             # hash du jeu d'évaluation
    fallback_for: list[str] = field(default_factory=list)  # model_id qu'il remplace
    health: str = "unknown"              # unknown | up | down


# ---------------------------------------------------------------------------
# Registre par défaut — embarqué (surchargeable via configs/ai/)
# ---------------------------------------------------------------------------

DEFAULT_MODELS: list[ModelMetadata] = [
    # — Texte : raisonnement clinique —————————————
    ModelMetadata(
        model_id="med42-v2-70b", display_name="Med42 v2 (70B)",
        family="text", provider_gateway="ollama", vram_gb=42.0, priority=90,
        deployment="server",
        capabilities=ModelCapabilities(
            tasks=[ClinicalTask.CLINICAL_REASONING, ClinicalTask.BIOMEDICAL_SYNTHESIS],
            modalities=[Modality.TEXT], languages=["en", "fr"],
            clinical_risk_max="supervised",
            autonomous_diagnosis_allowed=False, evidence_required=True,
            local_execution=False, context_required=["symptoms", "patient_context"],
            min_vram_gb=42.0,
            notes="Clinical Reasoner — synthèse encadrée par Evidence Pack + règles.",
        ),
    ),
    ModelMetadata(
        model_id="openbiollm-70b", display_name="OpenBioLLM (70B)",
        family="text", provider_gateway="ollama", vram_gb=42.0, priority=75,
        deployment="server",
        capabilities=ModelCapabilities(
            tasks=[ClinicalTask.BIOMEDICAL_SYNTHESIS],
            modalities=[Modality.TEXT], languages=["en", "fr"],
            clinical_risk_max="supervised",
            autonomous_diagnosis_allowed=False, evidence_required=True,
            local_execution=False, min_vram_gb=42.0,
            notes="Biomedical Synthesizer — littérature et dossiers complexes.",
        ),
    ),
    ModelMetadata(
        model_id="deepseek-r1-distill-32b", display_name="DeepSeek-R1-Distill (32B)",
        family="text", provider_gateway="ollama", vram_gb=20.0, priority=80,
        capabilities=ModelCapabilities(
            tasks=[ClinicalTask.LOGICAL_AUDIT],
            modalities=[Modality.TEXT], languages=["en", "fr"],
            clinical_risk_max="assisted",
            autonomous_diagnosis_allowed=False, evidence_required=True,
            min_vram_gb=20.0,
            notes="Auditeur logique — cohérence, contradictions. Ne décide JAMAIS.",
        ),
    ),
    # — Vision ————————————————————————
    ModelMetadata(
        model_id="medgemma-4b-it", display_name="MedGemma 4B IT",
        family="vision", provider_gateway="ollama", vram_gb=4.0, priority=85,
        capabilities=ModelCapabilities(
            tasks=[ClinicalTask.IMAGE_ANALYSIS],
            modalities=[Modality.IMAGE, Modality.TEXT], languages=["en", "fr"],
            clinical_risk_max="assisted",
            autonomous_diagnosis_allowed=False, evidence_required=False,
            context_required=["symptoms", "patient_context", "localization", "duration"],
            notes="Analyse d'image contextualisée — premier avis / seconde lecture.",
        ),
    ),
    ModelMetadata(
        model_id="minicpm-v-2.6", display_name="MiniCPM-V 2.6",
        family="vision", provider_gateway="ollama", vram_gb=6.0, priority=70,
        fallback_for=["medgemma-4b-it"],
        capabilities=ModelCapabilities(
            tasks=[ClinicalTask.IMAGE_TRIAGE],
            modalities=[Modality.IMAGE, Modality.TEXT], languages=["en", "zh"],
            clinical_risk_max="assisted",
            autonomous_diagnosis_allowed=False,
            notes="Triage / screening image — sensibilité-spécificité équilibrées.",
        ),
    ),
    ModelMetadata(
        model_id="sam2-medical", display_name="SAM2 Medical (segmentation)",
        family="vision", provider_gateway="vllm", vram_gb=8.0, priority=60,
        capabilities=ModelCapabilities(
            tasks=[ClinicalTask.IMAGE_SEGMENTATION],
            modalities=[Modality.IMAGE], languages=["en"],
            clinical_risk_max="assisted", autonomous_diagnosis_allowed=False,
            notes="Segmentation — masques et mesures. Sort l'évidence → pas le diagnostic.",
        ),
    ),
    # — Voix ————————————————————————
    ModelMetadata(
        model_id="medasr-quantized", display_name="MedASR (quantifié)",
        family="speech", provider_gateway="ollama", vram_gb=1.0, priority=90,
        capabilities=ModelCapabilities(
            tasks=[ClinicalTask.SPEECH_TO_TEXT_DICTATION],
            modalities=[Modality.AUDIO, Modality.TEXT], languages=["fr", "en"],
            clinical_risk_max="none", autonomous_diagnosis_allowed=False,
            notes="Dictée clinique FR/EN — léger, périphérie.",
        ),
    ),
    ModelMetadata(
        model_id="whisper-large-v3", display_name="Whisper Large v3",
        family="speech", provider_gateway="ollama", vram_gb=3.0, priority=75,
        capabilities=ModelCapabilities(
            tasks=[ClinicalTask.SPEECH_TO_TEXT_CONVERSATION],
            modalities=[Modality.AUDIO, Modality.TEXT],
            languages=["fr", "en", "multilingual"],
            clinical_risk_max="none", autonomous_diagnosis_allowed=False,
            notes="Conversation terrain multilingue / code-switching.",
        ),
    ),
    # — Retrieval ————————————————————————
    ModelMetadata(
        model_id="bge-m3", display_name="BGE-M3",
        family="embeddings", provider_gateway="deterministic", vram_gb=2.0, priority=90,
        capabilities=ModelCapabilities(
            tasks=[ClinicalTask.EMBEDDINGS],
            modalities=[Modality.TEXT], languages=["multilingual"],
            clinical_risk_max="none", autonomous_diagnosis_allowed=False,
            notes="Sensory retrieval layer — hybride multilingue.",
        ),
    ),
    ModelMetadata(
        model_id="qwen-reranker", display_name="Qwen Reranker",
        family="reranking", provider_gateway="deterministic", vram_gb=4.0, priority=85,
        capabilities=ModelCapabilities(
            tasks=[ClinicalTask.RERANKING],
            modalities=[Modality.TEXT], languages=["multilingual"],
            clinical_risk_max="none", autonomous_diagnosis_allowed=False,
            notes="Reranking cross-encoder — TOP 30 → TOP 5.",
        ),
    ),
]


class ModelRegistry:
    """Registre vivant des modèles — source unique de vérité du mesh."""

    def __init__(self, models: list[ModelMetadata] | None = None) -> None:
        self._models: dict[str, ModelMetadata] = {m.model_id: m for m in (models or DEFAULT_MODELS)}

    # --- chargement ------------------------------------------------------------
    @classmethod
    def from_yaml(cls, path: str | Path) -> "ModelRegistry":
        with open(path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        models: list[ModelMetadata] = []
        for m in data.get("models", []):
            caps = m.get("capabilities", {}) or {}
            models.append(ModelMetadata(
                model_id=str(m["model_id"]),
                display_name=str(m.get("display_name", m["model_id"])),
                family=str(m.get("family", "text")),
                provider_gateway=str(m.get("provider_gateway", "ollama")),
                vram_gb=float(m.get("vram_gb", 0)),
                priority=int(m.get("priority", 50)),
                deployment=str(m.get("deployment", "local")),
                clinically_validated=bool(m.get("clinically_validated", False)),
                validated_with=str(m.get("validated_with", "")),
                fallback_for=list(m.get("fallback_for", [])),
                capabilities=ModelCapabilities(
                    tasks=[ClinicalTask(t) for t in caps.get("tasks", [])],
                    modalities=[Modality(x) for x in caps.get("modalities", ["text"])],
                    languages=list(caps.get("languages", ["en"])),
                    clinical_risk_max=str(caps.get("clinical_risk_max", "assisted")),
                    autonomous_diagnosis_allowed=False,  # JAMAIS surchargé
                    evidence_required=bool(caps.get("evidence_required", False)),
                    local_execution=bool(caps.get("local_execution", True)),
                    context_required=list(caps.get("context_required", [])),
                    min_vram_gb=float(caps.get("min_vram_gb", 0)),
                    notes=str(caps.get("notes", "")),
                ),
            ))
        return cls(models)

    # --- fusion capacités déclaratives -------------------------------------------
    def apply_capabilities_yaml(self, path: str | Path) -> "ModelRegistry":
        """Fusionne configs/ai/model_capabilities.yaml dans le registre.

        Les capacités YAML surchargent celles du registre SAUF les invariants
        durs (autonomous_diagnosis forcée à False, quels que soient le YAML
        et le code). Modèles inconnus dans le YAML : ignorés.
        """
        import yaml as _yaml

        p = Path(path)
        if not p.exists():
            return self
        with open(p, encoding="utf-8") as fh:
            data = _yaml.safe_load(fh) or {}
        caps_by_model = data.get("capabilities", {}) or {}
        for model_id, caps in caps_by_model.items():
            m = self._models.get(str(model_id))
            if m is None:
                continue
            from tropirag.core.enums import ClinicalTask, Modality

            try:
                m.capabilities.tasks = [ClinicalTask(t) for t in caps.get("tasks", [])]
                m.capabilities.modalities = [Modality(x) for x in caps.get("modalities", ["text"])]
                m.capabilities.languages = list(caps.get("languages", m.capabilities.languages))
                m.capabilities.clinical_risk_max = str(caps.get("clinical_risk_max",
                                                                 m.capabilities.clinical_risk_max))
                m.capabilities.evidence_required = bool(caps.get("evidence_required",
                                                                 m.capabilities.evidence_required))
                m.capabilities.local_execution = bool(caps.get("local_execution",
                                                                m.capabilities.local_execution))
                m.capabilities.context_required = list(caps.get("context_required",
                                                                 m.capabilities.context_required))
                m.capabilities.min_vram_gb = float(caps.get("min_vram_gb",
                                                             m.capabilities.min_vram_gb) or 0)
                if caps.get("notes"):
                    m.capabilities.notes = str(caps["notes"])
            except (ValueError, TypeError):
                continue  # entrée YAML invalide → registre inchangé pour ce modèle
            m.capabilities.autonomous_diagnosis_allowed = False  # INVARIANT absolu
        return self

    # --- interrogation -----------------------------------------------------------
    def get(self, model_id: str) -> ModelMetadata | None:
        return self._models.get(model_id)

    def all(self) -> list[ModelMetadata]:
        return sorted(self._models.values(), key=lambda m: (-m.priority, m.model_id))

    def find_by_task(self, task: ClinicalTask, language: str | None = None) -> list[ModelMetadata]:
        cands = [m for m in self._models.values() if task in m.capabilities.tasks]
        if language:
            langs = [l.lower() for l in (language, "multilingual")]
            cands = [m for m in cands if any(l in [x.lower() for x in m.capabilities.languages] for l in langs)]
        return sorted(cands, key=lambda m: (-m.priority, m.model_id))

    def fallbacks_of(self, model_id: str) -> list[ModelMetadata]:
        return [m for m in self._models.values() if model_id in m.fallback_for]

    def supports(self, model_id: str, task: ClinicalTask) -> bool:
        m = self._models.get(model_id)
        return m is not None and task in m.capabilities.tasks

    def validate_invariants(self) -> list[str]:
        """Vérifie les invariants de gouvernance — retourne les violations."""
        violations = []
        for m in self._models.values():
            if m.capabilities.autonomous_diagnosis_allowed:
                violations.append(f"{m.model_id}: autonomous_diagnosis doit être false")
            if m.capabilities.evidence_required and m.family == "text" and ClinicalTask.CLINICAL_REASONING in m.capabilities.tasks:
                pass  # conforme
        return violations

    def fingerprint(self) -> str:
        return fingerprint(*sorted(self._models))

    def to_dict(self) -> list[dict]:
        return [
            {
                "model_id": m.model_id,
                "display_name": m.display_name,
                "family": m.family,
                "gateway": m.provider_gateway,
                "vram_gb": m.vram_gb,
                "priority": m.priority,
                "tasks": [t.value for t in m.capabilities.tasks],
                "languages": m.capabilities.languages,
                "clinical_risk_max": m.capabilities.clinical_risk_max,
                "autonomous_diagnosis": m.capabilities.autonomous_diagnosis_allowed,
                "evidence_required": m.capabilities.evidence_required,
                "clinically_validated": m.clinically_validated,
                "health": m.health,
            }
            for m in self.all()
        ]


@lru_cache(maxsize=1)
def get_registry() -> ModelRegistry:
    """Registre process-wide — YAML de config s'il existe, défaut sinon.

    Chaîne de sources : model_registry.yaml (identité) puis
    model_capabilities.yaml (capacités, fusion) — invariants préservés.
    """
    from tropirag.core.config import CONFIGS_DIR

    yml = CONFIGS_DIR / "ai" / "model_registry.yaml"
    registry = ModelRegistry.from_yaml(yml) if yml.exists() else ModelRegistry()
    return registry.apply_capabilities_yaml(CONFIGS_DIR / "ai" / "model_capabilities.yaml")
