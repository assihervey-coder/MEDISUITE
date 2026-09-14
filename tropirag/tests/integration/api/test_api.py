"""Tests d'intégration de l'API."""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setenv("TROPIRAG_API_KEY", "")  # auth désactivée pour les tests
    import importlib

    import tropirag.core.config as cfg
    importlib.reload(cfg)
    from tropirag.api import app as app_mod
    importlib.reload(app_mod)
    return TestClient(app_mod.app)


class TestAPI:
    def test_health(self, client):
        r = client.get("/api/v1/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"
        assert r.json()["components"]["rule_engine"]["rules"] >= 80

    def test_models_registry(self, client):
        r = client.get("/api/v1/models")
        data = r.json()
        assert len(data["models"]) >= 9
        assert data["invariants_violations"] == []

    def test_routing_endpoint(self, client):
        r = client.get("/api/v1/models/route", params={"task": "clinical_reasoning"})
        assert r.status_code == 200
        assert "reason" in r.json()

    def test_analyze_full(self, client, days_ago):
        r = client.post("/api/v1/clinical/analyze", json={
            "patient": {"age_years": 34, "sex": "male"},
            "free_text": "fièvre 39,6 depuis 4 jours, frissons, vomissements, céphalées",
            "travel": {"segments": [{"country": "CI", "rural_stay": True,
                                      "departure": days_ago(9)}]},
            "vitals": {"temperature_c": 39.6},
        })
        assert r.status_code == 200
        data = r.json()
        assert data["differentials"][0]["disease"] == "malaria"
        assert data["citations"]
        assert "professionnels de santé" in data["disclaimer"]

    def test_symptoms_normalize(self, client):
        r = client.post("/api/v1/symptoms/normalize", json={"text": "fièvre et frissons"})
        assert r.status_code == 200
        codes = [s["code"] for s in r.json()["symptoms"]]
        assert "fever" in codes and "chills" in codes

    def test_evidence_query(self, client):
        r = client.post("/api/v1/evidence/query", json={
            "query": "paludisme traitement CTA", "top_k": 3})
        assert r.status_code == 200
        assert r.json()["results"]

    def test_travel_profile(self, client):
        r = client.get("/api/v1/travel/profile/CI")
        assert r.status_code == 200
        assert r.json()["malaria"] == "high"

    def test_drug_check_via_analyze(self, client, days_ago):
        r = client.post("/api/v1/clinical/analyze", json={
            "patient": {"age_years": 30},
            "free_text": "fièvre, arthralgies, céphalées",
            "travel": {"segments": [{"country": "CI", "departure": days_ago(8)}]},
            "medications": [{"name": "ibuprofen"}, {"name": "paracetamol"}],
        })
        data = r.json()
        forbidden = {d["drug"] for d in data["drug_constraints"] if d["forbidden"]}
        assert "ibuprofen" in forbidden

    def test_error_handling(self, client):
        r = client.post("/api/v1/clinical/analyze", json={"symptoms": []})
        assert r.status_code == 200  # cas vide → réponse limites, pas de crash


class TestInferenceNodesRoute:
    """V1.1 — santé du mesh Ollama exposée par l'API."""

    def test_nodes_report_shape(self, client):
        r = client.get("/api/v1/inference/nodes")
        assert r.status_code == 200
        d = r.json()
        assert d["gateway"] == "ollama"
        assert "nodes" in d and "family_routing" in d
        assert d["inference_mode"] in ("deterministic", "ollama", "vllm")
        assert isinstance(d["required_models"], list)
        assert "med42-v2-70b" in d["required_models"]

    def test_nodes_with_env_routing(self, client):
        import os

        old = os.environ.get("TROPIRAG_OLLAMA_NODES")
        os.environ["TROPIRAG_OLLAMA_NODES"] = (
            "speech=http://127.0.0.1:1,text=http://127.0.0.1:2")
        try:
            r = client.get("/api/v1/inference/nodes")
            assert r.status_code == 200
            fr = r.json()["family_routing"]
            assert fr["text"] == "http://127.0.0.1:2"
        finally:
            if old is None:
                os.environ.pop("TROPIRAG_OLLAMA_NODES", None)
            else:
                os.environ["TROPIRAG_OLLAMA_NODES"] = old


class TestMobileInterface:
    """V1.1 — interface mobile servie par l'API."""

    def test_mobile_page_served(self, client):
        r = client.get("/mobile/")
        assert r.status_code == 200
        assert "TropiRAG Terrain" in r.text
        assert "manifest.json" in r.text

    def test_mobile_assets(self, client):
        for path in ("/mobile/app.js", "/mobile/sw.js",
                     "/mobile/manifest.json", "/mobile/icon.svg"):
            r = client.get(path)
            assert r.status_code == 200, path

    def test_mobile_case_roundtrip(self, client, days_ago):
        """Le cas soumis par le mobile (grossesse + terme) est honoré."""
        r = client.post("/api/v1/cases", json={
            "patient": {"age_years": 24, "sex": "female",
                        "pregnant": "pregnant", "gestational_age_weeks": 32},
            "free_text": "fièvre et le bébé bouge moins",
            "travel": {"segments": [{"country": "CI", "departure": days_ago(10)}]},
        })
        assert r.status_code == 200
        d = r.json()
        assert d["urgency"] in ("immediate", "emergency")
        codes = [f["code"] for f in d["red_flags"]]
        assert "fetal_distress_risk" in codes
        forbidden = {x["drug"] for x in d["drug_constraints"] if x["forbidden"]}
        assert "primaquine" in forbidden
