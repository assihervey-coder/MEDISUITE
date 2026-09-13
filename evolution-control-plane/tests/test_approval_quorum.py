"""Verrou : matrice d'approbation (quorum, séparation des devoirs)."""
from __future__ import annotations

import pytest

from ecp.domain.decision.decision import (QuorumNotMet, evaluate_quorum,
                                          required_roles)
from ecp.domain.decision.entities import Approval
from ecp.application.decision.approve import approve


def test_roles_requis_par_classe():
    assert required_roles("P1") == []
    assert required_roles("P3") == ["maintainer"]
    assert set(required_roles("P7")) == {"clinical_lead", "safety_officer"}
    assert set(required_roles("P8")) == {"clinical_lead", "safety_officer",
                                         "security_officer"}
    assert set(required_roles("P9")) == {"regulatory_affairs", "clinical_lead",
                                         "safety_officer"}


def test_quorum_p7_complet_passe():
    d = evaluate_quorum("PROP-9003", "P7",
                        [Approval(role="clinical_lead", actor="dr.kouassi"),
                         Approval(role="safety_officer", actor="s.fda")])
    assert d.outcome == "APPROVED"


def test_quorum_incomplet_rejete():
    with pytest.raises(QuorumNotMet, match="manquants"):
        evaluate_quorum("PROP-9004", "P8",
                        [Approval(role="clinical_lead", actor="dr.k")])


def test_quorum_p9_exige_trois_roles():
    with pytest.raises(QuorumNotMet):
        evaluate_quorum("PROP-9004b", "P9",
                        [Approval(role="regulatory_affairs", actor="r.a"),
                         Approval(role="clinical_lead", actor="dr.k")])


def test_auto_approbation_interdite():
    with pytest.raises(QuorumNotMet, match="auto|séparation|auteur"):
        evaluate_quorum("PROP-9005", "P3",
                        [Approval(role="maintainer", actor="alice")],
                        author="alice")


def test_use_case_approve_retourne_erreur_lisible():
    result = approve("PROP-9006", "P9",
                     [{"role": "regulatory_affairs", "actor": "r.a"}],
                     author="r.a")
    assert result["approved"] is False
    assert "required_roles" in result
