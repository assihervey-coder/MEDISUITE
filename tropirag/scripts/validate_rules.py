#!/usr/bin/env python3
"""Valide le référentiel de règles (lint clinique + fixtures comportementales).

Modes :
    python scripts/validate_rules.py              # lint seul
    python scripts/validate_rules.py --with-tests  # lint + fixtures YAML
                                                   # (rules/fever_travel/tests/)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from tropirag.clinical_engine.rules.rule_loader import load_rule_engine  # noqa: E402
from tropirag.clinical_engine.rules.rule_validator import validate_all  # noqa: E402

TESTS_DIR = PROJECT_ROOT / "rules" / "fever_travel" / "tests"

_URGENCY_ORDER = ["routine", "priority", "emergency", "immediate"]
_SEVERITY_ORDER = ["none", "mild", "moderate", "severe", "critical"]


def run_rule_fixtures() -> tuple[int, int, list[str]]:
    """Exécute toutes les fixtures YAML → (passées, total, erreurs)."""
    import yaml

    from tropirag.clinical_engine.orchestrator import ClinicalOrchestrator
    from tropirag.domain.clinical_case.builders import build_case

    orchestrator = ClinicalOrchestrator()
    files = sorted(TESTS_DIR.rglob("*.yaml"))
    passed = 0
    errors: list[str] = []
    for f in files:
        with open(f, encoding="utf-8") as fh:
            fixture = yaml.safe_load(fh) or {}
        name = fixture.get("name", f.stem)
        expect = fixture.get("expect", {}) or {}
        problems: list[str] = []
        try:
            analysis = orchestrator.analyze(build_case(fixture["case"]))
            matched = set(analysis.matched_rule_ids)
            for rid in expect.get("rules_include", []):
                if rid not in matched:
                    problems.append(f"règle attendue absente : {rid}")
            urg = analysis.safety.max_urgency.value
            if "urgency_at_least" in expect:
                if _URGENCY_ORDER.index(urg) < _URGENCY_ORDER.index(expect["urgency_at_least"]):
                    problems.append(f"urgence {urg} < attendu {expect['urgency_at_least']}")
            if "urgency_at_most" in expect:
                if _URGENCY_ORDER.index(urg) > _URGENCY_ORDER.index(expect["urgency_at_most"]):
                    problems.append(f"urgence {urg} > plafond {expect['urgency_at_most']}")
            sev = analysis.safety.max_severity.value
            if "severity_at_least" in expect:
                if _SEVERITY_ORDER.index(sev) < _SEVERITY_ORDER.index(expect["severity_at_least"]):
                    problems.append(f"sévérité {sev} < attendue {expect['severity_at_least']}")
            drugs = {str(getattr(d, "drug", d))
                     for d in getattr(analysis.rules, "drug_constraints", [])}
            for drug in expect.get("drugs_blocked_include", []):
                if drug not in drugs:
                    problems.append(f"contrainte médicamenteuse absente : {drug}")
            tests = {str(getattr(t, "test_code", "")) for t in
                     getattr(analysis.rules, "required_tests", [])}
            for code in expect.get("tests_include", []):
                if code not in tests:
                    problems.append(f"examen requis absent : {code}")
            if "isolation_required" in expect:
                if analysis.safety.isolation_required != bool(expect["isolation_required"]):
                    problems.append("isolement incohérent avec l'attente")
            if "notification_required" in expect:
                if analysis.safety.notify_public_health != bool(expect["notification_required"]):
                    problems.append("notification incohérente avec l'attente")
        except Exception as exc:  # fixture cassée = échec explicite
            problems.append(f"exception : {exc}")
        if problems:
            errors.append(f"{name} ({f.relative_to(PROJECT_ROOT)}): " + " ; ".join(problems))
        else:
            passed += 1
    return passed, len(files), errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Validation des règles TropiRAG")
    ap.add_argument("--with-tests", action="store_true",
                    help="exécuter aussi les fixtures comportementales YAML")
    args = ap.parse_args()

    errors = validate_all()
    eng = load_rule_engine()
    print(f"Règles chargées : {eng.count()} — empreinte {eng.fingerprint()}")
    if errors:
        print("ERREURS :")
        for e in errors:
            print("  ✗", e)
        return 1
    print("Lint clinique : aucune erreur.")

    if args.with_tests:
        passed, total, fixture_errors = run_rule_fixtures()
        print(f"Fixtures comportementales : {passed}/{total} passées")
        for e in fixture_errors:
            print("  ✗", e)
        if fixture_errors or total == 0:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
