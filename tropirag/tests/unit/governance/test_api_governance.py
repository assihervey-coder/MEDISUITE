"""API gouvernance — tampon middleware + garde 451 (TestClient)."""
from __future__ import annotations

import importlib

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setenv("TROPIRAG_API_KEY", "")  # auth désactivée pour les tests
    monkeypatch.delenv("MEDISUITE_GOVERNANCE_MODE", raising=False)
    monkeypatch.delenv("MEDISUITE_GOVERNANCE_CE_ACK", raising=False)
    import tropirag.core.config as cfg

    importlib.reload(cfg)
    from tropirag.api import app as app_mod

    importlib.reload(app_mod)
    return TestClient(app_mod.app)


class TestTamponSorties:
    def test_analyze_tamponnee(self, client, days_ago):
        """POST /clinical/analyze — la sortie CDS porte le bloc governance."""
        r = client.post("/api/v1/clinical/analyze", json={
            "patient": {"age_years": 34, "sex": "male"},
            "free_text": "fièvre 39,6 depuis 4 jours, frissons",
            "travel": {"segments": [{"country": "CI", "rural_stay": True,
                                      "departure": days_ago(9)}]},
            "vitals": {"temperature_c": 39.6},
        })
        assert r.status_code == 200
        body = r.json()
        g = body["governance"]
        assert g["statut"] == "investigation"
        assert g["decision_clinique"] == "interdite"
        assert g["verrou"] == "M+18"
        assert r.headers["X-Governance-Status"] == "investigation"
        assert r.headers["X-Governance-Decision"] == "interdite"

    def test_cases_tamponne(self, client, days_ago):
        r = client.post("/api/v1/cases", json={
            "patient": {"age_years": 30, "sex": "female"},
            "free_text": "fièvre et céphalées",
            "travel": {"segments": [{"country": "CI", "rural_stay": True,
                                      "departure": days_ago(5)}]},
        })
        assert r.status_code == 200
        assert r.json()["governance"]["statut"] == "investigation"

    def test_sante_non_tamponnee(self, client):
        """Health/dashboard ne matérialisent pas de sortie clinique — pas de
        tampon (économe et sans bruit réglementaire hors décision)."""
        r = client.get("/api/v1/health")
        assert r.status_code == 200
        assert "governance" not in r.json()
        assert "X-Governance-Status" not in r.headers

    def test_surveillance_tamponnee(self, client):
        r = client.get("/api/v1/surveillance/map")
        assert r.status_code == 200
        assert r.json()["governance"]["statut"] == "investigation"


class TestGardeDecision:
    def test_finalize_451(self, client):
        """La matérialisation d'une décision clinique est bloquée : 451."""
        r = client.post("/api/v1/decision/finalize", json={
            "case_id": "CASE-TEST",
            "decision": "hospitalisation",
            "destinataire": "prescription-service",
        })
        assert r.status_code == 451
        detail = r.json()["detail"]
        assert detail["error"] == "clinical_decision_locked"
        assert detail["case_id"] == "CASE-TEST"
        assert detail["governance"]["decision_clinique"] == "interdite"
        assert r.headers["X-Governance-Decision"] == "interdite"

    def test_etat_public_governance(self, client):
        r = client.get("/api/v1/governance")
        assert r.status_code == 200
        body = r.json()
        assert body["statut"] == "investigation"
        assert body["finalize"]["disponible"] is False
        assert body["finalize"]["refus_code"] == 451
        cal = body["calendrier"]
        assert cal["pose"] is False
        assert cal["phase_active"] == "R6"
        assert cal["verrou_m18"] == "2026-12-01"  # M0 défaut 2025-06-01
