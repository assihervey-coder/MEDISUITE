"""Énumérations du domaine clinique TropiRAG."""
from __future__ import annotations

from enum import Enum


class StrEnum(str, Enum):
    def __str__(self) -> str:  # pragma: no cover
        return self.value


class Severity(StrEnum):
    """Échelle de gravité OMS-simplifiée."""

    NONE = "none"
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


class Urgency(StrEnum):
    ROUTINE = "routine"
    PRIORITY = "priority"
    EMERGENCY = "emergency"
    IMMEDIATE = "immediate"  # danger vital immédiat


class Sex(StrEnum):
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"


class PregnancyStatus(StrEnum):
    NOT_APPLICABLE = "not_applicable"
    PREGNANT = "pregnant"
    POSSIBLY_PREGNANT = "possibly_pregnant"
    NOT_PREGNANT = "not_pregnant"
    UNKNOWN = "unknown"


class SymptomCategory(StrEnum):
    GENERAL = "general"
    NEUROLOGICAL = "neurological"
    GASTROINTESTINAL = "gastrointestinal"
    RESPIRATORY = "respiratory"
    CUTANEOUS = "cutaneous"
    HEMORRHAGIC = "hemorrhagic"
    CARDIOVASCULAR = "cardiovascular"
    GENITOURINARY = "genitourinary"
    MUSCULOSKELETAL = "musculoskeletal"


class DiseaseCategory(StrEnum):
    PARASITIC = "parasitic"
    VIRAL = "viral"
    BACTERIAL = "bacterial"
    RICKETTSIAL = "rickettsial"
    UNKNOWN = "unknown"


class Modality(StrEnum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    LAB = "lab"


class ClinicalTask(StrEnum):
    """Capacités du mesh IA — le routeur sélectionne par capacité, pas par modèle."""

    SPEECH_TO_TEXT_DICTATION = "speech_dictation"
    SPEECH_TO_TEXT_CONVERSATION = "conversation_transcription"
    CLINICAL_REASONING = "clinical_reasoning"
    BIOMEDICAL_SYNTHESIS = "biomedical_synthesis"
    LOGICAL_AUDIT = "logical_audit"
    IMAGE_ANALYSIS = "image_analysis"
    IMAGE_TRIAGE = "image_triage"
    IMAGE_SEGMENTATION = "image_segmentation"
    EMBEDDINGS = "embeddings"
    RERANKING = "reranking"


class InferenceMode(StrEnum):
    DETERMINISTIC = "deterministic"
    OLLAMA = "ollama"
    VLLM = "vllm"


class SourceAuthority(StrEnum):
    """Hiérarchie d'autorité des sources (1 = le plus fiable)."""

    WHO = "who"                    # OMS / WHO — lignes directrices internationales
    NATIONAL = "national"          # ministères de santé nationaux
    MSF = "msf"                    # protocoles terrain MSF / ALIMA
    CDC = "cdc"                    # CDC / ECDC
    INSTITUTIONAL = "institutional"  # sociétés savantes, CHU
    SCIENTIFIC = "scientific"      # littérature évaluée par les pairs
    UNKNOWN = "unknown"


AUTHORITY_RANK: dict[SourceAuthority, int] = {
    SourceAuthority.WHO: 1,
    SourceAuthority.NATIONAL: 2,
    SourceAuthority.MSF: 2,
    SourceAuthority.CDC: 2,
    SourceAuthority.INSTITUTIONAL: 3,
    SourceAuthority.SCIENTIFIC: 4,
    SourceAuthority.UNKNOWN: 9,
}


class EscalationLevel(StrEnum):
    NONE = "none"
    SENIOR_CLINICIAN = "senior_clinician"      # médecin senior à voir
    REFER_HOSPITAL = "refer_hospital"          # référence vers hôpital
    EMERGENCY_TRANSFER = "emergency_transfer"  # transfert urgent (SAMU/ambulance)
    ISOLATION = "isolation"                    # isolement immédiat (MVH)
    NOTIFY_PUBLIC_HEALTH = "notify_public_health"


class RuleActionType(StrEnum):
    RAISE_SUSPICION = "raise_suspicion"
    RED_FLAG = "red_flag"
    ESCALATE = "escalate"
    REQUIRE_TEST = "require_test"
    CONTRAINDICATE_DRUG = "contraindicate_drug"
    RECOMMEND_DRUG = "recommend_drug"
    NOTIFY = "notify"
    INFORM = "inform"


class RefusalReason(StrEnum):
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    OUTSIDE_SCOPE = "outside_scope"
    SAFETY_OVERRIDE = "safety_override"
    AUTONOMOUS_DIAGNOSIS_FORBIDDEN = "autonomous_diagnosis_forbidden"
    HALLUCINATION_DETECTED = "hallucination_detected"
    INJECTION_DETECTED = "injection_detected"


class Language(StrEnum):
    FR = "fr"
    EN = "en"
