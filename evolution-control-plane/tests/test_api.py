"""Verrou : API REST /api/v1/evolution — parcours e2e complet (TestClient)."""
from __future__ import annotations

import importlib

import pytest

fastapi = pytest.importorskip("fastapi")

app_mod = importlib.import_module("evolution-control-plane.api.rest.app")
from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture()
def client():
    return TestClient(app_mod.app)


def test_health(client):
    r = client.get("/api/v1/evolution/health")
    assert r.status_code == 200
    assert r.json()["principle"] == "NO DIRECT CHANGE"


def test_parcours_complet_proposition_vers_approbation(client):
    payload = {
        "title": "Ajout patient-context digital twin",
        "type": "ARCHITECTURE",
        "requested_by": "archi",
        "affected_domains": ["patient", "ai"],
        "changed_paths": ["services/patient-service/src/main.py"],
        "breaking_change": False,
        "patient_safety_impact": "MEDIUM", "clinical_impact": "MEDIUM",
    }
    r = client.post("/api/v1/evolution/proposals", json=payload)
    assert r.status_code == 201
    pid = r.json()["id"]
    assert pid.startswith("PROP-")

    assert client.post(f"/api/v1/evolution/proposals/{pid}/validate").json()["valid"]
    cls = client.post(f"/api/v1/evolution/proposals/{pid}/classify").json()
    assert cls["classified"] and cls["change_class"] == "P4"

    assessment = client.post(f"/api/v1/evolution/proposals/{pid}/analyze").json()
    assert assessment["proposal_id"] == pid
    assert "risk" in assessment and "blast_radius" in assessment
    assert client.get(f"/api/v1/evolution/proposals/{pid}").json()["status"] == \
        "DECISION_PENDING"

    # quorum P4 incomplet → 403
    r = client.post(f"/api/v1/evolution/proposals/{pid}/approve",
                    params={"actor": "committee", "reason": "go"},
                    json=[{"role": "maintainer", "actor": "alice"}])
    assert r.status_code == 403

    # quorum complet → APPROVED
    r = client.post(f"/api/v1/evolution/proposals/{pid}/approve",
                    params={"actor": "committee", "reason": "go"},
                    json=[{"role": "maintainer", "actor": "alice"},
                          {"role": "security_officer", "actor": "bob"}])
    assert r.status_code == 200 and r.json()["approved"] is True
    assert client.get(f"/api/v1/evolution/proposals/{pid}").json()["status"] == "APPROVED"


def test_rejet_motivé(client):
    payload = {"title": "Proposition rejetée explicitement", "type": "FEATURE",
               "requested_by": "dev", "affected_domains": ["lab"]}
    pid = client.post("/api/v1/evolution/proposals", json=payload).json()["id"]
    client.post(f"/api/v1/evolution/proposals/{pid}/validate")
    client.post(f"/api/v1/evolution/proposals/{pid}/classify")
    client.post(f"/api/v1/evolution/proposals/{pid}/analyze")  # → DECISION_PENDING
    r = client.post(f"/api/v1/evolution/proposals/{pid}/reject",
                    params={"actor": "committee", "reason": "hors usage prévu"})
    assert r.json()["rejected"] is True
    assert client.get(f"/api/v1/evolution/proposals/{pid}").json()["status"] == "REJECTED"


def test_events_flux(client):
    r = client.get("/api/v1/evolution/events")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
