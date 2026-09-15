"""Neurologie (🧠) — Module 13 MEDISUITE.

AVC (ASPECTS/NIHSS), épilepsie, cognition (MMSE/MoCA), SEP (McDonald/EDSS), Parkinson.

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
from medisuite_rules import neurology

app: FastAPI = create_service_app(
    "neurology-service", "Neurologie", "AVC (ASPECTS/NIHSS), épilepsie, cognition (MMSE/MoCA), SEP (McDonald/EDSS), Parkinson.",
    module_label="Module 13 · Neurologie")

engine = engine_for("neurology-service")
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
        demo = [('Code AVC — IRM 22 min', 'pat0031', 'SORO Adama', 'ASPECTS + NIHSS'), ('Troubles mnésiques 65 ans', 'pat0032', 'ALLA Christine', 'MMSE + MoCA'), ('Suspicion SEP', 'pat0033', 'DIABATE Salif', 'McDonald 2017')]
        for i, (titre, pid, nom, note) in enumerate(demo, 1):
            db.add(Case(id=new_id(), patient_id=pid, patient_nom=nom,
                        date="2026-09-%02d" % i, titre=titre,
                        severite="", payload={"note": note}))
        db.commit()




@app.get("/module-info", tags=["module"])
def module_info() -> dict:
    return {"module": 13, "nom": "Neurologie", "service": "neurology-service",
            "scores": ['aspects', 'nihss', 'mmse', 'mcdonald'],
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




@app.post("/api/v1/scores/aspects", tags=["scores cliniques"])
def score_aspects(body: dict, user: dict = Depends(current_user)) -> dict:
    """Score aspects — medisuite_rules.neurology"""
    try:
        result = neurology.aspects(**body)
    except TypeError as exc:
        raise HTTPException(422, f"paramètres invalides : {exc}")
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    return {"score_endpoint": "aspects", "resultat": result,
            "moteur": "medisuite_rules.neurology"}


@app.post("/api/v1/scores/nihss", tags=["scores cliniques"])
def score_nihss(body: dict, user: dict = Depends(current_user)) -> dict:
    """Score nihss — medisuite_rules.neurology"""
    try:
        result = neurology.nihss(**body)
    except TypeError as exc:
        raise HTTPException(422, f"paramètres invalides : {exc}")
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    return {"score_endpoint": "nihss", "resultat": result,
            "moteur": "medisuite_rules.neurology"}


@app.post("/api/v1/scores/mmse", tags=["scores cliniques"])
def score_mmse(body: dict, user: dict = Depends(current_user)) -> dict:
    """Score mmse — medisuite_rules.neurology"""
    try:
        result = neurology.mmse(**body)
    except TypeError as exc:
        raise HTTPException(422, f"paramètres invalides : {exc}")
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    return {"score_endpoint": "mmse", "resultat": result,
            "moteur": "medisuite_rules.neurology"}


@app.post("/api/v1/scores/mcdonald", tags=["scores cliniques"])
def score_mcdonald(body: dict, user: dict = Depends(current_user)) -> dict:
    """Score mcdonald — medisuite_rules.neurology"""
    try:
        result = neurology.mcdonald_ms(**body)
    except TypeError as exc:
        raise HTTPException(422, f"paramètres invalides : {exc}")
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    return {"score_endpoint": "mcdonald", "resultat": result,
            "moteur": "medisuite_rules.neurology"}

