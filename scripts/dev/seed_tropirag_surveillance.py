#!/usr/bin/env python3
"""Seed de démonstration — surveillance d'éclosions TropiRAG → Épidémiologie.

Injecte dans la base TropiRAG du monorepo (data/tropirag.db) un jeu de cas
démo antidatés sur ~3 semaines et 5 districts sanitaires CI + cas non
localisés, afin que la carte /api/v1/surveillance/map et l'écran Épidémiologie
du portail affichent des signaux d'éclosion réalistes.

GARANTIES :
  - chaque cas est réellement ANALYSÉ par le moteur de règles déterministe
    (ResponseOrchestrator.process, use_ai=False) — les différentiels, urgences
    et gravités persistés viennent du rule engine, jamais inventés ;
  - seules les horodatages sont antidatés (created_at) pour produire des
    courbes hebdomadaires multi-semaines (détection last_week ≥ prev+2) ;
  - IDÉMPOTENT : purge d'abord les case_id « CASE-SURV-% » (legacy + ORM).

Usage :  PYTHONPATH=tropirag python scripts/dev/seed_tropirag_surveillance.py
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("TROPIRAG_ROOT", str(ROOT / "tropirag"))
os.environ.setdefault("TROPIRAG_DB_PATH", str(ROOT / "data" / "tropirag.db"))
os.environ.setdefault("TROPIRAG_DATA_DIR", str(ROOT / "tropirag"))
sys.path.insert(0, str(ROOT / "tropirag"))

SURV_PREFIX = "CASE-SURV-"

# ---------------------------------------------------------------------------
# Archétypes cliniques (payloads identiques à POST /api/v1/cases)
# ---------------------------------------------------------------------------
P_MALARIO = "malaria_uncomplicated"
P_DENGUE = "dengue_suspected"
P_TYPHOIDE = "typhoid_suspected"
P_MALARIO_SEVERE = "malaria_severe"

ARCHETYPES: dict[str, dict] = {
    P_MALARIO: {
        "patient": {"age": 27, "sex": "male", "pregnant": "not_applicable"},
        "symptoms": [{"code": "fever"}, {"code": "headache"},
                     {"code": "myalgia"}, {"code": "chills"}],
        "vitals": {"temperature_c": 38.6},
        "lab_results": [{"test": "rdt_malaria", "value": "positif"}],
    },
    P_MALARIO_SEVERE: {
        "patient": {"age": 34, "sex": "female", "pregnant": "not_pregnant"},
        "symptoms": [{"code": "fever"}, {"code": "vomiting"},
                     {"code": "fatigue"}, {"code": "jaundice"}],
        "vitals": {"temperature_c": 39.4},
        "lab_results": [{"test": "rdt_malaria", "value": "positif"}],
    },
    P_DENGUE: {
        "patient": {"age": 19, "sex": "female", "pregnant": "not_pregnant"},
        "symptoms": [{"code": "fever"}, {"code": "headache"},
                     {"code": "rash"}, {"code": "myalgia"},
                     {"code": "nausea"}],
        "vitals": {"temperature_c": 39.1},
        "lab_results": [{"test": "rdt_malaria", "value": "negatif"}],
    },
    P_TYPHOIDE: {
        "patient": {"age": 41, "sex": "male", "pregnant": "not_applicable"},
        "symptoms": [{"code": "fever"}, {"code": "abdominal_pain"},
                     {"code": "diarrhea"}, {"code": "fatigue"}],
        "vitals": {"temperature_c": 38.4},
        "lab_results": [],
    },
}

# ---------------------------------------------------------------------------
# Distribution démo : district → {semaine relative (0 = en cours) → [(archétype, region), ...]}
# Objectif : 2 signaux d'éclosion (Abidjan, Vallée du Bandama — Bouaké),
# 1 district stable (Daloa), 2 districts peu actifs, cas non localisés.
# ---------------------------------------------------------------------------
DISTRICT_PLAN: dict[str, dict[int, list[tuple[str, str]]]] = {
    "abidjan": {
        -2: [(P_MALARIO, "Abidjan"), (P_MALARIO, "Abidjan"),
             (P_DENGUE, "Abidjan")],
        -1: [(P_MALARIO, "Abidjan"), (P_DENGUE, "Abidjan"),
             (P_MALARIO, "Abidjan"), (P_TYPHOIDE, "Abidjan")],
        0:  [(P_DENGUE, "Abidjan"), (P_MALARIO, "Abidjan"),
             (P_DENGUE, "Abidjan"), (P_MALARIO, "Abidjan"),
             (P_DENGUE, "Abidjan"), (P_MALARIO_SEVERE, "Abidjan"),
             (P_MALARIO, "Abidjan")],
    },
    "vallee-du-bandama": {
        -1: [(P_MALARIO, "Bouaké"), (P_MALARIO, "Bouaké")],
        0:  [(P_MALARIO, "Bouaké"), (P_MALARIO_SEVERE, "Bouaké"),
             (P_MALARIO, "Bouaké"), (P_TYPHOIDE, "Bouaké")],
    },
    "sassandra-marahoue": {
        -1: [(P_MALARIO, "Daloa"), (P_DENGUE, "Daloa"), (P_MALARIO, "Daloa")],
        0:  [(P_MALARIO, "Daloa"), (P_MALARIO, "Daloa"), (P_DENGUE, "Daloa")],
    },
    "bas-sassandra": {
        0: [(P_MALARIO, "San Pedro"), (P_TYPHOIDE, "San Pedro")],
    },
    "yamoussoukro": {
        0: [(P_MALARIO, "Yamoussoukro")],
    },
    "__non_localises__": {
        0: [(P_MALARIO, ""), (P_DENGUE, "")],  # région absente → non résolue
    },
}


def iso_stamp(week_off: int, weekday: int, hour: int) -> str:
    """Horodatage ISO de la semaine (0 = semaine courante), jour 1-7, heure 0-23."""
    from datetime import datetime

    iso = today().isocalendar()
    d = datetime.fromisocalendar(iso[0], iso[1] + week_off, weekday)
    return d.strftime("%Y-%m-%d") + f"T{hour:02d}:00:00"


def today() -> dt.date:
    return dt.date.today()


MANIFEST = ROOT / "data" / "tropirag-surv-seed.json"


def purge(db) -> None:
    """Supprime les seeds précédents (IDs listés dans le manifeste)."""
    ids: list[str] = []
    if MANIFEST.exists():
        try:
            ids = json.loads(MANIFEST.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            ids = []
    if not ids:
        print("  (aucun seed antérieur à purger)")
        return
    for table in ("cases", "analyses", "evidence_usage",
                  "patients", "clinical_cases", "travel", "symptoms",
                  "diagnoses", "diagnostic_tests", "medications"):
        try:
            for cid in ids:
                db.execute(f"DELETE FROM {table} WHERE case_id=?", (cid,))
        except Exception as exc:  # table ORM éventuellement absente
            print(f"  (purge {table} ignorée : {exc})")
    print(f"  (purge de {len(ids)} seeds antérieurs)")


def main() -> int:
    from tropirag.api.routes.clinical import get_orchestrator
    from tropirag.integrations.surveillance import OutbreakMonitor
    from tropirag.persistence.database import Database
    from tropirag.persistence.repositories.case_repository import CaseRepository

    db = Database.instance()
    purge(db)

    orch = get_orchestrator()
    repo = CaseRepository(db)
    n = 0
    seeded_ids: list[str] = []

    for _district, weeks in DISTRICT_PLAN.items():
        for week_off, entries in weeks.items():
            for idx, (arch, region) in enumerate(entries):
                n += 1
                payload = dict(ARCHETYPES[arch])
                payload["symptom_codes"] = [s["code"] for s in payload["symptoms"]]
                payload["travel"] = {"segments": [
                    {"country": "CI", "region": region or None,
                     "rural_stay": False, "forest_stay": False,
                     "stagnant_water": False}]}
                payload["free_text"] = None

                r = orch.process(dict(payload), language="fr", use_ai=False)
                cid = r.case_id  # ID généré par l'orchestrateur — référence unique
                seeded_ids.append(cid)
                repo.save_case(cid, payload.get("patient") or {}, payload)
                repo.save_analysis(cid, r.urgency, r.severity,
                                   r.differentials, r.matched_rule_ids,
                                   r.ai_layer, r.refusal)

                # antidatage par semaine ISO explicite (bucket hebdo exact) —
                # semaine courante : lundi uniquement (jamais d'horodatage futur)
                weekday = 1 if week_off == 0 else 1 + (idx % 6)
                stamp = iso_stamp(week_off, weekday, 7 + (idx * 2) % 15)
                db.execute("UPDATE cases SET created_at=? WHERE case_id=?",
                           (stamp, cid))
                db.execute("UPDATE analyses SET created_at=? WHERE case_id=?",
                           (stamp, cid))

    MANIFEST.write_text(json.dumps(seeded_ids), encoding="utf-8")

    snapshot = OutbreakMonitor(db).clusters(days=30)
    print(f"✓ {n} cas démo injectés et analysés (règles déterministes)")
    print(f"  total 30 j : {snapshot['total_cases']} — non localisés : "
          f"{snapshot['non_localises']['cases']}")
    print("  national :", snapshot["national_by_disease"])
    for o in snapshot["outbreaks"]:
        print(f"  ⚠ éclosion {o['label']} : {o['cases_last_week']} cas "
              f"(S{o['last_week'].split('W')[1]}) vs {o['cases_previous_week']} — "
              f"{o['top_disease']}")
    if not snapshot["outbreaks"]:
        print("  (aucun signal — vérifier la distribution des semaines)")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
