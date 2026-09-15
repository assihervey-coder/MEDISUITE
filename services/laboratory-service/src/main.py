"""laboratory-service — LIS complet : prescription → prélèvement → résultat →
validation biologiste → compte-rendu, avec contrôle qualité Westgard et HL7 v2.

Flagship du moteur de règles : chaque résultat passe par lab_qc.analyser_resultat
(flag de référence + valeur critique + delta check), le QC par westgard().
"""
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

from medisuite_core import hl7
from medisuite_core import security
from medisuite_core import auth_deps
from medisuite_core.db import Base, engine_for, init_db, new_id
from medisuite_core.events import bus
from medisuite_core.http import create_service_app
from medisuite_core.rbac import can
from medisuite_rules import lab_qc

app: FastAPI = create_service_app(
    "laboratory-service", "Laboratoire (LIS)",
    "Prescription, prélèvements, résultats avec flags de référence et valeurs "
    "critiques, validation biologiste, QC Westgard/Levey-Jennings, HL7 ORM/ORU.",
    module_label="Laboratoire")

engine = engine_for("laboratory-service")
JWT_SECRET = "medisuite-dev-secret-change-in-prod"


def current_user(authorization: Annotated[str | None, Header()] = None) -> dict:
    """Identité : absent → anon ; jeton invalide/expiré → 401 (le portail
    déconnecte au lieu d'afficher un faux 403) ; valide → claims (RBAC)."""
    return auth_deps.bearer_identity(authorization, JWT_SECRET)


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    patient_id: Mapped[str] = mapped_column(String(16), index=True)
    patient_dossier: Mapped[str] = mapped_column(String(20), default="")
    patient_nom: Mapped[str] = mapped_column(String(120), default="")
    analyte: Mapped[str] = mapped_column(String(40), index=True)  # clé REFERENCE_RANGES
    prescripteur: Mapped[str] = mapped_column(String(80), default="")
    urgent: Mapped[bool] = mapped_column(default=False)
    statut: Mapped[str] = mapped_column(String(20), default="ORDERED")
    # ORDERED → COLLECTED → RESULTED → VALIDATED


class Sample(Base):
    __tablename__ = "samples"
    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    order_id: Mapped[str] = mapped_column(String(16), index=True)
    barcode: Mapped[str] = mapped_column(String(30), unique=True)
    type_prelevement: Mapped[str] = mapped_column(String(30), default="sang veineux")


class Result(Base):
    __tablename__ = "results"
    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    order_id: Mapped[str] = mapped_column(String(16), index=True)
    valeur: Mapped[float] = mapped_column()
    unite: Mapped[str] = mapped_column(String(20), default="")
    reference: Mapped[str] = mapped_column(String(40), default="")
    flag: Mapped[str] = mapped_column(String(20), default="")
    critical: Mapped[bool] = mapped_column(default=False)
    delta_pct: Mapped[float | None] = mapped_column(nullable=True)
    valide_par: Mapped[str] = mapped_column(String(80), default="")


class QCRun(Base):
    __tablename__ = "qc_runs"
    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    analyte: Mapped[str] = mapped_column(String(40), index=True)
    moyenne: Mapped[float] = mapped_column()
    ecart_type: Mapped[float] = mapped_column()
    valeurs: Mapped[list] = mapped_column(JSON)
    decision: Mapped[str] = mapped_column(String(60), default="")
    violations: Mapped[list] = mapped_column(JSON, default=list)


SessionLocal = init_db(engine, Base.metadata)


def seed() -> None:
    """Jeu de démonstration déterministe (graine 42) — idempotent.

    Recouvre le workflow complet : prescriptions ORDERED/COLLECTED/RESULTED/
    VALIDATED, flags calculés par le moteur lab_qc (même logique que
    l'endpoint /results), dont deux valeurs critiques pour la démo
    notification + un résultat validé par le biologiste démo."""
    import random

    with SessionLocal() as db:
        if db.scalar(select(Order).limit(1)):
            return
        rng = random.Random(42)
        demo = [
            # (patient_id, dossier, nom, analyte, urgent, valeur_ou_None, valide)
            ("pat0001", "MS-2026-00001", "Kouassi Didier", "hemoglobine", False, 9.1, True),
            ("pat0001", "MS-2026-00001", "Kouassi Didier", "creatinine", False, 1.1, True),
            ("pat0002", "MS-2026-00002", "Diomandé Awa", "hba1c", False, 9.4, True),
            ("pat0003", "MS-2026-00003", "Traoré Ibrahim", "glucose", True, 386.0, False),
            ("pat0004", "MS-2026-00004", "Aka Marie", "leucocytes", True, 18400.0, False),
            ("pat0005", "MS-2026-00005", "Bamba Salif", "crp", False, 42.0, False),
            ("pat0006", "MS-2026-00006", "N'Guessan Adjoua", "plaquettes", False, None, False),
            ("pat0007", "MS-2026-00007", "Coulibaly Fanta", "sodium", False, None, False),
            ("pat0008", "MS-2026-00008", "Yao Kouadio", "potassium", True, None, False),
        ]
        for pid, dossier, nom, analyte, urgent, valeur, valide in demo:
            o = Order(id=new_id(), patient_id=pid, patient_dossier=dossier,
                      patient_nom=nom, analyte=analyte,
                      prescripteur="Dr Koné Fatoumata", urgent=urgent,
                      statut="ORDERED")
            db.add(o)
            if valeur is None:
                continue  # reste ORDERED : démo bouton « Prélever »
            o.statut = "COLLECTED"
            db.add(Sample(id=new_id(), order_id=o.id,
                          barcode=f"LAB-2026-{new_id().upper()[:10]}"))
            analyse = lab_qc.analyser_resultat(analyte, valeur)
            loinc, unite, bas, haut, *_ = lab_qc.REFERENCE_RANGES[analyte]
            r = Result(id=new_id(), order_id=o.id, valeur=valeur, unite=unite,
                       reference=f"{bas}-{haut} {unite}",
                       flag=analyse["flag"], critical=analyse["critical"],
                       delta_pct=round(rng.uniform(-12, 12), 1))
            if valide:
                r.valide_par = "Dr Bakayoko Lydie (biologiste)"
                o.statut = "VALIDATED"
            else:
                o.statut = "RESULTED"
            db.add(r)
        db.commit()


seed()


class OrderIn(BaseModel):
    patient_id: str
    patient_dossier: str = ""
    patient_nom: str = ""
    analyte: str
    prescripteur: str = ""
    urgent: bool = False


class ResultIn(BaseModel):
    valeur: float
    resultat_precedent: float | None = None


class QCIn(BaseModel):
    analyte: str
    moyenne: float
    ecart_type: float
    valeurs: list[float]


@app.post("/api/v1/orders", status_code=201, tags=["prescriptions"])
def create_order(body: OrderIn, user: dict = Depends(current_user)) -> dict:
    if not can(user.get("role", ""), "lab.order"):
        raise HTTPException(403, "permission lab.order requise")
    if body.analyte not in lab_qc.REFERENCE_RANGES:
        raise HTTPException(422, f"analyte inconnu — disponibles : "
                                 f"{sorted(lab_qc.REFERENCE_RANGES)}")
    with SessionLocal() as db:
        o = Order(id=new_id(), **body.model_dump())
        db.add(o)
        db.commit()
        bus.publish("lab.ordered", {"order_id": o.id, "analyte": o.analyte})
        return {c.name: getattr(o, c.name) for c in o.__table__.columns}


@app.get("/api/v1/orders", tags=["prescriptions"])
def list_orders(statut: str = "", limit: int = 50,
                user: dict = Depends(current_user)) -> list[dict]:
    with SessionLocal() as db:
        stmt = select(Order).limit(limit)
        if statut:
            stmt = stmt.where(Order.statut == statut)
        return [{c.name: getattr(o, c.name) for c in o.__table__.columns}
                for o in db.scalars(stmt)]


@app.get("/api/v1/results", tags=["résultats"])
def list_results(limit: int = 100,
                 user: dict = Depends(current_user)) -> list[dict]:
    """Résultats publiés, joints à leur prescription (analyte, patient, statut)
    — alimente l'écran Laboratoire du web-portal en une seule requête."""
    with SessionLocal() as db:
        rows = db.execute(
            select(Result, Order).join(Order, Result.order_id == Order.id)
            .order_by(Result.id.desc()).limit(limit)).all()
        return [{"id": r.id, "order_id": r.order_id, "analyte": o.analyte,
                 "patient_nom": o.patient_nom, "patient_dossier": o.patient_dossier,
                 "valeur": r.valeur, "unite": r.unite, "reference": r.reference,
                 "flag": r.flag, "critical": r.critical, "delta_pct": r.delta_pct,
                 "valide_par": r.valide_par, "statut": o.statut}
                for r, o in rows]


@app.post("/api/v1/orders/{oid}/collect", tags=["prélèvements"])
def collect(oid: str, type_prelevement: str = "sang veineux",
            user: dict = Depends(current_user)) -> dict:
    with SessionLocal() as db:
        o = db.get(Order, oid)
        if not o:
            raise HTTPException(404, "prescription introuvable")
        if o.statut != "ORDERED":
            raise HTTPException(409, f"statut {o.statut} : prélèvement déjà fait")
        s = Sample(id=new_id(), order_id=oid,
                   barcode=f"LAB-2026-{new_id().upper()[:10]}")
        db.add(s)
        o.statut = "COLLECTED"
        db.commit()
        return {"sample_id": s.id, "barcode": s.barcode,
                "type_prelevement": s.type_prelevement, "order": o.statut}


@app.post("/api/v1/orders/{oid}/results", tags=["résultats"])
def enter_result(oid: str, body: ResultIn,
                 user: dict = Depends(current_user)) -> dict:
    """Entrée résultat (automate ou saisie) : flag référence + delta check
    + alerte critique automatiques (moteur lab_qc)."""
    with SessionLocal() as db:
        o = db.get(Order, oid)
        if not o:
            raise HTTPException(404, "prescription introuvable")
        analyse = lab_qc.analyser_resultat(o.analyte, body.valeur)
        delta = lab_qc.delta_check(body.valeur, body.resultat_precedent or 0,
                                   o.analyte) if body.resultat_precedent else None
        loinc, unite, bas, haut, *_ = lab_qc.REFERENCE_RANGES[o.analyte]
        r = Result(id=new_id(), order_id=oid, valeur=body.valeur, unite=unite,
                   reference=f"{bas}-{haut} {unite}", flag=analyse["flag"],
                   critical=analyse["critical"],
                   delta_pct=delta["delta_pct"] if delta else None)
        db.add(r)
        o.statut = "RESULTED"
        db.commit()
        if analyse["critical"]:
            bus.publish("alert.clinical", {
                "type": "valeur_critique", "analyte": o.analyte,
                "valeur": body.valeur, "order_id": oid,
                "patient": o.patient_nom, "action": "contacter le prescripteur"})
        return {c.name: getattr(r, c.name) for c in r.__table__.columns} | {
            "notification_critique": analyse["critical"]}


@app.post("/api/v1/results/{rid}/validate", tags=["résultats"])
def validate_result(rid: str, user: dict = Depends(current_user)) -> dict:
    """Validation biologiste (RBAC lab.validate) → résultat FHIR 'final' + ORU^R01."""
    if not can(user.get("role", ""), "lab.validate"):
        raise HTTPException(403, "seul un biologiste valide les résultats")
    with SessionLocal() as db:
        r = db.get(Result, rid)
        if not r:
            raise HTTPException(404, "résultat introuvable")
        o = db.get(Order, r.order_id)
        o.statut = "VALIDATED"
        r.valide_par = user.get("nom", "biologiste")
        db.commit()
        bus.publish("lab.result.validated", {"order_id": o.id,
                                             "critical": r.critical})
        return {"result_id": r.id, "statut": o.statut,
                "valide_par": r.valide_par,
                "message_hl7_oru": hl7.build_oru_r01(
                    {"loinc": lab_qc.REFERENCE_RANGES[o.analyte][0],
                     "analyse": o.analyte, "valeur": r.valeur,
                     "unite": r.unite, "dans_reference": r.flag == "normal"},
                    {"numero_dossier": o.patient_dossier,
                     "nom": o.patient_nom, "prenoms": ""})}


@app.post("/api/v1/qc/run", tags=["contrôle qualité"])
def qc_run(body: QCIn, user: dict = Depends(current_user)) -> dict:
    """Exécute les règles de Westgard sur une série de contrôles QC."""
    if not can(user.get("role", ""), "lab.qc"):
        raise HTTPException(403, "permission lab.qc requise")
    verdict = lab_qc.westgard(body.valeurs, body.moyenne, body.ecart_type)
    with SessionLocal() as db:
        qc = QCRun(id=new_id(), analyte=body.analyte, moyenne=body.moyenne,
                   ecart_type=body.ecart_type, valeurs=body.valeurs,
                   decision=verdict["decision"], violations=verdict["violations"])
        db.add(qc)
        db.commit()
        return verdict | {"qc_id": qc.id}


@app.get("/api/v1/qc/{qc_id}/levey-jennings", tags=["contrôle qualité"])
def levey_jennings(qc_id: str) -> list[dict]:
    with SessionLocal() as db:
        qc = db.get(QCRun, qc_id)
        if not qc:
            raise HTTPException(404, "run QC introuvable")
        return [lab_qc.levey_jennings(v, qc.moyenne, qc.ecart_type)
                for v in qc.valeurs]


@app.get("/api/v1/hl7/orm/{oid}", tags=["interopérabilité"])
def build_orm(oid: str) -> dict:
    """Génère la commande HL7 v2 ORM^O01 pour un analyseur externe."""
    with SessionLocal() as db:
        o = db.get(Order, oid)
        if not o:
            raise HTTPException(404, "prescription introuvable")
        loinc = lab_qc.REFERENCE_RANGES[o.analyte][0]
        msg = hl7.build_orm_o01({"id": o.id, "code_examen": loinc,
                                 "libelle_examen": o.analyte,
                                 "prescripteur": o.prescripteur,
                                 "urgent": "S" if o.urgent else "R"})
        return {"message": msg, "mllp_frame_hex":
                hl7.mllp_frame(msg).hex()}


@app.post("/api/v1/hl7/oru", tags=["interopérabilité"])
def receive_oru(payload: dict) -> dict:
    """Reçoit un message ORU^R01 d'un automate (Mirth) et extrait le résultat."""
    msg = hl7.parse(payload.get("message", ""))
    if "ORU" not in msg.message_type:
        raise HTTPException(422, f"type inattendu : {msg.message_type}")
    valeur = float(msg.field("OBX", 5) or 0)
    loinc = msg.field("OBX", 3)
    return {"type": msg.message_type, "loinc": loinc, "valeur": valeur,
            "flag": msg.field("OBX", 8),
            "patient_dossier": msg.field("PID", 3)}
