"""Tests audit-service : chaîne de hachage, vérification, détection d'altération."""
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[3]
for p in ("packages/medisuite-core", str(ROOT / "services" / "audit-service" / "src")):
    sys.path.insert(0, p)
from fastapi.testclient import TestClient
from main import app, _chain, _loaded
client = TestClient(app)


def _reset():
    global _loaded
    _chain.events.clear()
    _loaded = False


def test_append_et_verify():
    _reset()
    for i in range(6):
        r = client.post("/api/v1/events", json={
            "actor": f"user{i}", "role": "medecin", "action": "patient.read",
            "resource": f"patient:{i}", "detail": {"ip": "10.0.0.1"}})
        assert r.status_code == 201
    v = client.post("/api/v1/chain/verify").json()
    assert v["integre"] is True and v["nb_events"] == 6


def test_tail():
    _reset()
    for i in range(3):
        client.post("/api/v1/events", json={
            "actor": "a", "action": "lab.order", "resource": f"o{i}"})
    tail = client.get("/api/v1/tail", params={"n": 2}).json()
    assert len(tail) == 2 and tail[-1]["action"] == "lab.order"


def test_detection_alteration():
    _reset()
    for i in range(5):
        client.post("/api/v1/events", json={
            "actor": "a", "action": "ai.infer", "resource": f"case:{i}"})
    assert client.post("/api/v1/chain/verify").json()["integre"] is True
    # falsification rétroactive du 3e événement
    client.post("/api/v1/chain/tamper-demo/2")
    v = client.post("/api/v1/chain/verify").json()
    assert v["integre"] is False and v["premiere_alteration"] == 2


def test_stats():
    _reset()
    client.post("/api/v1/events", json={"actor": "a", "action": "x.y", "resource": "r"})
    s = client.get("/api/v1/stats").json()
    assert s["par_action"].get("x.y") == 1
