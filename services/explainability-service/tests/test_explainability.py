"""Tests explainability-service."""
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[3]
for p in ("packages/medisuite-core", str(ROOT / "services" / "explainability-service" / "src")):
    sys.path.insert(0, p)
from fastapi.testclient import TestClient
from main import app
client = TestClient(app)


def test_importance_normalisee():
    r = client.post("/api/v1/modality-importance", json={
        "attention": {"imaging": 3.0, "tabulaire": 1.0, "texte": 1.0}}).json()
    assert abs(sum(r["importance_pct"].values()) - 100) < 0.5
    assert r["modalite_dominante"] == "imaging"


def test_poids_nuls_rejetes():
    r = client.post("/api/v1/modality-importance", json={
        "attention": {"a": 0.0, "b": 0.0}})
    assert r.status_code == 422


def test_gradcam_centroide():
    r = client.post("/api/v1/gradcam-lite", json={
        "grid": [[0, 0, 0], [0, 5, 1], [0, 1, 0]]}).json()
    assert r["heatmap"][1][1] == 1.0
    assert 0.3 < r["centroid_saliency"]["y"] < 1.8
