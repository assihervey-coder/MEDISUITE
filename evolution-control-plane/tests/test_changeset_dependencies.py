"""Verrou : change sets immuables + ordonnancement sans cycle."""
from __future__ import annotations

import hashlib

import pytest

from ecp.domain.change.change_set import ChangeSet
from ecp.domain.change.dependencies import topological_order
from ecp.domain.proposal.value_objects import ChangeSetId


def _cs() -> ChangeSet:
    cs = ChangeSet(id=ChangeSetId("CHG-9001"), proposal="PROP-9001",
                   baseline_version="0.15.0", baseline_commit="18d2b4d",
                   target_version="0.16.0",
                   modifications=["ADD"], affected_components=["patient-context"])
    cs.add_unit(type("U", (), {"to_dict": lambda self: {"component": "patient-context"}})())
    return cs


def test_freeze_produit_checksum_deterministe():
    cs = _cs()
    c1 = cs.freeze()
    assert len(c1) == 64
    cs2 = _cs()
    assert cs2.freeze() == c1  # déterministe (tri des clés)


def test_change_set_fige_est_immuable():
    cs = _cs()
    cs.freeze()
    with pytest.raises(RuntimeError):
        cs.add_unit(type("U", (), {"to_dict": lambda self: {}})())
    assert cs.frozen is True


def test_ordre_topologique_simple():
    order = topological_order([("a", []), ("b", ["a"]), ("c", ["a", "b"])])
    assert order.index("a") < order.index("b") < order.index("c")


def test_cycle_detecte():
    with pytest.raises(ValueError, match="cycle"):
        topological_order([("a", ["b"]), ("b", ["a"])])


def test_dependance_inconnue_detectee():
    with pytest.raises(ValueError, match="inconnues"):
        topological_order([("a", ["fantome"])])


def test_contrat_changeset_to_dict():
    cs = _cs()
    cs.freeze()
    d = cs.to_dict()
    for champ in ("id", "proposal", "baseline", "target", "modifications",
                  "affected_components", "migration_required",
                  "rollback_supported", "checksum", "immutable"):
        assert champ in d
    assert d["immutable"] is True
