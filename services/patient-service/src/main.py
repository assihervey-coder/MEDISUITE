"""patient-service — dossier patient, consultations, consentements RGPD, FHIR.

Endpoints métier : CRUD patients, recherche, consultations, diagnostics CIM-10,
allergies, consentements (usage IA / recherche / partage), export FHIR R4.
Chaque écriture publie un événement (patient.created/updated) et journalise.
"""
from __future__ import annotations

import pathlib
import sys
from datetime import date

ROOT = pathlib.Path(__file__).resolve().parents[3]
for p in ("packages/medisuite-core", "packages/clinical-rules"):
    sys.path.insert(0, str(ROOT / p))

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column
from typing import Annotated

from medisuite_core import fhir, security
from medisuite_core.db import Base, engine_for, init_db, new_id
from medisuite_core.events import bus
from medisuite_core.http import create_service_app
from medisuite_core.rbac import can
from medisuite_core.seed import COMMUNES, NOMS, PRENOMS_F, PRENOMS_M, VILLES, \
    age_from, generate_patient
import random

app: FastAPI = create_service_app(
    "patient-service", "Dossier Patient",
    "Dossier clinique unifié : démographie, consultations, diagnostics, allergies, "
    "consentements RGPD, export FHIR R4.", module_label="Dossier Patient")

engine = engine_for("patient-service")
PSEUDO_SALT = "medisuite-patient-salt"  # Vault en prod
JWT_SECRET = "medisuite-dev-secret-change-in-prod"


def current_user(
    authorization: Annotated[str | None, Header()] = None,
) -> dict:
    """Dépendance d'authentification : décode le Bearer JWT (fail-open anonyme
    en dev, à durcir par dépendance stricte en prod — voir auth-service)."""
    if not authorization or not authorization.lower().startswith("bearer "):
        return {"sub": "anon", "role": ""}
    try:
        return security.jwt_decode(authorization.split(" ", 1)[1], JWT_SECRET)
    except security.JWTError:
        return {"sub": "anon", "role": ""}


class Patient(Base):
    __tablename__ = "patients"
    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    numero_dossier: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    nom: Mapped[str] = mapped_column(String(80), index=True)
    prenoms: Mapped[str] = mapped_column(String(120))
    sexe: Mapped[str] = mapped_column(String(1))
    date_naissance: Mapped[str] = mapped_column(String(10))
    telephone: Mapped[str] = mapped_column(String(30), default="")
    ville: Mapped[str] = mapped_column(String(60), default="Abidjan")
    commune: Mapped[str] = mapped_column(String(60), default="")
    cnam: Mapped[str] = mapped_column(String(30), default="")
    groupe_sanguin: Mapped[str] = mapped_column(String(4), default="")
    consent_ia: Mapped[bool] = mapped_column(default=False)
    consent_recherche: Mapped[bool] = mapped_column(default=False)


class Encounter(Base):
    __tablename__ = "encounters"
    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    patient_id: Mapped[str] = mapped_column(String(16), index=True)
    date: Mapped[str] = mapped_column(String(10))
    motif: Mapped[str] = mapped_column(String(300))
    classe: Mapped[str] = mapped_column(String(10), default="AMB")
    service: Mapped[str] = mapped_column(String(60), default="")
    prescripteur: Mapped[str] = mapped_column(String(80), default="")


class Condition(Base):
    __tablename__ = "conditions"
    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    patient_id: Mapped[str] = mapped_column(String(16), index=True)
    cim10: Mapped[str] = mapped_column(String(10), index=True)
    libelle: Mapped[str] = mapped_column(String(200))
    severite: Mapped[str] = mapped_column(String(20), default="")
    statut: Mapped[str] = mapped_column(String(20), default="active")


class Allergy(Base):
    __tablename__ = "allergies"
    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    patient_id: Mapped[str] = mapped_column(String(16), index=True)
    substance: Mapped[str] = mapped_column(String(100))
    reaction: Mapped[str] = mapped_column(String(200))
    severite: Mapped[str] = mapped_column(String(20), default="modérée")


SessionLocal = init_db(engine, Base.metadata)


class PatientIn(BaseModel):
    nom: str
    prenoms: str
    sexe: str  # M/F
    date_naissance: str  # YYYY-MM-DD
    telephone: str = ""
    ville: str = "Abidjan"
    commune: str = ""
    cnam: str = ""
    groupe_sanguin: str = ""


class EncounterIn(BaseModel):
    date: str
    motif: str
    classe: str = "AMB"
    service: str = ""
    prescripteur: str = ""


class ConditionIn(BaseModel):
    cim10: str
    libelle: str
    severite: str = ""
    statut: str = "active"


class ConsentIn(BaseModel):
    consent_ia: bool | None = None
    consent_recherche: bool | None = None


def _patient_dict(p: Patient) -> dict:
    d = {c.name: getattr(p, c.name) for c in p.__table__.columns}
    d["age"] = age_from(d["date_naissance"])
    d["pseudonyme"] = security.pseudonymize(d["numero_dossier"], salt=PSEUDO_SALT)
    return d


def _get(db, patient_id: str) -> Patient:
    p = db.get(Patient, patient_id)
    if not p:
        raise HTTPException(404, "patient introuvable")
    return p


def seed() -> None:
    with SessionLocal() as db:
        if db.scalar(select(Patient).limit(1)):
            return
        rng = random.Random(42)
        compteur = 1
        for d in generate_patient(rng, 14):
            db.add(Patient(id=d["id"], numero_dossier=f"MS-2026-{compteur:05d}",
                           nom=d["nom"], prenoms=d["prenoms"], sexe=d["sexe"],
                           date_naissance=d["date_naissance"],
                           telephone=d["telephone"], ville=d["ville"],
                           commune=d["commune"], cnam=d["cnam"],
                           groupe_sanguin=d["groupe_sanguin"]))
            compteur += 1
        db.commit()


@app.get("/api/v1/patients", tags=["patients"])
def list_patients(q: str = "", limit: int = 20,
                  user: dict = Depends(current_user)) -> list[dict]:
    if not can(user.get("role", ""), "patient.read"):
        raise HTTPException(403, "permission patient.read requise")
    seed()
    with SessionLocal() as db:
        stmt = select(Patient).limit(limit)
        if q:
            stmt = select(Patient).where(
                Patient.nom.ilike(f"%{q}%") | Patient.numero_dossier.ilike(f"%{q}%")
            ).limit(limit)
        return [_patient_dict(p) for p in db.scalars(stmt)]


@app.post("/api/v1/patients", status_code=201, tags=["patients"])
def create_patient(body: PatientIn, user: dict = Depends(current_user)) -> dict:
    if not can(user.get("role", ""), "patient.write"):
        raise HTTPException(403, "permission patient.write requise")
    if body.sexe not in ("M", "F"):
        raise HTTPException(422, "sexe doit être M ou F")
    with SessionLocal() as db:
        n = len(db.scalars(select(Patient)).all()) + 1
        p = Patient(id=new_id(), numero_dossier=f"MS-2026-{n:05d}", **body.model_dump())
        db.add(p)
        db.commit()
        bus.publish("patient.created", {"patient_id": p.id,
                                        "numero_dossier": p.numero_dossier})
        return _patient_dict(p)


@app.get("/api/v1/patients/{pid}", tags=["patients"])
def get_patient(pid: str, user: dict = Depends(current_user)) -> dict:
    if not can(user.get("role", ""), "patient.read"):
        raise HTTPException(403, "permission patient.read requise")
    with SessionLocal() as db:
        return _patient_dict(_get(db, pid))


@app.get("/api/v1/patients/{pid}/fhir", tags=["interopérabilité"])
def get_patient_fhir(pid: str, user: dict = Depends(current_user)) -> dict:
    if not can(user.get("role", ""), "patient.read"):
        raise HTTPException(403, "permission patient.read requise")
    with SessionLocal() as db:
        return fhir.patient_to_fhir(_patient_dict(_get(db, pid)))


@app.post("/api/v1/patients/{pid}/encounters", status_code=201,
          tags=["consultations"])
def add_encounter(pid: str, body: EncounterIn,
                  user: dict = Depends(current_user)) -> dict:
    if not can(user.get("role", ""), "patient.write"):
        raise HTTPException(403, "permission patient.write requise")
    with SessionLocal() as db:
        _get(db, pid)
        e = Encounter(id=new_id(), patient_id=pid, **body.model_dump())
        db.add(e)
        db.commit()
        return {c.name: getattr(e, c.name) for c in e.__table__.columns}


@app.get("/api/v1/patients/{pid}/encounters", tags=["consultations"])
def list_encounters(pid: str, user: dict = Depends(current_user)) -> list[dict]:
    with SessionLocal() as db:
        _get(db, pid)
        return [{c.name: getattr(e, c.name) for c in e.__table__.columns}
                for e in db.scalars(select(Encounter).where(
                    Encounter.patient_id == pid))]


@app.get("/api/v1/patients/{pid}/conditions", tags=["diagnostics"])
def list_conditions(pid: str, user: dict = Depends(current_user)) -> list[dict]:
    """Liste des diagnostics CIM-10 du patient (lecture, sans PHI superflu)."""
    with SessionLocal() as db:
        _get(db, pid)
        return [{k.name: getattr(c, k.name) for k in c.__table__.columns}
                for c in db.scalars(select(Condition).where(
                    Condition.patient_id == pid))]


@app.post("/api/v1/patients/{pid}/conditions", status_code=201,
          tags=["diagnostics"])
def add_condition(pid: str, body: ConditionIn,
                  user: dict = Depends(current_user)) -> dict:
    if not can(user.get("role", ""), "patient.write"):
        raise HTTPException(403, "permission patient.write requise")
    with SessionLocal() as db:
        _get(db, pid)
        c = Condition(id=new_id(), patient_id=pid, **body.model_dump())
        db.add(c)
        db.commit()
        return {k.name: getattr(c, k.name) for k in c.__table__.columns}


@app.post("/api/v1/patients/{pid}/consent", tags=["RGPD"])
def update_consent(pid: str, body: ConsentIn,
                   user: dict = Depends(current_user)) -> dict:
    """Consentements RGPD art. 7 : usage IA et recherche (révocable à tout moment)."""
    with SessionLocal() as db:
        p = _get(db, pid)
        if body.consent_ia is not None:
            p.consent_ia = body.consent_ia
        if body.consent_recherche is not None:
            p.consent_recherche = body.consent_recherche
        db.commit()
        bus.publish("patient.consent.updated",
                    {"patient_id": pid, "consent_ia": p.consent_ia,
                     "consent_recherche": p.consent_recherche,
                     "par": user.get("sub")})
        return {"id": pid, "consent_ia": p.consent_ia,
                "consent_recherche": p.consent_recherche,
                "avertissement": "consentement IA requis avant toute inférence"}
