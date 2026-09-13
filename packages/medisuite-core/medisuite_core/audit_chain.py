"""Registre d'audit à chaîne de hachage (ADR-0021).

Chaque événement clinique est chaîné : hash_n = SHA256(payload_n | prev_hash).
Toute altération rétroactive casse la chaîne → détection par `verify()`.
Garanties de non-répudiation proches d'une blockchain sans son coût opérationnel.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field, asdict

GENESIS = "0" * 64


@dataclass
class AuditEvent:
    index: int
    timestamp: float
    actor: str                 # user_id ou "system"
    role: str                  # rôle RBAC au moment de l'action
    action: str                # ex. "patient.read", "lab.validate", "ai.infer"
    resource: str              # ex. "patient:abc123", "study:1.2.840..."
    detail: dict = field(default_factory=dict)
    prev_hash: str = GENESIS
    hash: str = ""

    def compute_hash(self) -> str:
        payload = json.dumps(
            {"index": self.index, "timestamp": self.timestamp, "actor": self.actor,
             "role": self.role, "action": self.action, "resource": self.resource,
             "detail": self.detail, "prev_hash": self.prev_hash},
            sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        return hashlib.sha256(payload.encode()).hexdigest()

    def to_dict(self) -> dict:
        return asdict(self)


class HashChainLedger:
    """Registre en mémoire ; la persistance est déléguée au service appelant
    (audit-service le stocke en base et expose POST /api/v1/chain/verify)."""

    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    def append(self, actor: str, role: str, action: str,
               resource: str, detail: dict | None = None) -> AuditEvent:
        prev = self.events[-1].hash if self.events else GENESIS
        event = AuditEvent(
            index=len(self.events), timestamp=time.time(), actor=actor, role=role,
            action=action, resource=resource, detail=detail or {}, prev_hash=prev)
        event.hash = event.compute_hash()
        self.events.append(event)
        return event

    def verify(self) -> tuple[bool, int | None]:
        """Retourne (intégrité_ok, index_première_altération ou None)."""
        expected_prev = GENESIS
        for event in self.events:
            if event.prev_hash != expected_prev or event.hash != event.compute_hash():
                return False, event.index
            expected_prev = event.hash
        return True, None

    def tail(self, n: int = 50) -> list[dict]:
        return [e.to_dict() for e in self.events[-n:]]
