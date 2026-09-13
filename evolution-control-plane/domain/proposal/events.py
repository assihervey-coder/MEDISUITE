"""Événements du domaine — bus in-process V1, chaîne d'audit côté adapters."""
from __future__ import annotations

from typing import Any

from .value_objects import now_iso

EVENTS_EMITTED: list[dict[str, Any]] = []

# Noms canoniques des événements du cycle d'évolution
PROPOSAL_SUBMITTED = "ProposalSubmitted"
PROPOSAL_VALIDATED = "ProposalValidated"
PROPOSAL_CLASSIFIED = "ProposalClassified"
IMPACT_ANALYSIS_COMPLETED = "ImpactAnalysisCompleted"
RISK_ASSESSMENT_COMPLETED = "RiskAssessmentCompleted"
APPROVAL_REQUESTED = "ApprovalRequested"
PROPOSAL_APPROVED = "ProposalApproved"
PROPOSAL_REJECTED = "ProposalRejected"
CHANGE_SET_CREATED = "ChangeSetCreated"
IMPLEMENTATION_STARTED = "ImplementationStarted"
IMPLEMENTATION_COMPLETED = "ImplementationCompleted"
COMPATIBILITY_CHECK_COMPLETED = "CompatibilityCheckCompleted"
VALIDATION_STARTED = "ValidationStarted"
VALIDATION_COMPLETED = "ValidationCompleted"
CLINICAL_VALIDATION_COMPLETED = "ClinicalValidationCompleted"
SAFETY_VALIDATION_COMPLETED = "SafetyValidationCompleted"
RELEASE_CANDIDATE_CREATED = "ReleaseCandidateCreated"
ROLLOUT_STARTED = "RolloutStarted"
ROLLOUT_ADVANCED = "RolloutAdvanced"
ROLLOUT_PAUSED = "RolloutPaused"
ROLLBACK_TRIGGERED = "RollbackTriggered"
ROLLBACK_COMPLETED = "RollbackCompleted"
RELEASE_COMPLETED = "ReleaseCompleted"
EVOLUTION_ACCEPTED = "EvolutionAccepted"


def emit(event: str, **payload: Any) -> dict[str, Any]:
    """Émet un événement (in-process V1) — jamais réécrit après émission."""
    evt = {"event": event, "timestamp": now_iso(), **payload}
    EVENTS_EMITTED.append(evt)
    return evt
