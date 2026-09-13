"""Oncologie (🎗️) — Module 03 MEDISUITE.

Dépistage multi-organes, BI-RADS, Fleischner, Lung-RADS, TNM AJCC 8e, ROMA, ECOG.

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
from medisuite_core.db import Base, engine_for, init_db, new_id
from medisuite_core.http import create_service_app
from medisuite_core.rbac import can
from medisuite_rules import oncology

app: FastAPI = create_service_app(
    "oncology-service", "Oncologie", "Dépistage multi-organes, BI-RADS, Fleischner, Lung-RADS, TNM AJCC 8e, ROMA, ECOG.",
    module_label="Module 03 · Oncologie")

engine = engine_for("oncology-service")
JWT_SECRET = "medisuite-dev-secret-change-in-prod"


def current_user(authorization: Annotated[str | None, Header()] = None) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        return {"sub": "anon", "role": ""}
    try:
        return security.jwt_decode(authorization.split(" ", 1)[1], JWT_SECRET)
    except security.JWTError:
        return {"sub": "anon", "role": ""}


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
        demo = [('Dépistage sein — mammographie suspecte', 'pat0001', 'KOUASSI Aya', 'BI-RADS 4 à documenter'), ('Tumor board — adénocarcinome colique', 'pat0002', 'KONÉ Ibrahim', 'Discussion RCP'), ('Suivi survivorship — tumeur stade II', 'pat0003', 'TRAORÉ Rokia', 'Contrôle 6 mois')]
        for i, (titre, pid, nom, note) in enumerate(demo, 1):
            db.add(Case(id=new_id(), patient_id=pid, patient_nom=nom,
                        date="2026-09-%02d" % i, titre=titre,
                        severite="", payload={"note": note}))
        db.commit()




@app.get("/module-info", tags=["module"])
def module_info() -> dict:
    return {"module": 3, "nom": "Oncologie", "service": "oncology-service",
            "scores": ['birads', 'fleischner', 'lung-rads', 'tnm-breast', 'roma', 'ecog'],
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




@app.post("/api/v1/scores/birads", tags=["scores cliniques"])
def score_birads(body: dict, user: dict = Depends(current_user)) -> dict:
    """Score birads — medisuite_rules.oncology"""
    try:
        result = oncology.birads(**body)
    except TypeError as exc:
        raise HTTPException(422, f"paramètres invalides : {exc}")
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    return {"score_endpoint": "birads", "resultat": result,
            "moteur": "medisuite_rules.oncology"}


@app.post("/api/v1/scores/fleischner", tags=["scores cliniques"])
def score_fleischner(body: dict, user: dict = Depends(current_user)) -> dict:
    """Score fleischner — medisuite_rules.oncology"""
    try:
        result = oncology.fleischner(**body)
    except TypeError as exc:
        raise HTTPException(422, f"paramètres invalides : {exc}")
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    return {"score_endpoint": "fleischner", "resultat": result,
            "moteur": "medisuite_rules.oncology"}


@app.post("/api/v1/scores/lung_rads", tags=["scores cliniques"])
def score_lung_rads(body: dict, user: dict = Depends(current_user)) -> dict:
    """Score lung-rads — medisuite_rules.oncology"""
    try:
        result = oncology.lung_rads(**body)
    except TypeError as exc:
        raise HTTPException(422, f"paramètres invalides : {exc}")
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    return {"score_endpoint": "lung_rads", "resultat": result,
            "moteur": "medisuite_rules.oncology"}


@app.post("/api/v1/scores/tnm_breast", tags=["scores cliniques"])
def score_tnm_breast(body: dict, user: dict = Depends(current_user)) -> dict:
    """Score tnm-breast — medisuite_rules.oncology"""
    try:
        result = oncology.tnm_breast_stage(**body)
    except TypeError as exc:
        raise HTTPException(422, f"paramètres invalides : {exc}")
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    return {"score_endpoint": "tnm_breast", "resultat": result,
            "moteur": "medisuite_rules.oncology"}


@app.post("/api/v1/scores/roma", tags=["scores cliniques"])
def score_roma(body: dict, user: dict = Depends(current_user)) -> dict:
    """Score roma — medisuite_rules.oncology"""
    try:
        result = oncology.roma_score(**body)
    except TypeError as exc:
        raise HTTPException(422, f"paramètres invalides : {exc}")
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    return {"score_endpoint": "roma", "resultat": result,
            "moteur": "medisuite_rules.oncology"}


@app.post("/api/v1/scores/ecog", tags=["scores cliniques"])
def score_ecog(body: dict, user: dict = Depends(current_user)) -> dict:
    """Score ecog — medisuite_rules.oncology"""
    try:
        result = oncology.ecog(**body)
    except TypeError as exc:
        raise HTTPException(422, f"paramètres invalides : {exc}")
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    return {"score_endpoint": "ecog", "resultat": result,
            "moteur": "medisuite_rules.oncology"}

