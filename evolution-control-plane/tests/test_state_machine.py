"""Verrou : machine à états stricte du cycle d'évolution."""
from __future__ import annotations

import pytest

from ecp.domain.proposal.entities import Proposal
from ecp.domain.proposal.enums import ChangeClass, Outcome, ProposalState, ProposalType
from ecp.domain.proposal.policies import (GateMissing, TransitionDenied,
                                          assert_transition)
from ecp.domain.proposal.value_objects import ProposalId


def _proposal(jusqua_decision: bool = False) -> Proposal:
    p = Proposal(id=ProposalId("PROP-9001"), title="Test lifecycle proposal",
                 type=ProposalType.FEATURE, requested_by="tester")
    p.submit()
    if jusqua_decision:
        for etat in (ProposalState.VALIDATED, ProposalState.CLASSIFIED,
                     ProposalState.IMPACT_ANALYSIS, ProposalState.RISK_ASSESSMENT,
                     ProposalState.DECISION_PENDING):
            p.transition(etat, "system")
    return p


def test_chemin_ferique_complet_jusqua_acceptation():
    p = _proposal()  # SUBMITTED
    chemin = [ProposalState.VALIDATED, ProposalState.CLASSIFIED,
              ProposalState.IMPACT_ANALYSIS, ProposalState.RISK_ASSESSMENT,
              ProposalState.DECISION_PENDING, ProposalState.APPROVED,
              ProposalState.CHANGE_PLANNED, ProposalState.IMPLEMENTATION,
              ProposalState.TECHNICAL_VALIDATION, ProposalState.CLINICAL_VALIDATION,
              ProposalState.SAFETY_VALIDATION, ProposalState.RELEASE_CANDIDATE,
              ProposalState.CANARY, ProposalState.PILOT, ProposalState.ROLLOUT,
              ProposalState.RELEASED, ProposalState.MONITORED,
              ProposalState.ACCEPTED]
    for etat in chemin:
        if etat is ProposalState.APPROVED:
            p.decide(Outcome.APPROVED, "maintainer", "ok")
        else:
            p.transition(etat, "system")
    assert p.status is ProposalState.ACCEPTED
    assert len(p.history) == len(chemin) + 1  # + SUBMITTED


def test_transitions_interdites_relevees():
    with pytest.raises(TransitionDenied):
        assert_transition(ProposalState.DRAFT, ProposalState.APPROVED)
    with pytest.raises(TransitionDenied):
        assert_transition(ProposalState.SUBMITTED, ProposalState.CANARY)
    with pytest.raises(TransitionDenied):
        assert_transition(ProposalState.MONITORED, ProposalState.DRAFT)


def test_reject_et_rollback_sont_terminaux():
    p = _proposal(jusqua_decision=True)
    p.decide(Outcome.REJECTED, "committee", "hors périmètre V1")
    assert p.status is ProposalState.REJECTED
    with pytest.raises(TransitionDenied):
        p.transition(ProposalState.VALIDATED)


def test_deferred_est_reactivable():
    p = _proposal(jusqua_decision=True)  # déjà en DECISION_PENDING
    p.decide(Outcome.DEFERRED, "committee", "attend R6")
    p.transition(ProposalState.VALIDATED, "system", "réactivation")
    assert p.status is ProposalState.VALIDATED


def test_gates_manquants_bloquent_la_release_p8():
    with pytest.raises(GateMissing):
        assert_transition(ProposalState.CLINICAL_VALIDATION,
                          ProposalState.SAFETY_VALIDATION, ChangeClass.P8,
                          provided_gates=set())


def test_etats_emettent_un_historique_immuable_en_memoire():
    p = _proposal()
    p.transition(ProposalState.VALIDATED, "alice", "r1")
    evt = p.history[-1]
    assert evt["event"] == "PROPOSAL_TRANSITION"
    assert evt["previous_state"] == "SUBMITTED" and evt["new_state"] == "VALIDATED"
    assert evt["actor"] == "alice"
