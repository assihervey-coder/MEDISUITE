"""Pneumologie (🫁) — Module 09 MEDISUITE.

Nodules (Fleischner/Lung-RADS), TB OMS (endémie), BPCO GOLD, SAOS STOP-BANG, spirométrie.

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
from medisuite_rules import pneumology

app: FastAPI = create_service_app(
    "pneumology-service", "Pneumologie", "Nodules (Fleischner/Lung-RADS), TB OMS (endémie), BPCO GOLD, SAOS STOP-BANG, spirométrie.",
    module_label="Module 09 · Pneumologie")

engine = engine_for("pneumology-service")
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
        demo = [('Toux chronique — interrogation TB', 'pat0019', 'KOUAMÉ Prisca', 'GeneXpert demandé'), ('BPCO suivi annuel', 'pat0020', 'BECHIO Charles', 'GOLD E'), ('Ronflements + somnolence', 'pat0021', 'TANOH Paul', 'STOP-BANG')]
        for i, (titre, pid, nom, note) in enumerate(demo, 1):
            db.add(Case(id=new_id(), patient_id=pid, patient_nom=nom,
                        date="2026-09-%02d" % i, titre=titre,
                        severite="", payload={"note": note}))
        db.commit()




@app.get("/module-info", tags=["module"])
def module_info() -> dict:
    return {"module": 9, "nom": "Pneumologie", "service": "pneumology-service",
            "scores": ['gold', 'stop-bang', 'tb-oms', 'spirometrie'],
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




@app.post("/api/v1/scores/gold", tags=["scores cliniques"])
def score_gold(body: dict, user: dict = Depends(current_user)) -> dict:
    """Score gold — medisuite_rules.pneumology"""
    try:
        result = pneumology.gold_group(**body)
    except TypeError as exc:
        raise HTTPException(422, f"paramètres invalides : {exc}")
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    return {"score_endpoint": "gold", "resultat": result,
            "moteur": "medisuite_rules.pneumology"}


@app.post("/api/v1/scores/stop_bang", tags=["scores cliniques"])
def score_stop_bang(body: dict, user: dict = Depends(current_user)) -> dict:
    """Score stop-bang — medisuite_rules.pneumology"""
    try:
        result = pneumology.stop_bang(**body)
    except TypeError as exc:
        raise HTTPException(422, f"paramètres invalides : {exc}")
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    return {"score_endpoint": "stop_bang", "resultat": result,
            "moteur": "medisuite_rules.pneumology"}


@app.post("/api/v1/scores/tb_oms", tags=["scores cliniques"])
def score_tb_oms(body: dict, user: dict = Depends(current_user)) -> dict:
    """Score tb-oms — medisuite_rules.pneumology"""
    try:
        result = pneumology.tb_who_screen(**body)
    except TypeError as exc:
        raise HTTPException(422, f"paramètres invalides : {exc}")
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    return {"score_endpoint": "tb_oms", "resultat": result,
            "moteur": "medisuite_rules.pneumology"}


@app.post("/api/v1/scores/spirometrie", tags=["scores cliniques"])
def score_spirometrie(body: dict, user: dict = Depends(current_user)) -> dict:
    """Score spirometrie — medisuite_rules.pneumology"""
    try:
        result = pneumology.spirometry_interpretation(**body)
    except TypeError as exc:
        raise HTTPException(422, f"paramètres invalides : {exc}")
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    return {"score_endpoint": "spirometrie", "resultat": result,
            "moteur": "medisuite_rules.pneumology"}

