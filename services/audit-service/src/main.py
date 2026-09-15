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
    "audit-service", "Registre d'audit", "Registre d'audit à chaîne de hachage SHA-256 : non-répudiation, vérification d'intégrité (ADR-0021).", module_label="Registre d'audit")

engine = engine_for("audit-service")
JWT_SECRET = "medisuite-dev-secret-change-in-prod"


def current_user(authorization: Annotated[str | None, Header()] = None) -> dict:
    """Identité : absent → anon ; jeton invalide/expiré → 401 (le portail
    déconnecte au lieu d'afficher un faux 403) ; valide → claims (RBAC)."""
    return auth_deps.bearer_identity(authorization, JWT_SECRET)


from medisuite_core.audit_chain import AuditEvent, HashChainLedger


class AuditRow(Base):
    __tablename__ = "audit_chain"
    index: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[float] = mapped_column()
    actor: Mapped[str] = mapped_column(String(80))
    role: Mapped[str] = mapped_column(String(30))
    action: Mapped[str] = mapped_column(String(60), index=True)
    resource: Mapped[str] = mapped_column(String(120))
    detail: Mapped[dict] = mapped_column(JSON, default=dict)
    prev_hash: Mapped[str] = mapped_column(String(64))
    hash: Mapped[str] = mapped_column(String(64), unique=True)


SessionLocal = init_db(engine, Base.metadata)
_chain = HashChainLedger()
_loaded = False


def _chain_all() -> HashChainLedger:
    """Recharge la chaîne depuis la base (état partagé entre redémarrages)."""
    global _loaded
    if not _loaded:
        with SessionLocal() as db:
            for row in db.scalars(select(AuditRow).order_by(AuditRow.index)):
                e = AuditEvent(index=row.index, timestamp=row.timestamp,
                               actor=row.actor, role=row.role, action=row.action,
                               resource=row.resource, detail=row.detail,
                               prev_hash=row.prev_hash, hash=row.hash)
                _chain.events.append(e)
        _loaded = True
    return _chain


class EventIn(BaseModel):
    actor: str
    role: str = "system"
    action: str
    resource: str
    detail: dict = {}


def seed_events() -> None:
    """Jeu de démonstration déterministe — idempotent.

    Événements typiques d'une journée d'activité CHU : chaque entrée passe par
    HashChainLedger.append pour garantir la chaîne SHA-256 (vérifiable via
    POST /chain/verify), puis est persistée."""
    chain = _chain_all()
    if chain.events:
        return
    demo = [
        ("system", "system", "service.start", "auth-service",
         {"version": "v0.16.0"}),
        ("medecin@chu-cocody.ci", "medecin", "auth.login", "session:web-portal",
         {"mfa": False}),
        ("Dr Koné Fatoumata", "medecin", "patient.created", "patient:pat0001",
         {"commune": "Cocody"}),
        ("Dr Koné Fatoumata", "medecin", "lab.ordered", "order:hba1c-pat0002",
         {"urgent": False}),
        ("infirmier Traoré", "infirmier", "lab.collected", "sample:LAB-2026",
         {"type": "sang veineux"}),
        ("automate SYSMEX", "system", "lab.resulted", "order:leucocytes-pat0004",
         {"critical": True, "valeur": 18400}),
        ("Dr Bakayoko Lydie", "biologiste", "lab.result.validated",
         "result:hemoglobine-pat0001", {"flag": "low"}),
        ("Dr Ouattara Aline", "radiologue", "imaging.reported", "study:ACC-2026-00002",
         {"modality": "MG", "birads": 4}),
        ("admin@medisuite.ci", "admin", "consent.granted", "patient:pat0003",
         {"ia": True}),
        ("system", "system", "chain.verify", "audit:self", {"result": "OK"}),
    ]
    with SessionLocal() as db:
        for actor, role, action, resource, detail in demo:
            e = chain.append(actor, role, action, resource, detail)
            db.merge(AuditRow(**e.to_dict()))
        db.commit()


seed_events()


@app.post("/api/v1/events", status_code=201, tags=["registre"])
def append_event(body: EventIn) -> dict:
    chain = _chain_all()
    e = chain.append(body.actor, body.role, body.action, body.resource,
                     body.detail)
    with SessionLocal() as db:
        db.merge(AuditRow(**e.to_dict()))
        db.commit()
    return {"index": e.index, "hash": e.hash[:16] + "…"}


@app.get("/api/v1/tail", tags=["registre"])
def tail(n: int = 20) -> list[dict]:
    chain = _chain_all()
    return [{"index": e.index, "action": e.action, "actor": e.actor,
             "resource": e.resource, "hash": e.hash[:16] + "…"}
            for e in chain.events[-n:]]


@app.post("/api/v1/chain/verify", tags=["intégrité"])
def verify() -> dict:
    """Vérifie toute la chaîne : (intègre, index_première_altération)."""
    ok, bad = _chain_all().verify()
    return {"integre": ok, "premiere_alteration": bad,
            "nb_events": len(_chain_all().events)}


@app.post("/api/v1/chain/tamper-demo/{index}", tags=["intégrité"])
def tamper_demo(index: int) -> dict:
    """DÉMONSTRATION PÉDAGOGIQUE : altère une entrée pour prouver la détection.
    Jamais exposé en production (route absente du build prod)."""
    chain = _chain_all()
    if not 0 <= index < len(chain.events):
        raise HTTPException(404, "index hors chaîne")
    chain.events[index].action = "ACTION_FALSIFIEE"
    return {"altéré": index, "note": "POST /chain/verify détecte maintenant l'altération"}


@app.get("/api/v1/stats", tags=["registre"])
def stats() -> dict:
    chain = _chain_all()
    par_action: dict[str, int] = {}
    for e in chain.events:
        par_action[e.action] = par_action.get(e.action, 0) + 1
    return {"total": len(chain.events), "par_action": par_action}
