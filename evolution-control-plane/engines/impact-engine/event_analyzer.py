"""Analyseur événements — contrats du bus touchés (EVENTS.yaml)."""
from __future__ import annotations

from pathlib import Path

EVENTS_FILE = Path(__file__).resolve().parents[3] / "architecture" / "baseline" / "EVENTS.yaml"

EVOLUTION_EVENTS = {
    "ProposalSubmitted", "ProposalValidated", "ProposalClassified",
    "ImpactAnalysisCompleted", "RiskAssessmentCompleted", "ApprovalRequested",
    "ProposalApproved", "ProposalRejected", "ChangeSetCreated",
    "ImplementationStarted", "ImplementationCompleted",
    "CompatibilityCheckCompleted", "ValidationStarted", "ValidationCompleted",
    "ClinicalValidationCompleted", "SafetyValidationCompleted",
    "ReleaseCandidateCreated", "RolloutStarted", "RolloutAdvanced",
    "RolloutPaused", "RollbackTriggered", "RollbackCompleted",
    "ReleaseCompleted", "EvolutionAccepted",
}


def load_platform_events() -> set[str]:
    try:
        import yaml
        data = yaml.safe_load(EVENTS_FILE.read_text(encoding="utf-8")) or {}
        return set(data.get("contracts", []))
    except Exception:  # noqa: BLE001 — baseline absente : repli minimal
        return set()


def analyze_events(changed_paths: list[str]) -> dict:
    touched = set()
    if any("events" in p or "bus" in p for p in changed_paths):
        touched |= load_platform_events()
    if any("evolution" in p for p in changed_paths):
        touched |= EVOLUTION_EVENTS
    return {"events_touched": sorted(touched), "count": len(touched)}
