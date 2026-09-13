"""Cas d'usage — classification (plancher par chemins/type, remontée possible)."""
from __future__ import annotations

from typing import Any

from ...domain.proposal.entities import Proposal
from ...domain.proposal.enums import ChangeClass
from ...domain.proposal.policies import classify_by_paths


def classify(proposal: Proposal, override: ChangeClass | None = None) -> dict[str, Any]:
    """CLASSIFIED avec classe plancher ; override ne peut qu'augmenter."""
    detected = classify_by_paths(proposal.changed_paths, proposal.type,
                                 proposal.breaking_change)
    if override is not None and int(override.value[1:]) < int(detected.value[1:]):
        return {"classified": False,
                "error": f"override {override.value} < plancher détecté {detected.value}"}
    klass = proposal.classify(override=override)
    return {"classified": True, "change_class": klass.value,
            "full_regression": proposal.requires_full_regression()}
