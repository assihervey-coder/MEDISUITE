"""Verrou : classification P0-P9 (planchers par type/chemins, non abaissables)."""
from __future__ import annotations

import pytest

from ecp.domain.proposal.enums import ChangeClass, ProposalState, ProposalType
from ecp.domain.proposal.policies import classify_by_paths


def test_plancher_par_type():
    assert classify_by_paths([], ProposalType.FEATURE) is ChangeClass.P3
    assert classify_by_paths([], ProposalType.ARCHITECTURE) is ChangeClass.P4
    assert classify_by_paths([], ProposalType.DATA) is ChangeClass.P5
    assert classify_by_paths([], ProposalType.AI) is ChangeClass.P6
    assert classify_by_paths([], ProposalType.CLINICAL) is ChangeClass.P7
    assert classify_by_paths([], ProposalType.SECURITY) is ChangeClass.P8
    assert classify_by_paths([], ProposalType.REGULATORY) is ChangeClass.P9


def test_regles_de_chemins_reelles_du_repo():
    assert classify_by_paths(["packages/clinical-rules/medisuite_rules/scores.py"],
                             ) is ChangeClass.P7
    assert classify_by_paths(["ai/multimodal/core/fusion_engine.py"]) is ChangeClass.P6
    assert classify_by_paths(["migrations/database/expand/001.sql"]) is ChangeClass.P5
    assert classify_by_paths(["security/hardening/vault/init_secrets.sh"]) is ChangeClass.P8
    assert classify_by_paths(["compliance/mdr/technical-documentation/03-x.md"]) is ChangeClass.P9


def test_classe_la_plus_haute_gagne():
    klass = classify_by_paths(["packages/clinical-rules/x.py",
                               "ai/multimodal/y.py"])
    assert klass is ChangeClass.P7  # P7 > P6


def test_breaking_change_monte_au_moins_p4():
    assert classify_by_paths(["README.md"], breaking_change=True) is ChangeClass.P4


def test_documentaire_seul_p1():
    assert classify_by_paths(["docs/README.md"]) is ChangeClass.P1


def test_override_ne_peut_pas_abaisser():
    # max() dans l'agrégat : override P2 reste P7
    from ecp.domain.proposal.entities import Proposal
    from ecp.domain.proposal.value_objects import ProposalId
    p = Proposal(id=ProposalId("PROP-9002"),
                 title="Clinical override attempt here",
                 type=ProposalType.CLINICAL,
                 requested_by="tester",
                 affected_domains=["clinical"],
                 changed_paths=["packages/clinical-rules/scores.py"])
    p.submit()
    p.transition(ProposalState.VALIDATED, "system", "complète")
    klass = p.classify(override=ChangeClass.P2)
    assert klass is ChangeClass.P7
