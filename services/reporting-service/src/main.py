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
from medisuite_core.db import Base, engine_for, init_db, new_id
from medisuite_core.events import bus
from medisuite_core.http import create_service_app
from medisuite_core.rbac import can

app: FastAPI = create_service_app(
    "reporting-service", "Comptes-rendus", "Génération et signature de comptes-rendus cliniques (HTML signé).", module_label="Comptes-rendus")

engine = engine_for("reporting-service")
JWT_SECRET = "medisuite-dev-secret-change-in-prod"


def current_user(authorization: Annotated[str | None, Header()] = None) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        return {"sub": "anon", "role": ""}
    try:
        return security.jwt_decode(authorization.split(" ", 1)[1], JWT_SECRET)
    except security.JWTError:
        return {"sub": "anon", "role": ""}


TEMPLATES = {
    "radiologie": ["indication", "technique", "resultats", "conclusion"],
    "laboratoire": ["prescripteur", "prelevement", "resultats", "interpretation"],
    "oncologie": ["diagnostic", "stade", "biomarqueurs", "proposition_RCP"],
    "synthese_patient": ["antecedents", "traitements", "allergies", "plan"],
}


class GeneratedReport(Base):
    __tablename__ = "reports"
    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    kind: Mapped[str] = mapped_column(String(30), index=True)
    titre: Mapped[str] = mapped_column(String(200))
    patient_nom: Mapped[str] = mapped_column(String(120), default="")
    corps_html: Mapped[str] = mapped_column(default="")
    signature: Mapped[str] = mapped_column(String(200), default="")
    signataire: Mapped[str] = mapped_column(String(80), default="")


SessionLocal = init_db(engine, Base.metadata)


class ReportIn(BaseModel):
    kind: str
    titre: str
    patient_nom: str = ""
    sections: dict[str, str] = {}


@app.get("/api/v1/templates", tags=["modèles"])
def templates() -> dict:
    return {"templates": TEMPLATES}


@app.post("/api/v1/reports", status_code=201, tags=["comptes-rendus"])
def generate(body: ReportIn, user: dict = Depends(current_user)) -> dict:
    if body.kind not in TEMPLATES:
        raise HTTPException(422, f"modèle inconnu — {sorted(TEMPLATES)}")
    rows = "".join(
        f"<tr><th>{k}</th><td>{body.sections.get(k, '—')}</td></tr>"
        for k in TEMPLATES[body.kind])
    html = (f"<html><head><title>{body.titre}</title></head>"
            "<body style='font-family:serif;margin:40px'>"
            f"<h1>MEDISUITE — {body.kind.upper()}</h1>"
            f"<h2>{body.titre}</h2><p>Patient : {body.patient_nom}</p>"
            f"<table border=1 cellpadding=6>{rows}</table>"
            f"<footer><small>Généré le 2026-09-13 · rôle {user.get('role', 'anon')}</small></footer>"
            "</body></html>")
    with SessionLocal() as db:
        r = GeneratedReport(id=new_id(), kind=body.kind, titre=body.titre,
                            patient_nom=body.patient_nom, corps_html=html)
        db.add(r)
        db.commit()
        return {"id": r.id, "kind": r.kind, "taille_octets": len(html)}


@app.post("/api/v1/reports/{rid}/sign", tags=["comptes-rendus"])
def sign(rid: str, user: dict = Depends(current_user)) -> dict:
    """Signature HMAC du corps (horodatée) — réservée aux praticiens (RBAC)."""
    if not (can(user.get("role", ""), "imaging.report")
            or can(user.get("role", ""), "lab.validate")
            or can(user.get("role", ""), "patient.write")):
        raise HTTPException(403, "signature réservée aux praticiens")
    with SessionLocal() as db:
        r = db.get(GeneratedReport, rid)
        if not r:
            raise HTTPException(404, "compte-rendu introuvable")
        sig = security.pseudonymize(r.corps_html, user.get("sub", ""),
                                    salt="report-signing")
        r.signature = sig
        r.signataire = user.get("nom", "praticien")
        db.commit()
        bus.publish("report.signed", {"report_id": rid})
        return {"id": rid, "signature": r.signature[:16] + "…",
                "signataire": r.signataire}


@app.get("/api/v1/reports/{rid}", tags=["comptes-rendus"])
def get_report(rid: str):
    from fastapi.responses import HTMLResponse
    with SessionLocal() as db:
        r = db.get(GeneratedReport, rid)
        if not r:
            raise HTTPException(404, "compte-rendu introuvable")
        return HTMLResponse(r.corps_html)
