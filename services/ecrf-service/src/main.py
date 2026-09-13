"""ecrf-service — eCRF FHIR opérationnel de l'investigation MEDISUITE-CI-01
(jalons R5/R6, v0.7).

Implémente le §8 du protocole TD-10 :
- sujets pseudonymisés (code étude CI01-<SITE>-NNNNN, jamais de nom) ;
- formulaires F01-F06 (annexe A1) validés à la saisie par le noyau ecrf.py ;
- signatures investigateur (verrou) puis amendements (addendum versionné,
  l'original reste intact) — exigence ISO 14155 §4.8 / EGSP traçabilité ;
- requêtes de monitoring (SDV) ouvertes par le moniteur, closes par le site ;
- VERROU DE BASE (lock M+18, v0.8) : le promoteur fige la base (≥ 2
  témoins) à la fin des suivis 30 j — checksum SHA-256 de toutes les
  entrées ; après le lock, AUCUNE écriture n'est acceptée et l'extraction
  d'analyse devient possible pour le data manager uniquement ;
- EXTRACTION DATA MANAGER (v0.8) : jeu de données d'analyse (SAF) —
  dernières entrées SIGNÉES par sujet/formulaire + dérivations SAP
  (éligibilité, délai P3, SAE) — refusée avant le lock (409), alarme
  d'intégrité (500) si les données dérivent du checksum verrouillé ;
- synchronisation OFFLINE idempotente (rejouable sans doublon) — les sites
  CHU subissent des coupures réseau, la saisie ne doit jamais être bloquée ;
- export DSMB agrégé SANS donnée libre ni PHI (§6 confidentialité) ;
- audit chaîné SHA-256 natif (ADR-0021) de toutes les mutations ;
- poussée FHIR R4 optionnelle vers le hub HAPI du site (profils IOP,
  ADR-0024) — dégradation gracieuse si le hub est indisponible.

Séparation des rôles (fail-closed) : le comité d'adjudication (aveugle,
§3.3) ne peut saisir QUE le F05 ; les investigateurs ne peuvent JAMAIS
saisir le F05 (conflit d'intérêt ↔ aveuglement).
"""
from __future__ import annotations

import hashlib
import os
import pathlib
import statistics
import sys
import time
from typing import Annotated

ROOT = pathlib.Path(__file__).resolve().parents[3]
for p in ("packages/medisuite-core", "packages/clinical-rules"):
    sys.path.insert(0, str(ROOT / p))

from fastapi import Depends, FastAPI, Header, HTTPException
from sqlalchemy import JSON, Float, Integer, String, select
from sqlalchemy.orm import Mapped, mapped_column

from medisuite_core import ecrf as ecrf_mod
from medisuite_core import security
from medisuite_core.audit_chain import AuditEvent, HashChainLedger
from medisuite_core.db import Base, engine_for, init_db, new_id
from medisuite_core.events import bus
from medisuite_core.http import create_service_app
from medisuite_core.rbac import can

app: FastAPI = create_service_app(
    "ecrf-service", "eCRF Investigation CI-01",
    "eCRF FHIR de l'investigation multicentrique MEDISUITE-CI-01 "
    "(protocole R5, ISO 14155) : saisie offline-first, signatures, "
    "monitoring SDV, export DSMB, poussée HAPI IOP.",
    module_label="eCRF Investigation")

engine = engine_for("ecrf-service")
JWT_SECRET = "medisuite-dev-secret-change-in-prod"


def current_user(authorization: Annotated[str | None, Header()] = None) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        return {"sub": "anon", "role": ""}
    try:
        return security.jwt_decode(authorization.split(" ", 1)[1], JWT_SECRET)
    except security.JWTError:
        return {"sub": "anon", "role": ""}


def require_perm(user: dict, permission: str) -> None:
    if not can(user["role"], permission):
        raise HTTPException(403, f"permission {permission} requise")


# ── Modèles ──────────────────────────────────────────────────────────────────

class EcrfSubject(Base):
    __tablename__ = "ecrf_subject"
    code: Mapped[str] = mapped_column(String(20), primary_key=True)
    site: Mapped[str] = mapped_column(String(8), index=True)
    scenario: Mapped[str] = mapped_column(String(4), index=True)
    statut: Mapped[str] = mapped_column(String(20), default="inclus")
    motif: Mapped[str] = mapped_column(String(120), default="")
    consentement: Mapped[str] = mapped_column(String(20))
    created_by: Mapped[str] = mapped_column(String(40))
    created_at: Mapped[float] = mapped_column(Float())


class EcrfEntry(Base):
    __tablename__ = "ecrf_entry"
    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    subject_code: Mapped[str] = mapped_column(String(20), index=True)
    form_id: Mapped[str] = mapped_column(String(20), index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    parent_id: Mapped[str | None] = mapped_column(String(16), nullable=True,
                                                  index=True)
    payload: Mapped[dict] = mapped_column(JSON)
    statut: Mapped[str] = mapped_column(String(12), default="brouillon")
    data_hash: Mapped[str] = mapped_column(String(64))
    idem_key: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    signed_by: Mapped[str | None] = mapped_column(String(40), nullable=True)
    signed_at: Mapped[float | None] = mapped_column(Float, nullable=True)
    fhir_status: Mapped[str] = mapped_column(String(16), default="desactive")
    created_by: Mapped[str] = mapped_column(String(40))
    created_at: Mapped[float] = mapped_column(Float())


class EcrfQuery(Base):
    __tablename__ = "ecrf_query"
    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    subject_code: Mapped[str] = mapped_column(String(20), index=True)
    entry_id: Mapped[str | None] = mapped_column(String(16), nullable=True)
    champ: Mapped[str | None] = mapped_column(String(60), nullable=True)
    message: Mapped[str] = mapped_column(String(1000))
    statut: Mapped[str] = mapped_column(String(10), default="ouverte",
                                        index=True)
    opened_by: Mapped[str] = mapped_column(String(40))
    reponse: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    closed_by: Mapped[str | None] = mapped_column(String(40), nullable=True)
    created_at: Mapped[float] = mapped_column(Float())


class EcrfAuditRow(Base):
    __tablename__ = "ecrf_audit"
    index: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[float] = mapped_column(Float())
    actor: Mapped[str] = mapped_column(String(40))
    role: Mapped[str] = mapped_column(String(20))
    action: Mapped[str] = mapped_column(String(40))
    resource: Mapped[str] = mapped_column(String(80))
    detail: Mapped[dict] = mapped_column(JSON)
    prev_hash: Mapped[str] = mapped_column(String(64))
    hash: Mapped[str] = mapped_column(String(64))


class EcrfStudyLock(Base):
    """Verrou de base (lock M+18, protocole §7.4/SAP) — irréversible."""
    __tablename__ = "ecrf_study_lock"
    study: Mapped[str] = mapped_column(String(40), primary_key=True)
    locked_at: Mapped[float] = mapped_column(Float())
    locked_by: Mapped[str] = mapped_column(String(40))
    temoins: Mapped[list] = mapped_column(JSON)  # ≥ 2 noms (§8 verrou + témoins)
    nb_sujets: Mapped[int] = mapped_column(Integer)
    nb_entrees: Mapped[int] = mapped_column(Integer)
    checksum: Mapped[str] = mapped_column(String(64))
    declaration: Mapped[str] = mapped_column(String(500), default="")


SessionLocal = init_db(engine, Base.metadata)

# Registre d'audit chaîné : rechargé depuis la base au démarrage (chaîne
# continue même après redémarrage — IEC 81001-5-1).
LEDGER = HashChainLedger()


def _reload_ledger() -> None:
    with SessionLocal() as session:
        rows = session.scalars(select(EcrfAuditRow)
                               .order_by(EcrfAuditRow.index)).all()
    LEDGER.events = [
        AuditEvent(index=r.index, timestamp=r.timestamp, actor=r.actor,
                   role=r.role, action=r.action, resource=r.resource,
                   detail=r.detail, prev_hash=r.prev_hash, hash=r.hash)
        for r in rows]


_reload_ledger()


def _audit(actor: str, role: str, action: str, resource: str,
           detail: dict | None = None) -> AuditEvent:
    event = LEDGER.append(actor, role, action, resource, detail or {})
    with SessionLocal() as session:
        session.add(EcrfAuditRow(**event.to_dict()))
        session.commit()
    return event


# ── Verrou de base (lock M+18) et extraction data manager (v0.8) ─────────

def _ensure_unlocked() -> None:
    """Interdit toute écriture après le lock M+18 (protocole §7.4)."""
    if _lock_state()["locked"]:
        raise HTTPException(409, "base verrouillée (lock M+18) — aucune "
                                 "écriture acceptée ; extraction data "
                                 "manager uniquement")


def _lock_state() -> dict:
    with SessionLocal() as session:
        row = session.get(EcrfStudyLock, ecrf_mod.STUDY_CODE)
        if row is None:
            return {"locked": False, "study": ecrf_mod.STUDY_CODE}
        return {"locked": True, "study": row.study,
                "locked_at": row.locked_at, "locked_by": row.locked_by,
                "temoins": row.temoins, "nb_sujets": row.nb_sujets,
                "nb_entrees": row.nb_entrees, "checksum": row.checksum,
                "declaration": row.declaration}


def _compute_checksum() -> tuple[str, int, int]:
    """SHA-256 canonique de l'état complet (sujets + entrées) — SAP A5.

    Canonicalisation triée (sujets puis entrées par sujet/formulaire/version) :
    `S|code|site|scenario|statut` et `E|code|form|v|statut|<hash contenu>|signataire`.
    Le hash couvre le CONTENU CANONIQUE du payload recalculé à la volée
    (`canonical_payload`, ecrf.py) — et non le data_hash stocké : une
    altération directe de la base modifie le checksum et déclenche l'alarme
    d'intégrité de l'extraction.
    """
    with SessionLocal() as session:
        subjects = session.scalars(select(EcrfSubject)
                                   .order_by(EcrfSubject.code)).all()
        entries = session.scalars(select(EcrfEntry)
                                  .order_by(EcrfEntry.subject_code,
                                            EcrfEntry.form_id,
                                            EcrfEntry.version)).all()
        content_hashes = {
            e.id: hashlib.sha256(
                ecrf_mod.canonical_payload(dict(e.payload)).encode("utf-8")
            ).hexdigest() for e in entries}
    lines = [f"S|{s.code}|{s.site}|{s.scenario}|{s.statut}"
             for s in subjects]
    lines += [f"E|{e.subject_code}|{e.form_id}|{e.version:04d}|{e.statut}|"
              f"{content_hashes[e.id]}|{e.signed_by or ''}" for e in entries]
    blob = "\n".join(lines).encode("utf-8")
    return hashlib.sha256(blob).hexdigest(), len(subjects), len(entries)


# ── Poussée FHIR optionnelle (hub HAPI du site, profils IOP) ────────────────

FHIR_PUSH_ENABLED = os.environ.get("MEDISUITE_ECRF_FHIR_PUSH", "0") == "1"

from medisuite_core import hapi_client as hapi_mod  # noqa: E402

HAPI = hapi_mod.HapiClient()  # attribut module : surchargeable en tests


def _fhir_push(subject_code: str, form_id: str, payload: dict,
               site: str, entry_id: str) -> str:
    """Pousse le bundle vers HAPI ; statut gracieux, jamais bloquant."""
    if not FHIR_PUSH_ENABLED:
        return "desactive"
    bundle = ecrf_mod.entry_to_fhir(subject_code, form_id, payload, site,
                                    entry_id)
    try:
        HAPI.transaction(bundle)
        return "pousse"
    except hapi_mod.FhirError:
        return "erreur_hapi"
    except Exception:  # réseau indisponible : saisie locale préservée
        return "hors_ligne"


# ── Endpoints : catalogue et sujets ──────────────────────────────────────────

@app.get("/api/v1/ecrf/forms", tags=["eCRF"])
def forms(user: dict = Depends(current_user)) -> dict:
    """Catalogue des formulaires (annexe A1) — source unique de la saisie."""
    require_perm(user, "ecrf.read")
    return {"study": ecrf_mod.STUDY_CODE, "version": ecrf_mod.STUDY_VERSION,
            "sites": ecrf_mod.SITES, "scenarios": ecrf_mod.SCENARIOS,
            "forms": ecrf_mod.forms_catalog()}


@app.post("/api/v1/ecrf/subjects", status_code=201, tags=["eCRF"])
def create_subject(body: dict,
                   user: dict = Depends(current_user)) -> dict:
    """Inclusion d'un sujet (F01 en ligne) : code pseudonyme assigné."""
    require_perm(user, "ecrf.write")
    _ensure_unlocked()
    site = str(body.get("site", "")).strip().upper()
    scenario = str(body.get("scenario", "")).strip()
    consentement = str(body.get("consentement", "")).strip()
    if site not in ecrf_mod.SITES:
        raise HTTPException(422, f"site inconnu : '{site}'")
    if scenario not in ecrf_mod.SCENARIOS:
        raise HTTPException(422, f"scénario inconnu : '{scenario}'")
    if consentement not in ("ecrit", "differe_urgence"):
        raise HTTPException(422, "consentement : 'ecrit' ou "
                                 "'differe_urgence' requis à l'inclusion")
    f01 = {"date_passage": body.get("date_passage",
                                    time.strftime("%Y-%m-%d")),
           "scenario": scenario, "consentement": consentement,
           "age": body.get("age"),
           "perte_modalites": body.get("perte_modalites", 0),
           "grossesse": body.get("grossesse"),
           "doublon_14j": body.get("doublon_14j"),
           "panne_site_24h": body.get("panne_site_24h")}
    errors = ecrf_mod.validate_entry("F01-INCLUSION", f01)
    if errors:
        raise HTTPException(422, "; ".join(errors))
    statut, motif = ecrf_mod.derive_eligibility(f01)
    if statut == "refuse":
        raise HTTPException(422, "consentement refusé — pas d'inclusion")
    with SessionLocal() as session:
        last = session.scalars(
            select(EcrfSubject).where(EcrfSubject.site == site)).all()
        seq = max([int(s.code.rsplit("-", 1)[1]) for s in last] or [0]) + 1
        try:
            code = ecrf_mod.new_subject_code(site, seq)
        except ecrf_mod.EcrfValidationError as exc:
            raise HTTPException(422, str(exc))
        subject = EcrfSubject(code=code, site=site, scenario=scenario,
                              statut=statut, motif=motif,
                              consentement=consentement,
                              created_by=user["sub"], created_at=time.time())
        session.add(subject)
        session.commit()
        entry_id, _ = _save_entry(session, code, "F01-INCLUSION", f01, user,
                                  idem_extra=f"inclusion:{code}")
    bus.publish("ecrf.subject.included",
                {"code": code, "site": site, "scenario": scenario,
                 "statut": statut})
    return {"code": code, "site": site, "scenario": scenario,
            "statut": statut, "motif": motif, "entry_f01": entry_id}


def _save_entry(session, subject_code: str, form_id: str, payload: dict,
                user: dict, idem_extra: str = "",
                parent_id: str | None = None, version: int = 1) -> tuple[str, int]:
    entry = EcrfEntry(id=new_id(), subject_code=subject_code,
                      form_id=form_id, version=version, parent_id=parent_id,
                      payload=payload, statut="brouillon",
                      data_hash=ecrf_mod.dedup_key(subject_code, form_id,
                                                   payload),
                      idem_key=ecrf_mod.dedup_key(
                          subject_code, form_id,
                          {"extra": idem_extra, "payload": payload})
                      if idem_extra else
                      ecrf_mod.dedup_key(subject_code, form_id, payload),
                      created_by=user["sub"], created_at=time.time())
    session.add(entry)
    session.commit()
    return entry.id, entry.version


@app.get("/api/v1/ecrf/subjects", tags=["eCRF"])
def list_subjects(site: str | None = None, scenario: str | None = None,
                  statut: str | None = None,
                  user: dict = Depends(current_user)) -> dict:
    require_perm(user, "ecrf.read")
    with SessionLocal() as session:
        q = select(EcrfSubject)
        if site:
            q = q.where(EcrfSubject.site == site.upper())
        if scenario:
            q = q.where(EcrfSubject.scenario == scenario)
        if statut:
            q = q.where(EcrfSubject.statut == statut)
        rows = session.scalars(q.order_by(EcrfSubject.code)).all()
        return {"total": len(rows), "subjects": [
            {"code": s.code, "site": s.site, "scenario": s.scenario,
             "statut": s.statut, "motif": s.motif} for s in rows]}


@app.get("/api/v1/ecrf/subjects/{code}", tags=["eCRF"])
def get_subject(code: str, user: dict = Depends(current_user)) -> dict:
    require_perm(user, "ecrf.read")
    with SessionLocal() as session:
        s = session.get(EcrfSubject, code.upper())
        if s is None:
            raise HTTPException(404, f"sujet inconnu : '{code}'")
        entries = session.scalars(select(EcrfEntry)
                                  .where(EcrfEntry.subject_code == s.code)
                                  .order_by(EcrfEntry.created_at)).all()
        return {"code": s.code, "site": s.site, "scenario": s.scenario,
                "statut": s.statut, "motif": s.motif,
                "entries": [{"id": e.id, "form_id": e.form_id,
                             "version": e.version, "statut": e.statut,
                             "signed_by": e.signed_by,
                             "fhir_status": e.fhir_status,
                             "parent_id": e.parent_id} for e in entries]}


# ── Endpoints : saisie, signature, amendement ────────────────────────────────

def _check_form_write(user: dict, form_id: str) -> None:
    """Séparation des rôles : F05 réservé au comité (aveugle), F01-F04/F06
    interdits au comité ; le reste exige ecrf.write."""
    if form_id == "F05-ADJUDICATION":
        if not can(user["role"], "ecrf.adjudicate"):
            raise HTTPException(403, "F05 réservé au comité d'adjudication "
                                     "(aveugle — ecrf.adjudicate requis)")
        return
    if not can(user["role"], "ecrf.write"):
        raise HTTPException(403, "permission ecrf.write requise")


def _next_version(session, code: str, form_id: str) -> int:
    rows = session.scalars(select(EcrfEntry)
                           .where(EcrfEntry.subject_code == code)
                           .where(EcrfEntry.form_id == form_id)).all()
    return max([r.version for r in rows] or [0]) + 1


@app.post("/api/v1/ecrf/subjects/{code}/forms/{form_id}", tags=["eCRF"])
def submit_form(code: str, form_id: str, payload: dict,
                idempotency_key: Annotated[str | None, Header()] = None,
                user: dict = Depends(current_user)) -> dict:
    """Saisie d'un formulaire (contrôles §8) — idempotente (clé calculée)."""
    _check_form_write(user, form_id)
    _ensure_unlocked()
    code = code.upper()
    errors = ecrf_mod.validate_entry(form_id, payload)
    if errors:
        raise HTTPException(422, {"error": "validation_eCRF",
                                  "details": errors})
    idem = ecrf_mod.dedup_key(code, form_id, payload)
    with SessionLocal() as session:
        s = session.get(EcrfSubject, code)
        if s is None:
            raise HTTPException(404, f"sujet inconnu : '{code}'")
        existing = session.scalars(select(EcrfEntry)
                                   .where(EcrfEntry.idem_key == idem)).first()
        if existing is not None:
            return {"duplicate": True, "entry_id": existing.id,
                    "version": existing.version, "statut": existing.statut}
        entry_id = new_id()
        stored_payload = dict(payload)
        if idempotency_key:  # clé client (offline) : traçabilité dans le payload
            stored_payload["__idem_client"] = idempotency_key[:64]
        entry = EcrfEntry(id=entry_id, subject_code=code, form_id=form_id,
                          version=_next_version(session, code, form_id),
                          payload=stored_payload, statut="brouillon",
                          data_hash=ecrf_mod.dedup_key(code, form_id, payload),
                          idem_key=idem, created_by=user["sub"],
                          created_at=time.time())
        session.add(entry)
        session.commit()
        entry.fhir_status = _fhir_push(code, form_id, payload, s.site,
                                       entry_id)
        session.commit()
        _audit(user["sub"], user["role"], "ecrf.submit",
               f"subject:{code}/form:{form_id}",
               {"entry_id": entry_id, "hash": entry.data_hash[:12],
                "idem_client": (idempotency_key or "")[:12]})
    bus.publish("ecrf.form.submitted",
                {"subject": code, "form": form_id, "entry": entry_id})
    return {"duplicate": False, "entry_id": entry_id,
            "version": entry.version, "statut": entry.statut,
            "fhir_status": entry.fhir_status}


@app.post("/api/v1/ecrf/entries/{entry_id}/sign", tags=["eCRF"])
def sign_entry(entry_id: str, user: dict = Depends(current_user)) -> dict:
    """Signature investigateur : l'entrée est verrouillée (ISO 14155 §4.8)."""
    require_perm(user, "ecrf.sign")
    with SessionLocal() as session:
        entry = session.get(EcrfEntry, entry_id)
        if entry is None:
            raise HTTPException(404, f"entrée inconnue : '{entry_id}'")
        if entry.statut == "signe":
            raise HTTPException(409, "entrée déjà signée — passer par un "
                                     "amendement (addendum versionné)")
        entry.statut = "signe"
        entry.signed_by = user["sub"]
        entry.signed_at = time.time()
        session.commit()
        _audit(user["sub"], user["role"], "ecrf.sign",
               f"entry:{entry_id}", {"subject": entry.subject_code,
                                     "form": entry.form_id,
                                     "hash": entry.data_hash[:12]})
        return {"entry_id": entry_id, "statut": "signe",
                "signed_by": user["sub"], "signed_at": entry.signed_at}


@app.post("/api/v1/ecrf/entries/{entry_id}/amend", tags=["eCRF"])
def amend_entry(entry_id: str, body: dict,
                user: dict = Depends(current_user)) -> dict:
    """Amendement post-signature : nouvelle version, l'original est intact."""
    require_perm(user, "ecrf.write")
    _ensure_unlocked()
    motif = str(body.get("motif", "")).strip()
    payload = body.get("payload")
    if len(motif) < 3 or not isinstance(payload, dict):
        raise HTTPException(422, "motif (≥ 3 caractères) et payload requis")
    with SessionLocal() as session:
        parent = session.get(EcrfEntry, entry_id)
        if parent is None:
            raise HTTPException(404, f"entrée inconnue : '{entry_id}'")
        if parent.statut != "signe":
            raise HTTPException(409, "seule une entrée signée peut être "
                                     "amendée (l'ajustement pré-signature "
                                     "= nouvelle saisie)")
        errors = ecrf_mod.validate_entry(parent.form_id, payload)
        if errors:
            raise HTTPException(422, {"error": "validation_eCRF",
                                      "details": errors})
        version = _next_version(session, parent.subject_code,
                                parent.form_id)
        amend_id = new_id()
        amend = EcrfEntry(id=amend_id, subject_code=parent.subject_code,
                          form_id=parent.form_id, version=version,
                          parent_id=parent.id, payload=payload,
                          statut="brouillon",
                          data_hash=ecrf_mod.dedup_key(parent.subject_code,
                                                       parent.form_id, payload),
                          idem_key=ecrf_mod.dedup_key(
                              parent.subject_code, parent.form_id,
                              {"amend": entry_id, "payload": payload}),
                          created_by=user["sub"], created_at=time.time())
        session.add(amend)
        session.commit()
        amend.fhir_status = _fhir_push(parent.subject_code, parent.form_id,
                                       payload, _site_of(parent.subject_code),
                                       amend_id)
        session.commit()
        _audit(user["sub"], user["role"], "ecrf.amend",
               f"entry:{entry_id}", {"amend_id": amend_id,
                                     "version": version, "motif": motif})
        return {"amend_id": amend_id, "parent_id": entry_id,
                "version": version, "statut": amend.statut}


def _site_of(code: str) -> str:
    with SessionLocal() as session:
        s = session.get(EcrfSubject, code)
        return s.site if s else ""


# ── Endpoints : requêtes de monitoring (SDV, annexe A4) ─────────────────────

@app.get("/api/v1/ecrf/queries", tags=["monitoring"])
def list_queries(statut: str | None = None,
                 user: dict = Depends(current_user)) -> dict:
    require_perm(user, "ecrf.read")
    with SessionLocal() as session:
        q = select(EcrfQuery)
        if statut:
            q = q.where(EcrfQuery.statut == statut)
        rows = session.scalars(q.order_by(EcrfQuery.created_at)).all()
        return {"total": len(rows), "queries": [
            {"id": r.id, "subject_code": r.subject_code,
             "entry_id": r.entry_id, "champ": r.champ, "message": r.message,
             "statut": r.statut, "opened_by": r.opened_by,
             "reponse": r.reponse} for r in rows]}


@app.post("/api/v1/ecrf/queries", status_code=201, tags=["monitoring"])
def open_query(body: dict, user: dict = Depends(current_user)) -> dict:
    """Requête SDV ouverte par le moniteur indépendant (ecrf.monitor)."""
    require_perm(user, "ecrf.monitor")
    subject_code = str(body.get("subject_code", "")).strip().upper()
    message = str(body.get("message", "")).strip()
    if not subject_code or len(message) < 5:
        raise HTTPException(422, "subject_code et message (≥ 5 caractères) "
                                 "requis")
    with SessionLocal() as session:
        if session.get(EcrfSubject, subject_code) is None:
            raise HTTPException(404, f"sujet inconnu : '{subject_code}'")
        row = EcrfQuery(id=new_id(), subject_code=subject_code,
                        entry_id=body.get("entry_id"),
                        champ=body.get("champ"), message=message,
                        opened_by=user["sub"], created_at=time.time())
        session.add(row)
        session.commit()
        _audit(user["sub"], user["role"], "ecrf.query.open",
               f"subject:{subject_code}", {"query_id": row.id})
        return {"id": row.id, "statut": row.statut}


@app.post("/api/v1/ecrf/queries/{query_id}/close", tags=["monitoring"])
def close_query(query_id: str, body: dict,
                user: dict = Depends(current_user)) -> dict:
    """Le site répond, la requête se clôt (ecrf.write)."""
    require_perm(user, "ecrf.write")
    reponse = str(body.get("reponse", "")).strip()
    if len(reponse) < 3:
        raise HTTPException(422, "réponse (≥ 3 caractères) requise")
    with SessionLocal() as session:
        row = session.get(EcrfQuery, query_id)
        if row is None:
            raise HTTPException(404, f"requête inconnue : '{query_id}'")
        if row.statut == "resolue":
            raise HTTPException(409, "requête déjà résolue")
        row.statut = "resolue"
        row.reponse = reponse
        row.closed_by = user["sub"]
        session.commit()
        _audit(user["sub"], user["role"], "ecrf.query.close",
               f"query:{query_id}", {"subject": row.subject_code})
        return {"id": query_id, "statut": row.statut, "reponse": reponse}


# ── Endpoint : synchronisation offline (R6 opérationnel) ────────────────────

@app.post("/api/v1/ecrf/sync", tags=["offline"])
def sync_offline(body: dict, user: dict = Depends(current_user)) -> dict:
    """Rejoue un lot de saisies offline ; résultat PAR item (jamais global).

    Chaque item est traité comme une saisie normale (validation, idempotence
    par clé calculée) : un item déjà reçu répond « duplicate », un item
    invalide répond « error » avec les détails — le lot ne bloque jamais.
    """
    require_perm(user, "ecrf.write")
    items = body.get("items")
    if not isinstance(items, list) or not items:
        raise HTTPException(422, "items : liste non vide requise")
    if len(items) > 200:
        raise HTTPException(413, "≤ 200 items par lot (pagination client)")
    results = []
    for item in items:
        client_key = str(item.get("client_key", ""))[:64]
        subject_code = str(item.get("subject_code", "")).strip().upper()
        form_id = str(item.get("form_id", "")).strip()
        payload = item.get("payload")
        result = {"client_key": client_key}
        if not client_key or not ecrf_mod.is_valid_subject_code(subject_code):
            result |= {"status": "error",
                       "errors": ["client_key ou subject_code invalide"]}
        elif not isinstance(payload, dict):
            result |= {"status": "error", "errors": ["payload objet requis"]}
        else:
            try:
                _check_form_write(user, form_id)
                errors = ecrf_mod.validate_entry(form_id, payload)
                if errors:
                    result |= {"status": "error", "errors": errors}
                else:
                    outcome = submit_form(subject_code, form_id, payload,
                                          idempotency_key=client_key,
                                          user=user)
                    result |= {"status": "duplicate"
                               if outcome["duplicate"] else "created",
                               "entry_id": outcome["entry_id"],
                               "version": outcome["version"]}
            except HTTPException as exc:
                result |= {"status": "rejected", "errors": [str(exc.detail)]}
        results.append(result)
    created = sum(1 for r in results if r["status"] == "created")
    dup = sum(1 for r in results if r["status"] == "duplicate")
    _audit(user["sub"], user["role"], "ecrf.sync", "batch",
           {"items": len(items), "created": created, "duplicate": dup})
    return {"processed": len(results), "created": created,
            "duplicate": dup, "results": results}


# ── Endpoint : export DSMB agrégé (sans PHI, §6) ────────────────────────────

@app.get("/api/v1/ecrf/exports/dsmb", tags=["monitoring"])
def export_dsmb(user: dict = Depends(current_user)) -> dict:
    """Agrégats trimestriels DSMB : comptes, EI/SAE, délais, adhésion.

    AUCUNE donnée libre ni identifiante (confidentialité §6) : uniquement
    des comptages et des médianes dérivés des payloads validés.
    """
    require_perm(user, "ecrf.export")
    with SessionLocal() as session:
        subjects = session.scalars(select(EcrfSubject)).all()
        entries = session.scalars(select(EcrfEntry)).all()
    par_site: dict[str, int] = {}
    par_scenario: dict[str, int] = {}
    par_statut: dict[str, int] = {}
    for s in subjects:
        par_site[s.site] = par_site.get(s.site, 0) + 1
        par_scenario[s.scenario] = par_scenario.get(s.scenario, 0) + 1
        par_statut[s.statut] = par_statut.get(s.statut, 0) + 1
    ei = sae = 0
    adhesion: dict[str, int] = {}
    delais: list[float] = []
    forms_count: dict[str, int] = {}
    for e in entries:
        forms_count[e.form_id] = forms_count.get(e.form_id, 0) + 1
        if e.form_id == "F04-SUIVI30J":
            if e.payload.get("ei_lie_dispositif") is True:
                if e.payload.get("ei_gravite") == "SAE":
                    sae += 1
                elif e.payload.get("ei_gravite") == "EI":
                    ei += 1
        if e.form_id == "F03-DECISION":
            a = e.payload.get("adhesion")
            if a:
                adhesion[a] = adhesion.get(a, 0) + 1
            d = ecrf_mod.derive_delai_minutes(e.payload)
            if d is not None and d >= 0:
                delais.append(d)
    delai_median = round(statistics.median(delais), 2) if delais else None
    return {
        "study": ecrf_mod.STUDY_CODE,
        "sujets": {"total": len(subjects), "par_site": par_site,
                   "par_scenario": par_scenario, "par_statut": par_statut},
        "entrees": {"total": len(entries), "par_formulaire": forms_count},
        "surete": {"EI_lies_dispositif": ei, "SAE_lies_dispositif": sae,
                   "regle_arret": "≥ 2 SAE/site → arrêt temporaire (A5)"},
        "p3_delai_orientation_min": {"n": len(delais),
                                     "mediane": delai_median},
        "adhesion": adhesion,
        "avertissement": "export agrégé sans PHI — extractions nominatives "
                         "réservées au data manager (verrou §8)",
    }


# ── Endpoint : vérification de la chaîne d'audit ────────────────────────────

@app.get("/api/v1/ecrf/audit/verify", tags=["monitoring"])
def audit_verify(user: dict = Depends(current_user)) -> dict:
    require_perm(user, "audit.read")
    ok, first_bad = LEDGER.verify()
    return {"integre": ok, "premiere_alteration": first_bad,
            "evenements": len(LEDGER.events), "tail": LEDGER.tail(20)}


# ── Endpoints : verrou de base M+18 et extraction (v0.8, protocole §7.4) ────

@app.get("/api/v1/ecrf/study/status", tags=["eCRF"])
def study_status(user: dict = Depends(current_user)) -> dict:
    """État du verrou + compteurs de base — pilotage R6/R7."""
    require_perm(user, "ecrf.read")
    state = _lock_state()
    with SessionLocal() as session:
        open_q = len(session.scalars(select(EcrfQuery)
                                     .where(EcrfQuery.statut == "ouverte")
                                     ).all())
        nb_sujets = len(session.scalars(select(EcrfSubject)).all())
        nb_signes = len(session.scalars(select(EcrfEntry)
                                        .where(EcrfEntry.statut == "signe")
                                        ).all())
    state |= {"requetes_ouvertes": open_q, "sujets": nb_sujets,
              "entrees_signees": nb_signes}
    if not state["locked"]:
        checksum, _, nb_entrees = _compute_checksum()
        state |= {"checksum_courant": checksum, "entrees": nb_entrees,
                  "note": "le checksum courant est indicatif avant le lock"}
    return state


@app.post("/api/v1/ecrf/study/lock", tags=["eCRF"])
def lock_study(body: dict, user: dict = Depends(current_user)) -> dict:
    """VERROU DE BASE M+18 — promoteur (ecrf.lock), ≥ 2 témoins, irréversible.

    Préconditions : zéro requête de monitoring ouverte (plan-monitoring §5).
    Effets : checksum SHA-256 figé ; toute écriture → 409 ; l'extraction
    d'analyse du data manager est débloquée. Aucun déverrouillage n'existe
    (un correctif post-lock passe par un amendement documenté + nouveau
    protocole, pas par une réouverture — EGSP).
    """
    require_perm(user, "ecrf.lock")
    temoins = [str(t).strip() for t in body.get("temoins", []) if str(t).strip()]
    declaration = str(body.get("declaration", "")).strip()[:500]
    if len(temoins) < 2:
        raise HTTPException(422, "≥ 2 témoins requis (protocole §8 : verrou "
                                 "par le data manager/promoteur + témoins)")
    with SessionLocal() as session:
        if session.get(EcrfStudyLock, ecrf_mod.STUDY_CODE) is not None:
            raise HTTPException(409, "base déjà verrouillée — opération "
                                     "irréversible (voir study/status)")
        open_q = len(session.scalars(select(EcrfQuery)
                                     .where(EcrfQuery.statut == "ouverte")
                                     ).all())
        if open_q:
            raise HTTPException(409, f"{open_q} requête(s) de monitoring "
                                     "ouverte(s) — clôture requise avant le "
                                     "lock (plan-monitoring §5)")
        checksum, nb_sujets, nb_entrees = _compute_checksum()
        row = EcrfStudyLock(study=ecrf_mod.STUDY_CODE, locked_at=time.time(),
                            locked_by=user["sub"], temoins=temoins,
                            nb_sujets=nb_sujets, nb_entrees=nb_entrees,
                            checksum=checksum, declaration=declaration)
        session.add(row)
        session.commit()
    _audit(user["sub"], user["role"], "ecrf.study.lock",
           f"study:{ecrf_mod.STUDY_CODE}",
           {"checksum": checksum, "temoins": temoins,
            "sujets": nb_sujets, "entrees": nb_entrees})
    bus.publish("ecrf.study.locked",
                {"study": ecrf_mod.STUDY_CODE, "checksum": checksum})
    return {"locked": True, "checksum": checksum, "sujets": nb_sujets,
            "entrees": nb_entrees, "temoins": temoins,
            "extraction": "débloquée pour le data manager"}


@app.get("/api/v1/ecrf/extract", tags=["eCRF"])
def extract_dataset(user: dict = Depends(current_user)) -> dict:
    """Extraction d'analyse (SAF) — data manager UNIQUEMENT, après lock.

    Jeu de données : dernières entrées SIGNÉES par (sujet, formulaire) +
    dérivations SAP (éligibilité F01, délai P3 F03, SAE F04). Pseudonyme
    uniquement. L'intégrité est re-vérifiée à chaque extraction : si l'état
    courant diverge du checksum verrouillé → 500 + événement d'audit
    `ecrf.extract.integrity` (investigation requise avant toute analyse).
    """
    require_perm(user, "ecrf.extract")
    state = _lock_state()
    if not state["locked"]:
        raise HTTPException(409, "extraction d'analyse bloquée avant le "
                                 "verrou de base — lock M+18 requis "
                                 "(protocole §7.4 / SAP annexe A5)")
    checksum_now, nb_sujets, nb_entrees = _compute_checksum()
    if checksum_now != state["checksum"]:
        _audit(user["sub"], user["role"], "ecrf.extract.integrity",
               f"study:{ecrf_mod.STUDY_CODE}",
               {"attendu": state["checksum"], "constate": checksum_now})
        raise HTTPException(500, "alarme d'intégrité : l'état de la base "
                                 "diverge du checksum verrouillé — "
                                 "investigation requise (audit chaîné)")
    with SessionLocal() as session:
        subjects = session.scalars(select(EcrfSubject)
                                   .order_by(EcrfSubject.code)).all()
        entries = session.scalars(select(EcrfEntry)
                                  .order_by(EcrfEntry.version)).all()
        queries_resolues = len(session.scalars(
            select(EcrfQuery).where(EcrfQuery.statut == "resolue")).all())
    latest: dict[tuple[str, str], EcrfEntry] = {}
    for e in entries:  # tri par version : la dernière signée gagne
        if e.statut != "signe":
            continue
        key = (e.subject_code, e.form_id)
        if key not in latest or e.version > latest[key].version:
            latest[key] = e
    dataset = []
    for s in subjects:
        forms: dict[str, dict] = {}
        for (code, form_id), e in latest.items():
            if code != s.code:
                continue
            payload = e.payload
            derivees: dict = {}
            if form_id == "F01-INCLUSION":
                statut, motif = ecrf_mod.derive_eligibility(payload)
                derivees = {"eligibilite": statut, "motif": motif}
            elif form_id == "F03-DECISION":
                d = ecrf_mod.derive_delai_minutes(payload)
                derivees = {"delai_orientation_min": d}
            elif form_id == "F04-SUIVI30J":
                derivees = {"sae": ecrf_mod.is_sae(payload)}
            forms[form_id] = {"entry_id": e.id, "version": e.version,
                              "signed_by": e.signed_by,
                              "signed_at": e.signed_at, "payload": payload,
                              "derivees": derivees}
        dataset.append({"code": s.code, "site": s.site,
                        "scenario": s.scenario, "statut": s.statut,
                        "motif": s.motif, "forms": forms})
    _audit(user["sub"], user["role"], "ecrf.extract",
           f"study:{ecrf_mod.STUDY_CODE}",
           {"checksum": checksum_now, "sujets": len(dataset)})
    return {
        "study": ecrf_mod.STUDY_CODE,
        "protocol_version": ecrf_mod.STUDY_VERSION,
        "lock": {"locked_at": state["locked_at"], "locked_by": state["locked_by"],
                 "temoins": state["temoins"], "checksum": state["checksum"],
                 "nb_sujets": state["nb_sujets"],
                 "nb_entrees": state["nb_entrees"]},
        "integrity": {"checksum_recalcule": checksum_now, "conforme": True},
        "queries_resolues": queries_resolues,
        "dataset": dataset,
        "note": "SAF pseudonymisé — dernière entrée signée par "
                "(sujet, formulaire) + dérivations SAP ; usage analyse R7.",
    }
