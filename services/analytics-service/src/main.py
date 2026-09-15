from __future__ import annotations

import pathlib
import sys
from typing import Annotated

ROOT = pathlib.Path(__file__).resolve().parents[3]
for p in ("packages/medisuite-core", "packages/clinical-rules"):
    sys.path.insert(0, str(ROOT / p))

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy import JSON, String, select
from sqlalchemy.orm import Mapped, mapped_column

from medisuite_core import security
from medisuite_core import auth_deps
from medisuite_core.db import Base, engine_for, init_db, new_id
from medisuite_core.events import bus
from medisuite_core.http import create_service_app
from medisuite_core.rbac import can

app: FastAPI = create_service_app(
    "analytics-service", "Analytique & Épidémiologie", "KPIs inter-services, activité, épidémiologie (paludisme, VIH) — lecture seule.", module_label="Analytique & Épidémiologie")

engine = engine_for("analytics-service")
JWT_SECRET = "medisuite-dev-secret-change-in-prod"


def current_user(authorization: Annotated[str | None, Header()] = None) -> dict:
    """Identité : absent → anon ; jeton invalide/expiré → 401 (le portail
    déconnecte au lieu d'afficher un faux 403) ; valide → claims (RBAC)."""
    return auth_deps.bearer_identity(authorization, JWT_SECRET)


import json
import sqlite3

from medisuite_core.db import ROOT as MONO_ROOT


def _count(db_name: str, table: str) -> int | None:
    db = MONO_ROOT / "data" / f"{db_name}.db"
    if not db.exists():
        return None
    try:
        with sqlite3.connect(f"file:{db}?mode=ro", uri=True) as conn:
            return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    except sqlite3.Error:
        return None


@app.get("/api/v1/kpis", tags=["KPIs"])
def kpis() -> dict:
    """Agrégats lecture-seule sur les bases des autres services (database-per-service)."""
    return {
        "patients": _count("patient-service", "patients"),
        "consultations": _count("patient-service", "encounters"),
        "etudes_imagerie": _count("imaging-service", "studies"),
        "prescriptions_labo": _count("laboratory-service", "orders"),
        "resultats_valides": _count("laboratory-service", "results"),
        "comptes_rendus": _count("reporting-service", "reports"),
        "notes": "None = service jamais démarré (démarrage via make dev-up)",
    }


@app.get("/api/v1/activite", tags=["KPIs"])
def activite() -> dict:
    """Nombre d'événements par topic depuis le journal du bus (data/events.jsonl)."""
    sink = MONO_ROOT / "data" / "events.jsonl"
    topics: dict[str, int] = {}
    if sink.exists():
        for line in sink.read_text(encoding="utf-8").splitlines():
            try:
                t = json.loads(line)["topic"]
                topics[t] = topics.get(t, 0) + 1
            except (json.JSONDecodeError, KeyError):
                continue
    return {"par_topic": topics, "total": sum(topics.values())}


@app.get("/api/v1/epidemiologie/paludisme", tags=["épidémiologie"])
def paludisme() -> dict:
    """Suivi hebdomadaire synthétique (données déterministes de démonstration) —
    structure alignée sur les bulletins PNLP (Programme National de Lutte contre
    le Paludisme, Côte d'Ivoire)."""
    semaines = [f"S{i}" for i in range(1, 13)]
    cas = [320, 410, 380, 455, 512, 498, 560, 610, 585, 640, 700, 668]
    tdr_positifs = [round(c * 0.32) for c in cas]
    return {"annee": 2026, "semaines": semaines, "cas_suspects": cas,
            "tdr_positifs": tdr_positifs,
            "positivite_pct": round(100 * sum(tdr_positifs) / sum(cas), 1),
            "tendance": "hausse saisonnière (saison des pluies)"}


@app.get("/api/v1/epidemiologie/vih", tags=["épidémiologie"])
def vih() -> dict:
    """Indicateurs PTME simplifiés (UNAIDS 90-90-90)."""
    return {"diagnostiques_pct": 82, "sous_tar_pct": 76, "viro_supprimes_pct": 88,
            "source": "démonstration — brancher DHIS2 en production"}
