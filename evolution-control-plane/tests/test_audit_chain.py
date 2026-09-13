"""Verrou : chaîne d'audit WORM (SHA-256, altération détectée)."""
from __future__ import annotations

from ecp.adapters.repository.audit import AuditChain


def test_chaine_intacte(tmp_path):
    chain = AuditChain(tmp_path / "events.jsonl")
    chain.append("PROPOSAL_APPROVED", actor="committee", proposal_id="PROP-0001",
                 previous_state="DECISION_PENDING", new_state="APPROVED",
                 reason="quorum P7", evidence_id="EVD-8821")
    chain.append("CHANGE_SET_CREATED", actor="api", change_set="CHG-0001")
    ok, bad_index = chain.verify_chain()
    assert ok and bad_index == -1
    assert chain.last_hash() != "0" * 64


def test_alteration_casse_la_chaine(tmp_path):
    import json
    path = tmp_path / "events.jsonl"
    chain = AuditChain(path)
    chain.append("EVT_1", actor="a")
    chain.append("EVT_2", actor="b")
    chain.append("EVT_3", actor="c")
    lines = path.read_text(encoding="utf-8").splitlines()
    # falsification : on modifie le premier enregistrement
    forged = json.loads(lines[0])
    forged["record"]["actor"] = "intrus"
    lines[0] = json.dumps(forged, ensure_ascii=False)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    chain2 = AuditChain(path)
    ok, bad_index = chain2.verify_chain()
    assert not ok and bad_index == 0


def test_genesis_sur_chaine_vide(tmp_path):
    chain = AuditChain(tmp_path / "vide.jsonl")
    assert chain.last_hash() == "0" * 64
    assert chain.verify_chain() == (True, -1)
