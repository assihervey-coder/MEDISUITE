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
from medisuite_core import auth_deps
from medisuite_core.db import Base, engine_for, init_db, new_id
from medisuite_core.events import bus
from medisuite_core.http import create_service_app
from medisuite_core.rbac import can

app: FastAPI = create_service_app(
    "notification-service", "Notifications", "Notifications multi-canaux : email, SMS, push, in-app + routage alertes.", module_label="Notifications")

engine = engine_for("notification-service")
JWT_SECRET = "medisuite-dev-secret-change-in-prod"


def current_user(authorization: Annotated[str | None, Header()] = None) -> dict:
    """Identité : absent → anon ; jeton invalide/expiré → 401 (le portail
    déconnecte au lieu d'afficher un faux 403) ; valide → claims (RBAC)."""
    return auth_deps.bearer_identity(authorization, JWT_SECRET)


class Message(Base):
    __tablename__ = "messages"
    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    canal: Mapped[str] = mapped_column(String(20), index=True)
    destinataire: Mapped[str] = mapped_column(String(120))
    sujet: Mapped[str] = mapped_column(String(200), default="")
    corps: Mapped[str] = mapped_column(default="")
    priorite: Mapped[str] = mapped_column(String(20), default="normale")
    lu: Mapped[bool] = mapped_column(default=False)


SessionLocal = init_db(engine, Base.metadata)


class SendIn(BaseModel):
    canal: str
    destinataire: str
    sujet: str = ""
    corps: str
    priorite: str = "normale"


CANALS = {"email": {"fournisseur": "SMTP interne", "debit_par_min": 1000},
          "sms": {"fournisseur": "passerelle opérateur CI", "debit_par_min": 300},
          "push": {"fournisseur": "FCM", "debit_par_min": 5000},
          "in_app": {"fournisseur": "WebSocket MEDISUITE", "debit_par_min": 10000}}


@app.get("/api/v1/channels", tags=["canaux"])
def channels() -> dict:
    return {"canaux": CANALS}


@app.post("/api/v1/send", status_code=201, tags=["envoi"])
def send(body: SendIn) -> dict:
    if body.canal not in CANALS:
        raise HTTPException(422, f"canal inconnu — {sorted(CANALS)}")
    with SessionLocal() as db:
        m = Message(id=new_id(), **body.model_dump())
        db.add(m)
        db.commit()
        return {"id": m.id, "canal": m.canal, "statut": "mis en file",
                "priorite": m.priorite}


@app.post("/api/v1/alerte-clinique", tags=["envoi"])
def alerte_clinique(body: dict) -> dict:
    """Routage des alertes critiques (event bus alert.clinical) :
    diffusion simultanée in_app + SMS au praticien de garde."""
    dest = body.get("destinataire", "praticien-de-garde")
    sujet = body.get("sujet", "ALERTE CLINIQUE")
    with SessionLocal() as db:
        ids = []
        for canal in ("in_app", "sms"):
            m = Message(id=new_id(), canal=canal, destinataire=dest,
                        sujet=sujet, corps=body.get("corps", ""),
                        priorite="critique")
            db.add(m)
            ids.append({"canal": canal, "id": m.id})
        db.commit()
    return {"diffuse": ids, "delai_cible_s": 30}


@app.get("/api/v1/inbox", tags=["réception"])
def inbox(canal: str = "", limit: int = 50) -> list[dict]:
    with SessionLocal() as db:
        stmt = select(Message).limit(limit)
        if canal:
            stmt = stmt.where(Message.canal == canal)
        return [{c.name: getattr(m, c.name) for c in m.__table__.columns}
                for m in db.scalars(stmt)]


@app.post("/api/v1/inbox/{mid}/read", tags=["réception"])
def mark_read(mid: str) -> dict:
    with SessionLocal() as db:
        m = db.get(Message, mid)
        if not m:
            raise HTTPException(404, "message introuvable")
        m.lu = True
        db.commit()
        return {"id": mid, "lu": True}
