"""Validation statique des règles (lint clinique avant chargement)."""
from __future__ import annotations

from pathlib import Path

import yaml

from tropirag.core.errors import RuleLoadError
from tropirag.clinical_engine.rules.rule_engine import Rule, evaluate_condition
from tropirag.domain.clinical_case.builders import build_case


def validate_rule_file(path: Path) -> list[str]:
    """Contrôles : IDs uniques, action connue, arbre de conditions parsable, then cohérent."""
    errors: list[str] = []
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict) or "rules" not in data:
        return [f"{path.name}: clé 'rules' absente"]
    seen_ids: set[str] = set()
    for i, raw in enumerate(data["rules"]):
        rid = raw.get("id", f"(#{i} sans id)")
        if rid in seen_ids:
            errors.append(f"{path.name}:{rid}: id dupliqué dans le fichier")
        seen_ids.add(rid)
        try:
            rule = Rule(
                id=str(rid),
                action=str(raw.get("action", "inform")),
                priority=int(raw.get("priority", 50)),
                weight=float(raw.get("weight", 0.5)),
                disease=raw.get("disease"),
                when=raw.get("when"),
                then=dict(raw.get("then") or {}),
            )
        except RuleLoadError as e:
            errors.append(f"{path.name}:{rid}: {e}")
            continue
        # l'arbre doit être évaluable sur un cas vide (pas d'exception)
        try:
            evaluate_condition(rule.when, __import__(
                "tropirag.clinical_engine.rules.rule_engine", fromlist=["EvalContext"]
            ).EvalContext(build_case({})))
        except Exception as e:  # noqa: BLE001
            errors.append(f"{path.name}:{rid}: condition invalide — {e}")
        if raw.get("evidence") and not isinstance(raw.get("evidence"), list):
            errors.append(f"{path.name}:{rid}: evidence doit être une liste")
    return errors


def validate_all(rule_dir: Path | None = None) -> list[str]:
    base = rule_dir or Path(__file__).resolve().parents[3] / "rules"
    errors: list[str] = []
    for p in sorted(base.rglob("*.yaml")):
        if "tests" in p.parts:
            continue
        errors.extend(validate_rule_file(p))
    return errors
