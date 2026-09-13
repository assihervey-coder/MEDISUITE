"""Routeurs assessments / decisions / changes / validations / rollouts / rollbacks."""
from __future__ import annotations

import importlib

from fastapi import APIRouter, HTTPException

from ..._bridge import register
from ..schemas.assessment import (AssessIn, ChangeSetIn, RollbackIn, RolloutIn,
                                  ValidationIn)

register()

_impact_uc = importlib.import_module("ecp.application.analysis.analyze_impact")
_risk_uc = importlib.import_module("ecp.application.analysis.calculate_risk")
_blast_uc = importlib.import_module("ecp.application.analysis.calculate_blast_radius")
_create_cs = importlib.import_module("ecp.application.implementation.create_change_set")
_verify_cs = importlib.import_module("ecp.application.implementation.verify_change")
_finalize = importlib.import_module("ecp.application.implementation.finalize_change")
_run_validation = importlib.import_module("ecp.application.validation.run_validation")
_run_regression = importlib.import_module("ecp.application.validation.run_regression")
_start_rollout = importlib.import_module("ecp.application.rollout.start_rollout")
_advance_rollout = importlib.import_module("ecp.application.rollout.advance_rollout")
_complete_rollout = importlib.import_module("ecp.application.rollout.complete_rollout")
_stages = importlib.import_module("ecp.domain.rollout.stages")
_init_rollback = importlib.import_module("ecp.application.rollback.initiate_rollback")
_exec_rollback = importlib.import_module("ecp.application.rollback.execute_rollback")
_verify_rollback = importlib.import_module("ecp.application.rollback.verify_rollback")
_events = importlib.import_module("ecp.domain.proposal.events")

from ._state import STATE  # noqa: E402

assessments = APIRouter(prefix="/assessments", tags=["assessments"])


@assessments.post("", status_code=201)
def create_assessment(payload: AssessIn) -> dict:
    counts = _impact_uc.analyze_impact(payload.changed_paths)
    risk = _risk_uc.calculate_risk(payload.impacts)
    blast = _blast_uc.calculate_blast_radius(counts, risk["risk"]["level"],
                                             payload.breaking, payload.cross_domain)
    return {"impact": counts, "risk": risk["risk"], "blast_radius": blast["blast_radius"]}


changes = APIRouter(prefix="/changes", tags=["changes"])


@changes.post("", status_code=201)
def create_change(payload: ChangeSetIn) -> dict:
    cs = _create_cs.create_change_set(payload.proposal_id, payload.baseline_version,
                                      payload.baseline_commit, payload.target_version,
                                      payload.units, payload.migration_required)
    STATE.changes[cs["id"]] = cs
    _events.emit(_events.CHANGE_SET_CREATED, change_set=cs["id"])
    STATE.audit.append("CHANGE_SET_CREATED", actor="api", change_set=cs["id"],
                       proposal=payload.proposal_id)
    return cs


@changes.get("/{cid}")
def get_change(cid: str) -> dict:
    if cid not in STATE.changes:
        raise HTTPException(404, f"change set inconnu : {cid}")
    return STATE.changes[cid]


@changes.post("/{cid}/validate")
def validate_change(cid: str, payload: ValidationIn) -> dict:
    if cid not in STATE.changes:
        raise HTTPException(404, f"change set inconnu : {cid}")
    cs = STATE.changes[cid]
    verification = _verify_cs.verify_change(cs)
    if not verification["verified"]:
        raise HTTPException(409, "change set non vérifiable")
    _test_plan = importlib.import_module("ecp.application.planning.generate_test_plan")
    klass = payload.facts.get("change_class", "P4")
    plan = _test_plan.generate_test_plan(
        [path for u in cs["units"] for path in u.get("paths", [])], klass)
    result = _run_validation.run_validation(cs, plan, payload.facts)
    STATE.validations[cid] = result
    _events.emit(_events.VALIDATION_COMPLETED, change_set=cid,
                 overall=result["results"]["compatibility"])
    return result


@changes.post("/{cid}/release")
def release_change(cid: str) -> dict:
    if cid not in STATE.changes:
        raise HTTPException(404, f"change set inconnu : {cid}")
    return _finalize.finalize_change(STATE.changes[cid], {"verified": True})


validations = APIRouter(prefix="/validations", tags=["validations"])


@validations.post("/regression")
def regression(payload: dict) -> dict:
    return _run_regression.run_regression(payload.get("suites", []))


rollouts = APIRouter(prefix="/releases", tags=["rollouts"])


@rollouts.post("/{rid}/deploy", status_code=201)
def deploy(rid: str, payload: RolloutIn) -> dict:
    try:
        result = _start_rollout.start_rollout(rid, payload.change_class,
                                              payload.checkpoints)
    except Exception as exc:  # noqa: BLE001 — CheckpointsIncomplete etc.
        raise HTTPException(422, str(exc)) from exc
    STATE.rollouts[rid] = result
    _events.emit(_events.ROLLOUT_STARTED, release=rid)
    return result


@rollouts.post("/{rid}/pause")
def pause(rid: str, reason: str = "pause demandée") -> dict:
    if rid not in STATE.rollouts:
        raise HTTPException(404, f"rollout inconnu : {rid}")
    plan = _stages.RolloutPlan(rid, [s["name"] for s in
                                     STATE.rollouts[rid]["rollout"]["stages"]])
    result = importlib.import_module(
        "ecp.application.rollout.pause_rollout").pause_rollout(plan, reason)
    STATE.rollouts[rid]["rollout"] = result["rollout"]
    _events.emit(_events.ROLLOUT_PAUSED, release=rid, reason=reason)
    return result


@rollouts.post("/{rid}/rollback")
def rollback_release(rid: str, payload: RollbackIn) -> dict:
    initiation = _init_rollback.initiate_rollback(payload.metrics, payload.alerts,
                                                  payload.human_decision)
    if not initiation.get("rollback_required"):
        return {"rollback": False, **initiation}
    rb_id = f"RBK-{abs(hash(rid)) % 9000 + 1000}"
    execution = _exec_rollback.execute_rollback(rb_id, rid,
                                                payload.checkpoints_restored)
    STATE.rollbacks[rb_id] = execution
    return {"rollback": True, "initiation": initiation, "execution": execution}


rollbacks = APIRouter(prefix="/rollbacks", tags=["rollbacks"])


@rollbacks.post("/{rbid}/verify")
def verify(rbid: str, smoke_passed: bool = True, chain_intact: bool = True,
           flags_off: bool = True) -> dict:
    return _verify_rollback.verify_rollback(rbid, smoke_passed, chain_intact, flags_off)
