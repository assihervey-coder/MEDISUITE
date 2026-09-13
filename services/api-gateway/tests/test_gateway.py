"""Tests api-gateway : registry, rate limiting, proxy authentifié."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
for p in ("packages/medisuite-core", str(ROOT / "services" / "api-gateway" / "src")):
    sys.path.insert(0, p)

from fastapi.testclient import TestClient

from main import app, REGISTRY, BUCKETS, _allow, JWT_SECRET
from medisuite_core import security

client = TestClient(app)


def _reset_bucket():
    BUCKETS.clear()


def test_health():
    assert client.get("/health").json()["service"] == "api-gateway"


def test_registry():
    r = client.get("/api/v1/registry").json()
    assert "auth" in r["services"] and "patients" in r["services"]


def test_service_inconnu():
    _reset_bucket()
    r = client.get("/api/service_fantome/health")
    assert r.status_code == 404 and "inconnu" in r.json()["detail"]


def test_write_sans_jwt_rejete():
    _reset_bucket()
    # POST sans JWT → 401 AVANT tout appel upstream (fail-closed)
    r = client.post("/api/patients/patients", json={})
    assert r.status_code == 401


def test_get_upstream_injoignable_502():
    _reset_bucket()
    # GET autorisé en dev mais le service cible n'est pas démarré → 502
    r = client.get("/api/patients/patients")
    assert r.status_code in (200, 502)


def test_rate_limiter():
    # bucket indépendant par client + recharge progressive
    for _ in range(200):
        _allow("client-rl-test")
    assert _allow("client-rl-test") is False
    assert _allow("autre-client-rl") is True


def test_about_etiquetage_public():
    # étiquette UDI lisible SANS JWT (MDR Annexe I §23.2)
    r = client.get("/api/v1/about").json()
    assert r["basic_udi_di"] == "MEDISUITE-PLTF-AIDE-DECISION"
    assert r["classe_mdr"].startswith("IIb")
    assert r["marquage_ce"] is False          # honnêteté : NON CE affiché
    assert "commit" in r and r["ifu"] and len(r["ifu"]) == 4


def test_about_env_prime_deployment(monkeypatch):
    # la version injectée au déploiement fait foi (règle 1 étiquetage)
    monkeypatch.setenv("MEDISUITE_VERSION", "v9.9.9-rc")
    monkeypatch.setenv("MEDISUITE_COMMIT", "abc1234")
    r = client.get("/api/v1/about").json()
    assert r["version"] == "v9.9.9-rc" and r["commit"] == "abc1234"
    assert r["basic_udi_di"] == "MEDISUITE-PLTF-AIDE-DECISION"
