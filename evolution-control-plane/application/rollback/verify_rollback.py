"""Cas d'usage — vérification post-rollback + événement de complétion."""
from __future__ import annotations

from ...domain.proposal.events import ROLLBACK_COMPLETED, emit
from ...domain.rollback.verification import RollbackVerification


def verify_rollback(rollback_id: str, smoke_passed: bool, chain_intact: bool,
                    flags_off: bool) -> dict:
    verification = RollbackVerification(rollback_id, smoke_passed, chain_intact,
                                        flags_off)
    result = verification.to_dict()
    if verification.success:
        emit(ROLLBACK_COMPLETED, rollback_id=rollback_id)
        result["next_state"] = "ROLLED_BACK (terminal après post-mortem)"
    return result
