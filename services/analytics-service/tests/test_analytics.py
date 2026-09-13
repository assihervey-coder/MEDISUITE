"""Tests analytics-service."""
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[3]
for p in ("packages/medisuite-core", str(ROOT / "services" / "analytics-service" / "src")):
    sys.path.insert(0, p)
from fastapi.testclient import TestClient
from main import app
client = TestClient(app)


def test_kpis():
    k = client.get("/api/v1/kpis").json()
    assert "patients" in k and "etudes_imagerie" in k
    assert k["patients"] is None or k["patients"] >= 0


def test_activite():
    a = client.get("/api/v1/activite").json()
    assert "par_topic" in a and a["total"] >= 0


def test_epidemiologie_paludisme():
    p = client.get("/api/v1/epidemiologie/paludisme").json()
    assert len(p["semaines"]) == 12 and 0 < p["positivite_pct"] < 100


def test_epidemiologie_vih():
    v = client.get("/api/v1/epidemiologie/vih").json()
    assert v["diagnostiques_pct"] > 50
