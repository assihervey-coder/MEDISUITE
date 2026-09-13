"""Tests multimodal-gateway : registre, validation, disponibilité moteur."""
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[3]
for p in ("packages/medisuite-core", str(ROOT / "services" / "multimodal-gateway" / "src")):
    sys.path.insert(0, p)
from fastapi.testclient import TestClient
from main import app
client = TestClient(app)


def test_modalites_registre():
    m = client.get("/api/v1/modalities").json()["modalites"]
    assert set(m) == {"imaging_2d", "imaging_3d", "signal_1d", "tabulaire",
                      "texte", "genomique", "waveform"}


def test_inference_sans_modalites():
    r = client.post("/api/v1/inference", json={"patient_id": "p"})
    assert r.status_code == 422


def test_inference_moteur_present_ou_503():
    r = client.post("/api/v1/inference", json={
        "patient_id": "p",
        "modalities": {"tabulaire": {"features": [0.1, 0.2, 0.3]}}})
    # 200 si le moteur NumPy est livré (phase IA), 503 sinon
    assert r.status_code in (200, 503)
