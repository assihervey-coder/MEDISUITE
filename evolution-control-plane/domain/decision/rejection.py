"""Rejection — rejet et reports motivés."""
from .entities import Rejection  # noqa: F401


def reject(proposal_id: str, actor: str, reason: str) -> dict:
    if not reason or len(reason) < 10:
        raise ValueError("un rejet doit être motivé (≥ 10 caractères)")
    return {"proposal_id": proposal_id, "rejection": Rejection(reason=reason, actor=actor).to_dict()}


def defer(proposal_id: str, actor: str, reason: str, revisit: str) -> dict:
    """DEFERRED = réactivable ; une date/condition de revisite est obligatoire."""
    if not revisit:
        raise ValueError("DEFERRED exige une condition/échéance de revisite")
    return {"proposal_id": proposal_id, "actor": actor, "reason": reason,
            "revisit_when": revisit, "outcome": "DEFERRED"}
