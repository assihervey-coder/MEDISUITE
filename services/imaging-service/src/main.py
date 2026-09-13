"""imaging-service — PACS léger avec DICOMweb (PS3.18) : QIDO-RS, WADO-RS, STOW-RS.

Workflow : STOW (réception examen) → QIDO (recherche) → WADO (métadonnées) →
compte-rendu signé par le radiologue (statut workflow : PENDING → REPORTED → SIGNED).
Intégration Orthanc/OHIF via configuration (ADR-0002/0006).
"""
from __future__ import annotations

import pathlib
import sys
from typing import Annotated

ROOT = pathlib.Path(__file__).resolve().parents[3]
for p in ("packages/medisuite-core", "packages/clinical-rules"):
    sys.path.insert(0, str(ROOT / p))

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column

from medisuite_core import security
from medisuite_core.db import Base, engine_for, init_db, new_id
from medisuite_core.events import bus
from medisuite_core.http import create_service_app
from medisuite_core.rbac import can

# Connecteur PACS réel (v0.2) — import bi-mode : paquet (uvicorn src.main:app)
# ou plat (tests : sys.path inclut src/).
try:
    from . import orthanc_client as _oc
except ImportError:  # mode plat
    import orthanc_client as _oc

app: FastAPI = create_service_app(
    "imaging-service", "Imagerie Médicale (PACS/DICOMweb)",
    "DICOMweb PS3.18 : QIDO-RS, WADO-RS, STOW-RS + worklist UPS + comptes-rendus "
    "signés. Connecteurs Orthanc/OHIF/dcm4chee.", module_label="Imagerie")

engine = engine_for("imaging-service")
JWT_SECRET = "medisuite-dev-secret-change-in-prod"


def current_user(authorization: Annotated[str | None, Header()] = None) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        return {"sub": "anon", "role": ""}
    try:
        return security.jwt_decode(authorization.split(" ", 1)[1], JWT_SECRET)
    except security.JWTError:
        return {"sub": "anon", "role": ""}


class Study(Base):
    __tablename__ = "studies"
    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    study_uid: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    accession_number: Mapped[str] = mapped_column(String(30), unique=True)
    patient_id: Mapped[str] = mapped_column(String(16), index=True)
    patient_name: Mapped[str] = mapped_column(String(120), default="")
    modality: Mapped[str] = mapped_column(String(10))  # CR/CT/MR/US/NM/PT...
    description: Mapped[str] = mapped_column(String(200), default="")
    study_date: Mapped[str] = mapped_column(String(10))
    nb_series: Mapped[int] = mapped_column(default=1)
    nb_instances: Mapped[int] = mapped_column(default=1)
    statut: Mapped[str] = mapped_column(String(20), default="PENDING")


class Series(Base):
    __tablename__ = "series"
    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    study_id: Mapped[str] = mapped_column(String(16), index=True)
    series_uid: Mapped[str] = mapped_column(String(80))
    modality: Mapped[str] = mapped_column(String(10))
    description: Mapped[str] = mapped_column(String(120), default="")
    nb_instances: Mapped[int] = mapped_column(default=1)


class Report(Base):
    __tablename__ = "reports"
    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    study_id: Mapped[str] = mapped_column(String(16), index=True)
    conclusion: Mapped[str] = mapped_column(String(2000))
    impression: Mapped[str] = mapped_column(String(500), default="")
    radiologue: Mapped[str] = mapped_column(String(80), default="")
    signe: Mapped[bool] = mapped_column(default=False)


SessionLocal = init_db(engine, Base.metadata)

_UCounter = 0


def _uid(root: str = "1.2.826.0.1.3680043.10.98") -> str:
    """Génère un UID DICOM (racine PED MEDISUITE + suffixe monotone)."""
    global _UCounter
    _UCounter += 1
    return f"{root}.{int(__import__('time').time())}.{_UCounter}"


class StowIn(BaseModel):
    patient_id: str
    patient_name: str = ""
    modality: str
    description: str = ""
    study_date: str = ""
    nb_instances: int = 1


class ReportIn(BaseModel):
    impression: str = ""
    conclusion: str
    signe: bool = False


def seed() -> None:
    with SessionLocal() as db:
        if db.scalar(select(Study).limit(1)):
            return
        from datetime import date, timedelta
        demos = [("CR", "Radio thorax", "drépanocytose, suivi"),
                 ("US", "Échographie obstétricale T2", " grossesse 28 SA"),
                 ("CT", "Scanner cérébral sans injection", "AVC suspicion"),
                 ("MR", "IRM prostatique multiparamétrique", "PI-RADS"),
                 ("NM", "Scintigraphie osseuse", "staging")]
        for i, (mod, desc, ctx) in enumerate(demos, 1):
            d = (date.today() - timedelta(days=i * 2)).isoformat()
            study = Study(id=new_id(), study_uid=_uid(),
                          accession_number=f"ACC-2026-{i:05d}",
                          patient_id=f"pat{i:04d}", patient_name=f"Dossier {i:04d}",
                          modality=mod, description=f"{desc} — {ctx}",
                          study_date=d)
            db.add(study)
            db.add(Series(id=new_id(), study_id=study.id, series_uid=_uid(),
                          modality=mod, description="série 1", nb_instances=8))
        db.commit()


# ------------------------------------------------------------- API métier

@app.get("/api/v1/studies", tags=["études"])
def list_studies(modality: str = "", patient_id: str = "", limit: int = 20,
                 user: dict = Depends(current_user)) -> list[dict]:
    if not can(user.get("role", ""), "imaging.read"):
        raise HTTPException(403, "permission imaging.read requise")
    seed()
    with SessionLocal() as db:
        stmt = select(Study).limit(limit)
        if modality:
            stmt = stmt.where(Study.modality == modality)
        if patient_id:
            stmt = stmt.where(Study.patient_id == patient_id)
        return [{c.name: getattr(s, c.name) for c in s.__table__.columns}
                for s in db.scalars(stmt)]


@app.post("/api/v1/studies", status_code=201, tags=["études"])
def create_study(body: StowIn, user: dict = Depends(current_user)) -> dict:
    if not can(user.get("role", ""), "imaging.upload"):
        raise HTTPException(403, "permission imaging.upload requise")
    with SessionLocal() as db:
        n = len(db.scalars(select(Study)).all()) + 1
        s = Study(id=new_id(), study_uid=_uid(),
                  accession_number=f"ACC-2026-{n:05d}", patient_id=body.patient_id,
                  patient_name=body.patient_name, modality=body.modality,
                  description=body.description, study_date=body.study_date,
                  nb_instances=body.nb_instances)
        db.add(s)
        db.add(Series(id=new_id(), study_id=s.id, series_uid=_uid(),
                      modality=body.modality, description="serie 1",
                      nb_instances=body.nb_instances))
        db.commit()
        bus.publish("imaging.study.received",
                    {"study_uid": s.study_uid, "modality": s.modality})
        return {c.name: getattr(s, c.name) for c in s.__table__.columns}


@app.post("/api/v1/studies/{sid}/report", status_code=201, tags=["comptes-rendus"])
def write_report(sid: str, body: ReportIn,
                 user: dict = Depends(current_user)) -> dict:
    """Rédige/signe le compte-rendu. Signature réservée au radiologue (RBAC)."""
    if body.signe and not can(user.get("role", ""), "imaging.report"):
        raise HTTPException(403, "seul un radiologue signe un compte-rendu")
    with SessionLocal() as db:
        study = db.get(Study, sid)
        if not study:
            raise HTTPException(404, "étude introuvable")
        r = Report(id=new_id(), study_id=sid, conclusion=body.conclusion,
                   impression=body.impression, radiologue=user.get("nom", "anon"),
                   signe=body.signe)
        db.add(r)
        study.statut = "SIGNED" if body.signe else "REPORTED"
        db.commit()
        if body.signe:
            bus.publish("imaging.report.signed", {"study_uid": study.study_uid})
        return {c.name: getattr(r, c.name) for c in r.__table__.columns}


@app.get("/api/v1/studies/{sid}/report", tags=["comptes-rendus"])
def get_report(sid: str, user: dict = Depends(current_user)) -> dict:
    with SessionLocal() as db:
        r = db.scalar(select(Report).where(Report.study_id == sid))
        if not r:
            raise HTTPException(404, "aucun compte-rendu")
        return {c.name: getattr(r, c.name) for c in r.__table__.columns}


# ------------------------------------------------------------- DICOMweb PS3.18

@app.get("/dicom-web/studies", tags=["DICOMweb (QIDO-RS)"])
def qido_studies(limit: int = 50) -> list[dict]:
    """QIDO-RS — recherche d'études (subset d'attributs DICOM JSON)."""
    seed()
    with SessionLocal() as db:
        out = []
        for s in db.scalars(select(Study).limit(limit)):
            out.append({
                "0020000D": {"vr": "UI", "Value": [s.study_uid]},
                "00080050": {"vr": "SH", "Value": [s.accession_number]},
                "00080060": {"vr": "CS", "Value": [s.modality]},
                "0008103E": {"vr": "LO", "Value": [s.description]},
                "00080020": {"vr": "DA", "Value": [s.study_date.replace("-", "")]},
                "00100010": {"vr": "PN", "Value": [{"Alphabetic": s.patient_name}]},
            })
        return out


@app.get("/dicom-web/studies/{study_uid}/series", tags=["DICOMweb (QIDO-RS)"])
def qido_series(study_uid: str) -> list[dict]:
    with SessionLocal() as db:
        study = db.scalar(select(Study).where(Study.study_uid == study_uid))
        if not study:
            raise HTTPException(404, "étude inconnue")
        return [{"0020000E": {"vr": "UI", "Value": [sr.series_uid]},
                 "00080060": {"vr": "CS", "Value": [sr.modality]},
                 "00201209": {"vr": "IS", "Value": [sr.nb_instances]}}
                for sr in db.scalars(select(Series).where(Series.study_id == study.id))]


@app.get("/dicom-web/studies/{study_uid}/metadata", tags=["DICOMweb (WADO-RS)"])
def wado_metadata(study_uid: str) -> dict:
    """WADO-RS — métadonnées de l'étude (les pixels passent par Orthanc en prod)."""
    with SessionLocal() as db:
        s = db.scalar(select(Study).where(Study.study_uid == study_uid))
        if not s:
            raise HTTPException(404, "étude inconnue")
        return {"00080016": {"vr": "UI", "Value": ["1.2.840.10008.5.1.4.1.1.7"]},
                "00080018": {"vr": "UI", "Value": [s.study_uid]},
                "00080060": {"vr": "CS", "Value": [s.modality]},
                "0020000D": {"vr": "UI", "Value": [s.study_uid]},
                "00080050": {"vr": "SH", "Value": [s.accession_number]}}


@app.post("/dicom-web/studies", status_code=201, tags=["DICOMweb (STOW-RS)"])
async def stow(request: Request) -> dict:
    """STOW-RS — réception d'une étude (JSON métadonnées en dev ; multipart
    DICOM relayé vers Orthanc en production via dicom-gateway)."""
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(415, "corps JSON attendu en mode léger (v0.1)")
    body = StowIn(**{k.lower(): v for k, v in {
        "patient_id": payload.get("00100020", {}).get("Value", [""])[0],
        "patient_name": (payload.get("00100010", {}).get("Value", [{}])[0]
                         or {}).get("Alphabetic", ""),
        "modality": payload.get("00080060", {}).get("Value", ["OT"])[0],
        "description": payload.get("0008103E", {}).get("Value", [""])[0],
        "study_date": payload.get("00080020", {}).get("Value", [""])[0],
    }.items()})
    with SessionLocal() as db:
        n = len(db.scalars(select(Study)).all()) + 1
        s = Study(id=new_id(), study_uid=_uid(),
                  accession_number=f"ACC-2026-{n:05d}", patient_id=body.patient_id,
                  patient_name=body.patient_name, modality=body.modality,
                  description=body.description,
                  study_date=body.study_date or __import__("datetime").date.today().isoformat())
        db.add(s)
        db.add(Series(id=new_id(), study_id=s.id, series_uid=_uid(),
                      modality=body.modality, description="série 1",
                      nb_instances=body.nb_instances))
        db.commit()
        return {"00081190": {"vr": "UR", "Value": [f"/dicom-web/studies/{s.study_uid}"]},
                "00081199": {"vr": "SQ", "Value": [{"00081199": {
                    "vr": "SQ", "Value": [{"00081190": {"vr": "UR", "Value": [
                        f"/dicom-web/studies/{s.study_uid}"]},
                        "00081198": {"vr": "US", "Value": [0]}}]}}]}}


@app.get("/api/v1/integrations", tags=["intégrations"])
def integrations() -> dict:
    """État des connecteurs PACS (ADR-0006) : Orthanc par défaut."""
    live = _oc.OrthancClient().ping()
    return {"orthanc": {"url": _oc.OrthancClient().url,
                         "actif": live,
                         "note": "docker compose -f local-deployment/"
                                 "docker-compose.minimal.yml up orthanc-pacs"},
            "ohif": {"mode": "extension dicom-viewer/apps/dicom-viewer"},
            "dcm4chee": {"url": None, "actif": False}}


# ── PACS réel (v0.2) : statut + relais QIDO vers Orthanc ─────────────────────

@app.get("/api/v1/pacs/status", tags=["PACS Orthanc (v0.2)"])
def pacs_status() -> dict:
    """Santé du PACS Orthanc réel. Jamais 5xx : reachable=false si hors ligne."""
    oc = _oc.OrthancClient()
    try:
        sysinfo = oc.system()
        return {"reachable": True, "url": oc.url,
                "version": sysinfo.get("Version"),
                "nom": sysinfo.get("Name"),
                "dicom_aet": sysinfo.get("DicomAet"),
                "patients": sysinfo.get("PatientCount"),
                "etudes": sysinfo.get("StudyCount"),
                "dicomweb": "/api/v1/pacs/studies"}
    except _oc.OrthancError as exc:
        return {"reachable": False, "url": oc.url, "erreur": str(exc),
                "note": "imagerie locale consultable ; vérifier "
                        "docker compose up orthanc-pacs"}


@app.get("/api/v1/pacs/studies", tags=["PACS Orthanc (v0.2)"])
def pacs_studies(limit: int = 20) -> list[dict]:
    """Fiches d'études du PACS réel (expansion Orthanc /studies)."""
    oc = _oc.OrthancClient()
    try:
        return oc.studies(limit=limit)
    except _oc.OrthancError as exc:
        raise HTTPException(502, f"PACS Orthanc injoignable : {exc}")


@app.get("/api/v1/pacs/qido", tags=["PACS Orthanc (v0.2)"])
def pacs_qido(query: str = "limit=20") -> list[dict]:
    """Relais QIDO-RS DICOMweb vers Orthanc (PS3.18), attributs DICOM JSON."""
    oc = _oc.OrthancClient()
    try:
        return oc.dicomweb_studies(query)
    except _oc.OrthancError as exc:
        raise HTTPException(502, f"PACS Orthanc injoignable : {exc}")
