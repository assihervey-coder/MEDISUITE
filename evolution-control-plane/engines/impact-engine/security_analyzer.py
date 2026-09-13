"""Analyseur sécurité — surfaces sensibles touchées."""
from __future__ import annotations

SENSITIVE_PREFIXES = (
    "security/", "infrastructure/kubernetes/base/networkpolicy.yaml",
    "services/auth-service/", "packages/medisuite-core/medisuite_core/security.py",
    "packages/medisuite-core/medisuite_core/rbac.py",
    "packages/medisuite-core/medisuite_core/audit_chain.py",
    "services/api-gateway/", "audit/",
)


def analyze_security(changed_paths: list[str]) -> dict:
    touched = [p for p in changed_paths
               if any(p == sp or p.startswith(sp) for sp in SENSITIVE_PREFIXES)]
    network_policy = any("networkpolicy" in p for p in touched)
    audit_chain = any("audit_chain" in p or p.startswith("audit/") for p in touched)
    return {
        "security_paths": touched,
        "network_policy_touched": network_policy,
        "audit_chain_touched": audit_chain,
        "count": len(touched),
    }
