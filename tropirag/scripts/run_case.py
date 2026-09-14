#!/usr/bin/env python3
"""TropiRAG — exécution d'un cas en CLI.

Usage :
    python scripts/run_case.py --scenario fever_travel_ci
    python scripts/run_case.py --json '{"patient": {...}, ...}'
    python scripts/run_case.py --file case.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tropirag.core.datetime import local_now  # noqa: E402
from tropirag.response_engine.response_orchestrator import process_case  # noqa: E402

SCENARIOS = {
    "fever_travel_ci": lambda: {
        "patient": {"age_years": 34, "sex": "male"},
        "free_text": "fièvre 39,6 depuis 4 jours, frissons, vomissements importants, céphalées",
        "travel": {"segments": [{"country": "CI", "region": "Abidjan",
                                 "rural_stay": True, "departure": days_ago(9)}]},
        "vitals": {"temperature_c": 39.6},
    },
    "severe_malaria": lambda: {
        "patient": {"age_years": 42},
        "free_text": "fièvre 40,2, convulsions puis coma, prostration",
        "travel": {"segments": [{"country": "BF", "rural_stay": True, "departure": days_ago(8)}]},
        "vitals": {"temperature_c": 40.2},
    },
    "dengue_warning": lambda: {
        "patient": {"age_years": 29},
        "free_text": "fièvre, douleur derrière les yeux, douleurs abdominales intenses, vomissements incoercibles",
        "travel": {"segments": [{"country": "CI", "region": "Abidjan", "departure": days_ago(10)}]},
    },
    "vhf_guinea": lambda: {
        "patient": {"age_years": 31},
        "free_text": "fièvre 39, myalgies, saignements des gencives",
        "travel": {"segments": [{"country": "GN", "departure": days_ago(15),
                                   "burial_attended": True}]},
    },
    "meningitis": lambda: {
        "patient": {"age_years": 19},
        "free_text": "fièvre 40, raideur de nuque, vomissements, photophobie",
    },
}


def days_ago(n: int) -> str:
    return (local_now().date() - timedelta(days=n)).isoformat()


def main() -> int:
    ap = argparse.ArgumentParser(description="TropiRAG — exécuter un cas clinique")
    ap.add_argument("--scenario", choices=sorted(SCENARIOS))
    ap.add_argument("--json", help="payload JSON direct")
    ap.add_argument("--file", help="chemin d'un fichier JSON")
    ap.add_argument("--no-ai", action="store_true", help="désactiver la synthèse IA")
    args = ap.parse_args()

    if args.json:
        payload = json.loads(args.json)
    elif args.file:
        payload = json.loads(Path(args.file).read_text(encoding="utf-8"))
    elif args.scenario:
        payload = SCENARIOS[args.scenario]()
    else:
        ap.error("fournir --scenario, --json ou --file")

    r = process_case(payload, use_ai=not args.no_ai)

    bar = "─" * 74
    print(bar)
    print(f"  TropiRAG — ANALYSE CLINIQUE  |  cas {r.case_id}")
    print(bar)
    print(f"  URGENCY: {r.urgency.upper()}   SEVERITY: {r.severity.upper()}   "
          f"AI: {r.ai_layer}")
    print(bar)
    print(r.narrative)
    if r.citations:
        print("\n  PREUVES CITÉES :")
        for c in r.citations:
            print(f"  {c['marker']} {c['full']}")
    if r.matched_rule_ids:
        print(f"\n  ({len(r.matched_rule_ids)} règles appliquées : "
              f"{', '.join(r.matched_rule_ids[:8])}…)")
    print(bar)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
