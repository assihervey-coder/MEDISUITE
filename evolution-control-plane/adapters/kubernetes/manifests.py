"""Adaptateur Kubernetes — V1 : validation statique des manifests (sans cluster)."""
from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[4]
K8S = ROOT / "infrastructure" / "kubernetes"


def manifests_valid() -> tuple[bool, list[str]]:
    errors: list[str] = []
    for path in sorted(K8S.rglob("*.yaml")):
        try:
            docs = [d for d in yaml.safe_load_all(path.read_text(encoding="utf-8")) if d]
            for d in docs:
                if "helm" not in path.parts and ("apiVersion" not in d or "kind" not in d):
                    errors.append(f"{path.relative_to(ROOT)} : doc invalide")
        except yaml.YAMLError as exc:
            errors.append(f"{path.relative_to(ROOT)} : YAML invalide ({exc})")
    return not errors, errors


def default_deny_enforced() -> bool:
    np = K8S / "base" / "networkpolicy.yaml"
    if not np.exists():
        return False
    docs = [d for d in yaml.safe_load_all(np.read_text(encoding="utf-8")) if d]
    return any(d.get("metadata", {}).get("name") == "default-deny-ingress" for d in docs)
