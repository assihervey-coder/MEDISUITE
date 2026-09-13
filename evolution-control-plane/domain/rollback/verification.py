"""Vérification post-rollback — smoke bloquant + preuve."""
from __future__ import annotations


class RollbackVerification:
    def __init__(self, rollback_id: str, smoke_passed: bool,
                 chain_intact: bool, flags_off: bool) -> None:
        self.rollback_id = rollback_id
        self.smoke_passed = smoke_passed
        self.chain_intact = chain_intact
        self.flags_off = flags_off

    @property
    def success(self) -> bool:
        return self.smoke_passed and self.chain_intact and self.flags_off

    def to_dict(self) -> dict:
        return {"rollback_id": self.rollback_id, "smoke_passed": self.smoke_passed,
                "audit_chain_intact": self.chain_intact, "flags_off": self.flags_off,
                "success": self.success}
