"""Tests du contrat de service : /health expose version + commit (UDI §2.1).

L'étiquetage (ifu/etiquetage-udi.md, règle 1) impose que « toute installation
doive pouvoir rendre compte de son hash de commit (/health expose version +
commit) ». Ces tests verrouillent cette promesse pour les 38 services.
"""

import os

from fastapi.testclient import TestClient

from medisuite_core.http import create_service_app


def _client(monkeypatch, **env):
    for k in ("MEDISUITE_VERSION", "MEDISUITE_COMMIT"):
        monkeypatch.delenv(k, raising=False)
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    app = create_service_app("svc-test", "Test", "Service de test")
    return TestClient(app)


def test_health_defaut(monkeypatch):
    r = _client(monkeypatch).get("/health").json()
    assert r["service"] == "svc-test" and r["status"] == "ok"
    assert r["version"] == "0.1.0"          # défaut du paramètre
    assert r["commit"] == "inconnu"          # jamais mentir : explicite


def test_health_version_commit_injectes(monkeypatch):
    r = _client(monkeypatch, MEDISUITE_VERSION="v0.6.0",
                MEDISUITE_COMMIT="8d3eb7e").get("/health").json()
    assert r["version"] == "v0.6.0" and r["commit"] == "8d3eb7e"


def test_health_version_env_prime_parametre(monkeypatch):
    # l'env prime, mais au DÉMARRAGE (lecture unique à la création de l'app)
    r = _client(monkeypatch, MEDISUITE_VERSION="v9.9.9").get("/health").json()
    assert r["version"] == "v9.9.9"
