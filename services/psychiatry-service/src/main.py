"""Psychiatrie (🧬) — Module 14 MEDISUITE.

PHQ-9, GAD-7, C-SSRS, AUDIT-C, Y-BOCS, biomarqueurs vocaux (prototype).

Scores cliniques disponibles via POST /api/v1/scores/{nom} — la logique provient
du moteur central packages/clinical-rules (source unique, testée, référencée).
"""
from __future__ import annotations

import pathlib
import sys
from typing import Annotated, Any

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
from medisuite_core.http import create_service_app
from medisuite_core.rbac import can
from medisuite_rules import psy_geriatrie

app: FastAPI = create_service_app(
    "psychiatry-service", "Psychiatrie", "PHQ-9, GAD-7, C-SSRS, AUDIT-C, Y-BOCS, biomarqueurs vocaux (prototype).",
    module_label="Module 14 · Psychiatrie")

engine = engine_for("psychiatry-service")
JWT_SECRET = "medisuite-dev-secret-change-in-prod"


def current_user(authorization: Annotated[str | None, Header()] = None) -> dict:
    """Identité : absent → anon ; jeton invalide/expiré → 401 (le portail
    déconnecte au lieu d'afficher un faux 403) ; valide → claims (RBAC)."""
    return auth_deps.bearer_identity(authorization, JWT_SECRET)


class Case(Base):
    __tablename__ = "cases"
    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    patient_id: Mapped[str] = mapped_column(String(16), index=True)
    patient_nom: Mapped[str] = mapped_column(String(120), default="")
    date: Mapped[str] = mapped_column(String(10))
    titre: Mapped[str] = mapped_column(String(200))
    severite: Mapped[str] = mapped_column(String(20), default="")
    statut: Mapped[str] = mapped_column(String(20), default="actif")
    payload: Mapped[dict] = mapped_column(JSON, default=dict)


SessionLocal = init_db(engine, Base.metadata)


class CaseIn(BaseModel):
    patient_id: str
    patient_nom: str = ""
    date: str = ""
    titre: str
    severite: str = ""
    payload: dict = {}


def seed() -> None:
    with SessionLocal() as db:
        if db.scalar(select(Case).limit(1)):
            return
        demo = [('Épisode dépressif — évaluation', 'pat0034', 'GNAKOU Alice', 'PHQ-9'), ('Attaques de panique', 'pat0035', 'LOUGUE Emmanuel', 'GAD-7'), ('Addiction alcool', 'pat0036', 'DJE Kouadio', 'AUDIT-C')]
        for i, (titre, pid, nom, note) in enumerate(demo, 1):
            db.add(Case(id=new_id(), patient_id=pid, patient_nom=nom,
                        date="2026-09-%02d" % i, titre=titre,
                        severite="", payload={"note": note}))
        db.commit()




@app.get("/module-info", tags=["module"])
def module_info() -> dict:
    return {"module": 14, "nom": "Psychiatrie", "service": "psychiatry-service",
            "scores": ['phq9', 'gad7', 'cssrs', 'audit-c'],
            "moteur": "packages/clinical-rules (source unique de vérité)"}


@app.get("/api/v1/cases", tags=["cas cliniques"])
def list_cases(user: dict = Depends(current_user)) -> list[dict]:
    if not can(user.get("role", ""), "patient.read"):
        raise HTTPException(403, "permission patient.read requise")
    seed()
    with SessionLocal() as db:
        return [{col.name: getattr(c, col.name) for col in c.__table__.columns}
                for c in db.scalars(select(Case))]


@app.post("/api/v1/cases", status_code=201, tags=["cas cliniques"])
def create_case(body: CaseIn, user: dict = Depends(current_user)) -> dict:
    if not can(user.get("role", ""), "patient.write"):
        raise HTTPException(403, "permission patient.write requise")
    with SessionLocal() as db:
        c = Case(id=new_id(), **body.model_dump())
        db.add(c)
        db.commit()
        return {k.name: getattr(c, k.name) for k in c.__table__.columns}


@app.post("/api/v1/cases/{cid}/close", tags=["cas cliniques"])
def close_case(cid: str, user: dict = Depends(current_user)) -> dict:
    with SessionLocal() as db:
        c = db.get(Case, cid)
        if not c:
            raise HTTPException(404, "cas introuvable")
        c.statut = "clos"
        db.commit()
        return {"id": cid, "statut": "clos"}




@app.post("/api/v1/scores/phq9", tags=["scores cliniques"])
def score_phq9(body: dict, user: dict = Depends(current_user)) -> dict:
    """Score phq9 — medisuite_rules.psy_geriatrie"""
    try:
        result = psy_geriatrie.phq9(**body)
    except TypeError as exc:
        raise HTTPException(422, f"paramètres invalides : {exc}")
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    return {"score_endpoint": "phq9", "resultat": result,
            "moteur": "medisuite_rules.psy_geriatrie"}


@app.post("/api/v1/scores/gad7", tags=["scores cliniques"])
def score_gad7(body: dict, user: dict = Depends(current_user)) -> dict:
    """Score gad7 — medisuite_rules.psy_geriatrie"""
    try:
        result = psy_geriatrie.gad7(**body)
    except TypeError as exc:
        raise HTTPException(422, f"paramètres invalides : {exc}")
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    return {"score_endpoint": "gad7", "resultat": result,
            "moteur": "medisuite_rules.psy_geriatrie"}


@app.post("/api/v1/scores/cssrs", tags=["scores cliniques"])
def score_cssrs(body: dict, user: dict = Depends(current_user)) -> dict:
    """Score cssrs — medisuite_rules.psy_geriatrie"""
    try:
        result = psy_geriatrie.cssrs_risk(**body)
    except TypeError as exc:
        raise HTTPException(422, f"paramètres invalides : {exc}")
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    return {"score_endpoint": "cssrs", "resultat": result,
            "moteur": "medisuite_rules.psy_geriatrie"}


@app.post("/api/v1/scores/audit_c", tags=["scores cliniques"])
def score_audit_c(body: dict, user: dict = Depends(current_user)) -> dict:
    """Score audit-c — medisuite_rules.psy_geriatrie"""
    try:
        result = psy_geriatrie.audit_c(**body)
    except TypeError as exc:
        raise HTTPException(422, f"paramètres invalides : {exc}")
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    return {"score_endpoint": "audit_c", "resultat": result,
            "moteur": "medisuite_rules.psy_geriatrie"}

