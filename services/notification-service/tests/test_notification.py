"""Tests notification-service."""
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[3]
for p in ("packages/medisuite-core", str(ROOT / "services" / "notification-service" / "src")):
    sys.path.insert(0, p)
from fastapi.testclient import TestClient
from main import app
client = TestClient(app)


def test_channels():
    assert {"email", "sms", "push", "in_app"} <= set(
        client.get("/api/v1/channels").json()["canaux"])


def test_send_et_inbox():
    r = client.post("/api/v1/send", json={
        "canal": "sms", "destinataire": "+225 07 00 00 00 00",
        "sujet": "RDV", "corps": "Rappel RDV cardiologie demain 9h"})
    assert r.status_code == 201
    inbox = client.get("/api/v1/inbox", params={"canal": "sms"}).json()
    assert any(m["sujet"] == "RDV" for m in inbox)
    mid = r.json()["id"]
    assert client.post(f"/api/v1/inbox/{mid}/read").json()["lu"] is True


def test_alerte_critique_multi_canaux():
    r = client.post("/api/v1/alerte-clinique", json={
        "destinataire": "Dr Koné", "sujet": "Valeur critique K+ 7.4",
        "corps": "Potassium critique patient MS-2026-00001"})
    canaux = [d["canal"] for d in r.json()["diffuse"]]
    assert canaux == ["in_app", "sms"]


def test_canal_inconnu():
    r = client.post("/api/v1/send", json={
        "canal": "pigeon", "destinataire": "x", "corps": "y"})
    assert r.status_code == 422
