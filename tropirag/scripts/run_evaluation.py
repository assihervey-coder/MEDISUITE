#!/usr/bin/env python3
"""Runner maître d'évaluation — exécute les suites et agrège les verdicts.

Usage :
    python scripts/run_evaluation.py                     # toutes les suites
    python scripts/run_evaluation.py --suite retrieval
    python scripts/run_evaluation.py --suite retrieval,safety
    python scripts/run_evaluation.py --list

Suites : retrieval | grounding | clinical | ai | safety
Rapports : evaluation/reports/<suite>/<suite>_report.{json,md}
Code de sortie : 0 si tout passe, 1 sinon (utilisable en CI).
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT))

SUITES = {
    "retrieval": ("evaluation.retrieval.benchmark", "run"),
    "grounding": ("evaluation.grounding.evidence_coverage", "run"),
    "grounding:citations": ("evaluation.grounding.citation_accuracy", "run"),
    "grounding:unsupported": ("evaluation.grounding.unsupported_claims", "run"),
    "clinical:accuracy": ("evaluation.clinical.case_accuracy", "run"),
    "clinical:differential": ("evaluation.clinical.differential_quality", "run"),
    "clinical:temporal": ("evaluation.clinical.temporal_quality", "run"),
    "clinical:escalation": ("evaluation.clinical.escalation_quality", "run"),
    "ai:models": ("evaluation.ai.model_benchmark", "run"),
    "ai:routing": ("evaluation.ai.routing_benchmark", "run"),
    "ai:latency": ("evaluation.ai.latency", "run"),
    "ai:memory": ("evaluation.ai.memory_usage", "run"),
    "ai:failure": ("evaluation.ai.failure_rate", "run"),
    "safety:invariants": ("evaluation.safety.safety_benchmark", "run"),
    "safety:refusal": ("evaluation.safety.refusal_benchmark", "run"),
    "safety:hallucination": ("evaluation.safety.hallucination_benchmark", "run"),
    "safety:dangerous": ("evaluation.safety.dangerous_output_detection", "run"),
}

GROUPS = {
    "retrieval": ["retrieval"],
    "grounding": ["grounding", "grounding:citations", "grounding:unsupported"],
    "clinical": ["clinical:accuracy", "clinical:differential",
                 "clinical:temporal", "clinical:escalation"],
    "ai": ["ai:models", "ai:routing", "ai:latency", "ai:memory", "ai:failure"],
    "safety": ["safety:invariants", "safety:refusal",
               "safety:hallucination", "safety:dangerous"],
}


def resolve(selections: list[str]) -> list[str]:
    out: list[str] = []
    for sel in selections:
        if sel == "all":
            out.extend(SUITES.keys())
        elif sel in GROUPS:
            out.extend(GROUPS[sel])
        elif sel in SUITES:
            out.append(sel)
        else:
            print(f"✗ suite inconnue : {sel}")
            sys.exit(1)
    seen: set[str] = set()
    return [s for s in out if not (s in seen or seen.add(s))]


def run_suite(name: str):
    import importlib

    module_path, fn = SUITES[name]
    mod = importlib.import_module(module_path)
    return getattr(mod, fn)()


def main() -> int:
    ap = argparse.ArgumentParser(description="Évaluation scientifique TropiRAG")
    ap.add_argument("--suite", default="all",
                    help="suites séparées par virgules (all|retrieval|grounding|"
                         "clinical|ai|safety ou granulaire, voir --list)")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    if args.list:
        print("Suites disponibles :")
        for name in SUITES:
            print(f"  {name:28s} → evaluation/reports/{name.split(':')[0]}/")
        return 0

    selections = [s.strip() for s in args.suite.split(",") if s.strip()]
    names = resolve(selections or ["all"])

    print(f"═══ TROPIRAG ÉVALUATION — {len(names)} suite(s) ═══")
    results = []
    overall_ok = True
    for name in names:
        t0 = time.perf_counter()
        try:
            report = run_suite(name)
        except Exception as exc:
            print(f"[✗] {name:28s} ERREUR : {exc}")
            overall_ok = False
            continue
        elapsed = time.perf_counter() - t0
        status = "✓ PASS" if report.passed else "✗ FAIL"
        print(f"[{status}] {name:28s} {elapsed:6.1f}s")
        for m in report.metrics:
            flag = "  ✓" if m.passed else "  ✗"
            print(f"{flag} {m.name:34s} {m.value:.4f} (seuil {m.threshold:.2f})")
        if not report.passed:
            overall_ok = False
        results.append((name, report.passed))

    print("═══" + ("═" * 40))
    if results:
        print(f"Verdict global : {'PASS ✔' if overall_ok else 'FAIL ✘'} "
              f"({sum(1 for _, p in results if p)}/{len(results)} suites)")
    return 0 if overall_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
