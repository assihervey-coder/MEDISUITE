"""Routeur proposals — cycle de vie via l'API."""
from __future__ import annotations

import importlib

from fastapi import APIRouter, HTTPException

from ..._bridge import register
from ..schemas.proposal import ProposalIn

register()

_drepo = importlib.import_module("ecp.domain.proposal.repository")
_denums = importlib.import_module("ecp.domain.proposal.enums")
_intake_submit = importlib.import_module("ecp.application.intake.submit_proposal")
_intake_validate = importlib.import_module("ecp.application.intake.validate_proposal")
_intake_classify = importlib.import_module("ecp.application.intake.classify_proposal")
_generate_assessment = importlib.import_module(
    "ecp.application.analysis.generate_assessment")
_approve_uc = importlib.import_module("ecp.application.decision.approve")
_events = importlib.import_module("ecp.domain.proposal.events")

from ._state import STATE  # noqa: E402 — après register()

router = APIRouter(prefix="/proposals", tags=["proposals"])


def _get(pid: str):
    p = STATE.proposals.get(_drepo.ProposalId(pid))
    if p is None:
        raise HTTPException(404, f"proposition inconnue : {pid}")
    return p


def _impact_dict(p) -> dict[str, str]:
    iv = p.impacts
    return {"clinical": iv.clinical.value, "patient_safety": iv.patient_safety.value,
            "security": iv.security.value, "data": iv.data.value,
            "api": iv.api.value, "ai": iv.ai.value}


@router.get("")
def list_proposals() -> list[dict]:
    return [p.to_dict() for p in STATE.proposals.list()]


@router.post("", status_code=201)
def create_proposal(payload: ProposalIn) -> dict:
    proposal = _intake_submit.submit(payload.model_dump(), repo=STATE.proposals)
    _events.emit(_events.PROPOSAL_SUBMITTED, proposal_id=proposal.id.value)
    STATE.audit.append("PROPOSAL_SUBMITTED", actor=payload.requested_by,
                       proposal_id=proposal.id.value)
    return proposal.to_dict()


@router.get("/{pid}")
def get_proposal(pid: str) -> dict:
    return _get(pid).to_dict()


@router.post("/{pid}/validate")
def validate_proposal(pid: str) -> dict:
    p = _get(pid)
    result = _intake_validate.validate(p)
    STATE.proposals.save(p)
    return result


@router.post("/{pid}/classify")
def classify_proposal(pid: str) -> dict:
    p = _get(pid)
    result = _intake_classify.classify(p)
    STATE.proposals.save(p)
    return result


@router.post("/{pid}/analyze")
def analyze_proposal(pid: str) -> dict:
    p = _get(pid)
    assessment = _generate_assessment.generate_assessment(
        pid, p.changed_paths, _impact_dict(p), p.breaking_change,
        len(p.affected_domains) > 1)
    STATE.assessments[pid] = assessment
    if p.status.value == "CLASSIFIED":
        p.transition(_denums.ProposalState.IMPACT_ANALYSIS, "api", "impact analysé")
        p.transition(_denums.ProposalState.RISK_ASSESSMENT, "api", "risque évalué")
        p.transition(_denums.ProposalState.DECISION_PENDING, "api", "prêt à décider")
        STATE.proposals.save(p)
    return assessment


@router.get("/{pid}/impact")
def get_impact(pid: str) -> dict:
    p = _get(pid)
    if pid not in STATE.assessments:
        raise HTTPException(404, "assessment absent — lancer POST /analyze")
    return STATE.assessments[pid]["impact"] | {"proposal_id": pid}


@router.get("/{pid}/risk")
def get_risk(pid: str) -> dict:
    if pid not in STATE.assessments:
        raise HTTPException(404, "assessment absent — lancer POST /analyze")
    return STATE.assessments[pid]["risk"]


@router.get("/{pid}/tests")
def get_tests(pid: str) -> dict:
    if pid not in STATE.assessments:
        raise HTTPException(404, "assessment absent — lancer POST /analyze")
    _test_plan = importlib.import_module("ecp.application.planning.generate_test_plan")
    klass = (STATE.proposals.get(_drepo.ProposalId(pid)).change_class.value
             if STATE.proposals.get(_drepo.ProposalId(pid)).change_class else "P3")
    return _test_plan.generate_test_plan(
        STATE.proposals.get(_drepo.ProposalId(pid)).changed_paths, klass)


@router.post("/{pid}/approve")
def approve_proposal(pid: str, approvals: list[dict] | None = None,
                     actor: str = "committee", reason: str = "") -> dict:
    p = _get(pid)
    if p.status.value != "DECISION_PENDING":
        raise HTTPException(409, f"état {p.status.value} ≠ DECISION_PENDING")
    klass = p.change_class.value if p.change_class else "P3"
    result = _approve_uc.approve(pid, klass, approvals or [], author=p.requested_by)
    if not result.get("approved"):
        raise HTTPException(403, result.get("reason", "quorum non atteint"))
    p.decide(_denums.Outcome.APPROVED, actor, reason)
    STATE.audit.append("PROPOSAL_APPROVED", actor=actor, proposal_id=pid,
                       previous_state="DECISION_PENDING", new_state="APPROVED",
                       reason=reason)
    STATE.proposals.save(p)
    return result


@router.post("/{pid}/reject")
def reject_proposal(pid: str, actor: str = "committee", reason: str = "") -> dict:
    p = _get(pid)
    try:
        p.decide(_denums.Outcome.REJECTED, actor, reason)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(409, str(exc)) from exc
    STATE.audit.append("PROPOSAL_REJECTED", actor=actor, proposal_id=pid, reason=reason)
    STATE.proposals.save(p)
    return {"rejected": True, "proposal_id": pid}
