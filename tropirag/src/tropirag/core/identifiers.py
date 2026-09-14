"""Identifiants déterministes : préfixes, ULID-lite, IDs de traçabilité."""
from __future__ import annotations

import os
import secrets
import time

# Préfixes lisibles par domaine
PREFIXES = {
    "case": "CASE",
    "patient": "PAT",
    "analysis": "ANA",
    "evidence": "EVD",
    "response": "RSP",
    "inference": "INF",
    "audit": "AUD",
    "rule": "RULE",
    "request": "REQ",
    "session": "SES",
}

_B32 = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def _b32(n: int, length: int) -> str:
    out = []
    while n and len(out) < length:
        n, r = divmod(n, 32)
        out.append(_B32[r])
    while len(out) < length:
        out.append(_B32[0])
    return "".join(reversed(out))


def new_id(kind: str) -> str:
    """Identifiant lisible : PREFIX-TIMESTAMP-RANDOM (tri chronologique)."""
    prefix = PREFIXES.get(kind, "ID")
    ts = _b32(int(time.time() * 1000) - 1_700_000_000, 8)
    rnd = _b32(int.from_bytes(secrets.token_bytes(5), "big"), 8)
    return f"{prefix}-{ts}-{rnd}"


def new_request_id() -> str:
    return new_id("request")


def short_token(n: int = 6) -> str:
    return secrets.token_hex(n // 2)


def fingerprint(*parts: object) -> str:
    """Empreinte courte stable (audit, cache d'index)."""
    import hashlib

    h = hashlib.sha256("|".join(str(p) for p in parts).encode("utf-8"))
    return h.hexdigest()[:16]
