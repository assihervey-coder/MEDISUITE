"""Autorisation par rôles (V1 : rôle unique clinicien)."""
from __future__ import annotations

ROLES = {
    "clinician": ["cases:*", "clinical:*", "evidence:*", "drugs:*"],
    "admin": ["*"],
}


def can(role: str, resource: str) -> bool:
    perms = ROLES.get(role, [])
    if "*" in perms:
        return True
    scope = resource.split(":")[0] + ":*"
    return scope in perms or resource in perms
