"""Urgences (🚨) — Module 26 MEDISUITE.

ESI/CTMP, qSOFA, Wells PE, Parkland, ISS, CURB-65, code AVC/STEMI, choc ATLS.

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
from medisuite_rules import emergency
from medisuite_rules import triage

app: FastAPI = create_service_app(
    "emergency-service", "Urgences", "ESI/CTMP, qSOFA, Wells PE, Parkland, ISS, CURB-65, code AVC/STEMI, choc ATLS.",
    module_label="Module 26 · Urgences")

engine = engine_for("emergency-service")
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
        demo = [('Polytraumatisé — Baie 2', 'pat0070', 'GOULY Franck', 'ISS + choc'), ('Détresse respiratoire fébrile', 'pat0071', 'YAPI Bénédicte', 'qSOFA + CURB-65'), ('Brûlure ébullition 25 %', 'pat0072', 'BAH Sékou', 'Parkland')]
        for i, (titre, pid, nom, note) in enumerate(demo, 1):
            db.add(Case(id=new_id(), patient_id=pid, patient_nom=nom,
                        date="2026-09-%02d" % i, titre=titre,
                        severite="", payload={"note": note}))
        db.commit()




@app.get("/module-info", tags=["module"])
def module_info() -> dict:
    return {"module": 26, "nom": "Urgences", "service": "emergency-service",
            "scores": ['esi', 'ctmp', 'qsofa', 'parkland', 'curbs65', 'shock-index'],
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




@app.post("/api/v1/scores/esi", tags=["scores cliniques"])
def score_esi(body: dict, user: dict = Depends(current_user)) -> dict:
    """Score esi — medisuite_rules.triage"""
    try:
        result = triage.esi(**body)
    except TypeError as exc:
        raise HTTPException(422, f"paramètres invalides : {exc}")
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    return {"score_endpoint": "esi", "resultat": result,
            "moteur": "medisuite_rules.triage"}


@app.post("/api/v1/scores/ctmp", tags=["scores cliniques"])
def score_ctmp(body: dict, user: dict = Depends(current_user)) -> dict:
    """Score ctmp — medisuite_rules.triage"""
    try:
        result = triage.ctmp(**body)
    except TypeError as exc:
        raise HTTPException(422, f"paramètres invalides : {exc}")
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    return {"score_endpoint": "ctmp", "resultat": result,
            "moteur": "medisuite_rules.triage"}


@app.post("/api/v1/scores/qsofa", tags=["scores cliniques"])
def score_qsofa(body: dict, user: dict = Depends(current_user)) -> dict:
    """Score qsofa — medisuite_rules.triage"""
    try:
        result = triage.qsofa(**body)
    except TypeError as exc:
        raise HTTPException(422, f"paramètres invalides : {exc}")
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    return {"score_endpoint": "qsofa", "resultat": result,
            "moteur": "medisuite_rules.triage"}


@app.post("/api/v1/scores/parkland", tags=["scores cliniques"])
def score_parkland(body: dict, user: dict = Depends(current_user)) -> dict:
    """Score parkland — medisuite_rules.emergency"""
    try:
        result = emergency.parkland(**body)
    except TypeError as exc:
        raise HTTPException(422, f"paramètres invalides : {exc}")
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    return {"score_endpoint": "parkland", "resultat": result,
            "moteur": "medisuite_rules.emergency"}


@app.post("/api/v1/scores/curbs65", tags=["scores cliniques"])
def score_curbs65(body: dict, user: dict = Depends(current_user)) -> dict:
    """Score curbs65 — medisuite_rules.emergency"""
    try:
        result = emergency.curbs65(**body)
    except TypeError as exc:
        raise HTTPException(422, f"paramètres invalides : {exc}")
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    return {"score_endpoint": "curbs65", "resultat": result,
            "moteur": "medisuite_rules.emergency"}


@app.post("/api/v1/scores/shock_index", tags=["scores cliniques"])
def score_shock_index(body: dict, user: dict = Depends(current_user)) -> dict:
    """Score shock-index — medisuite_rules.emergency"""
    try:
        result = emergency.shock_index(**body)
    except TypeError as exc:
        raise HTTPException(422, f"paramètres invalides : {exc}")
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    return {"score_endpoint": "shock_index", "resultat": result,
            "moteur": "medisuite_rules.emergency"}

