"""Énumérations du domaine Proposal."""
from __future__ import annotations

from enum import Enum


class ProposalState(str, Enum):
    """Machine à états complète du cycle d'évolution (EVOLUTION_LIFECYCLE.md)."""

    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    VALIDATED = "VALIDATED"
    CLASSIFIED = "CLASSIFIED"
    IMPACT_ANALYSIS = "IMPACT_ANALYSIS"
    RISK_ASSESSMENT = "RISK_ASSESSMENT"
    DECISION_PENDING = "DECISION_PENDING"
    REJECTED = "REJECTED"
    DEFERRED = "DEFERRED"
    APPROVED = "APPROVED"
    CHANGE_PLANNED = "CHANGE_PLANNED"
    IMPLEMENTATION = "IMPLEMENTATION"
    TECHNICAL_VALIDATION = "TECHNICAL_VALIDATION"
    CLINICAL_VALIDATION = "CLINICAL_VALIDATION"
    SAFETY_VALIDATION = "SAFETY_VALIDATION"
    RELEASE_CANDIDATE = "RELEASE_CANDIDATE"
    CANARY = "CANARY"
    PILOT = "PILOT"
    ROLLOUT = "ROLLOUT"
    PAUSED = "PAUSED"
    ROLLED_BACK = "ROLLED_BACK"
    RELEASED = "RELEASED"
    MONITORED = "MONITORED"
    ACCEPTED = "ACCEPTED"


class ProposalType(str, Enum):
    FEATURE = "FEATURE"
    ARCHITECTURE = "ARCHITECTURE"
    AI = "AI"
    CLINICAL = "CLINICAL"
    DATA = "DATA"
    SECURITY = "SECURITY"
    REGULATORY = "REGULATORY"


class Priority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ChangeClass(str, Enum):
    """Classification P0..P9 — plus la classe monte, plus les gates sont fortes."""

    P0 = "P0"  # interdit
    P1 = "P1"  # documentaire
    P2 = "P2"  # maintenance
    P3 = "P3"  # feature non-breaking
    P4 = "P4"  # architecture
    P5 = "P5"  # données
    P6 = "P6"  # IA
    P7 = "P7"  # clinique
    P8 = "P8"  # sécurité patient
    P9 = "P9"  # réglementaire


class ImpactLevel(str, Enum):
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Outcome(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    DEFERRED = "DEFERRED"
