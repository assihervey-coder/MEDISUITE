"""Médecine nucléaire (☢️) — Module 22 MEDISUITE.

TEP-TDM (SUV, MTV/TLG, PERCIST), SPECT, théranostique Lu-177, dosimétrie MIRD.

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
from medisuite_rules import oncology

app: FastAPI = create_service_app(
    "nuclear-medicine-service", "Médecine nucléaire", "TEP-TDM (SUV, MTV/TLG, PERCIST), SPECT, théranostique Lu-177, dosimétrie MIRD.",
    module_label="Module 22 · Médecine nucléaire")

engine = engine_for("nuclear-medicine-service")
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
        demo = [('TEP FDG staging lymphome', 'pat0058', 'BAMBA Awa', 'SUVmax'), ('PSMA prostate récidive', 'pat0059', 'GBANE Michel', 'TEP-PSMA'), ('PRRT Lu-177 séance 3', 'pat0060', 'KIPRE Jules', 'Dosimétrie')]
        for i, (titre, pid, nom, note) in enumerate(demo, 1):
            db.add(Case(id=new_id(), patient_id=pid, patient_nom=nom,
                        date="2026-09-%02d" % i, titre=titre,
                        severite="", payload={"note": note}))
        db.commit()



# ---- fonctions cliniques spécifiques au module ----

def _growth_pct(v1_ml: float, v2_ml: float) -> dict:
    """Taux de croissance volumétrique entre deux IRM (RANO 2010, adapted)."""
    if v1_ml <= 0:
        raise ValueError("volume initial invalide")
    pct = (v2_ml - v1_ml) / v1_ml * 100
    return {"croissance_pct": round(pct, 1),
            "significative": pct >= 25,  # critère progression RANO
            "interpretation": "progression selon RANO" if pct >= 25
            else "stable" if abs(pct) < 15 else "régression"}


def _apgar(items: list[int]) -> dict:
    """Score d'APGAR (Apgar 1952) : 5 items 0-2 (fréquence cardiaque, respiration,
    tonus, réactivité, coloration) à 1, 5 et 10 minutes."""
    if len(items) != 5 or any(not 0 <= s <= 2 for s in items):
        raise ValueError("APGAR : 5 items de 0 à 2")
    total = sum(items)
    return {"score": total,
            "etat": ("déprimé sévère — réanimation" if total <= 3
                     else "modérément déprimé — stimulation" if total <= 6
                     else "bonne adaptation")}


def _gdm_iadpsg(glycemie_jeun: float, glycemie_1h: float, glycemie_2h: float) -> dict:
    """HGPN — critères IADPSG/OMS 2013 (HGPO 75 g, seuils 92/180/153 mg/dL).
    Un seul seuil atteint suffit au diagnostic de diabète gestationnel."""
    seuils = {"jeun_92": glycemie_jeun >= 92, "h1_180": glycemie_1h >= 180,
              "h2_153": glycemie_2h >= 153}
    n = sum(seuils.values())
    return {"criteres": seuils, "seuils_atteints": n,
            "diagnostic": "diabète gestationnel (IADPSG)" if n >= 1
            else "HGPN normale",
            "conduite": ("diète + autosurveillance ± insuline"
                         if n >= 1 else "rattrapage T2 24-28 SA")}


def _suv_max(activite_kbq_ml: float, dose_injectee_MBq: float,
             poids_kg: float) -> dict:
    """SUVmax = C_tissu [kBq/mL] × poids [kg] × 1000 / dose [kBq]
    (normalisé ; cible malignité habituellement >2.5-3 sur TEP FDG)."""
    if dose_injectee_MBq <= 0 or poids_kg <= 0:
        raise ValueError("dose/poids invalides")
    suv = activite_kbq_ml * poids_kg * 1000 / (dose_injectee_MBq * 1000)
    return {"suv_max": round(suv, 2),
            "interpretation": ("hypermétabolisme — lésion suspecte" if suv >= 2.5
                               else "métabolisme faible — probablement bénin")}


def _eqd2(dose_par_seance: float, nb_seances: int, alpha_beta: float) -> dict:
    """EQD2 (équivalent dose 2 Gy/fx) : EQD2 = D × (d + α/β) / (2 + α/β)
    — radiobiologie clinique (référence : ICRU / radiobiology guide)."""
    if dose_par_seance <= 0 or nb_seances <= 0:
        raise ValueError("paramètres invalides")
    total = dose_par_seance * nb_seances
    eqd2 = total * (dose_par_seance + alpha_beta) / (2 + alpha_beta)
    return {"dose_totale_gy": total, "eqd2_gy": round(eqd2, 1),
            "note": "EQD2 α/β=%.0f — comparer aux contraintes OAR" % alpha_beta}


@app.get("/module-info", tags=["module"])
def module_info() -> dict:
    return {"module": 22, "nom": "Médecine nucléaire", "service": "nuclear-medicine-service",
            "scores": ['suv', 'ecog'],
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




@app.post("/api/v1/scores/suv", tags=["scores cliniques"])
def score_suv(body: dict, user: dict = Depends(current_user)) -> dict:
    """Score suv — module courant"""
    try:
        result = _suv_max(**body)
    except TypeError as exc:
        raise HTTPException(422, f"paramètres invalides : {exc}")
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    return {"score_endpoint": "suv", "resultat": result,
            "moteur": "medisuite_rules.custom"}


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

