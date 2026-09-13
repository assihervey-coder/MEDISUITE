"""Client serveur HAPI FHIR R4 — interopérabilité santé de niveau national. v0.4.

Connecteur du integration-service (et de tout service) vers un serveur HAPI
FHIR JPA (hapiproject/hapi) déployé en local (compose) ou en cluster (K8s).
REST FHIR R4 (POST/GET), zéro dépendance externe (urllib + json), conforme
à la contrainte « stdlib d'abord » du repo.

Configuration par variables d'environnement :
- MEDISUITE_FHIR_BASE    (défaut http://localhost:8090/fhir)
- MEDISUITE_FHIR_TIMEOUT (défaut 3.0 s)

Dégradation gracieuse : aucune exception ne remonte à l'API pour un serveur
hors ligne — `ping()` retourne False et les endpoints signale
reachable=false (l'exploitation hospitalière ne doit jamais dépendre du
référentiel central pour continuer à soigner en local).

Opérations supportées (FHIR R4, REST) :
- GET  [base]/metadata          → CapabilityStatement (conformité déclarée)
- POST [base]/Patient           → création (201, ETag version faible)
- GET  [base]/Patient/{id}      → lecture unitaire
- GET  [base]/Patient?family=…  → recherche (Bundle searchset)
- POST [base]/                  → transaction/batch (Bundle type transaction)
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request


class FhirError(RuntimeError):
    """Serveur FHIR injoignable ou réponse invalide."""


class HapiClient:
    """Client REST HAPI FHIR R4 minimal et testable (injection d'opener)."""

    def __init__(self, base: str | None = None, timeout: float | None = None,
                 opener=None) -> None:
        self.base = (base or os.environ.get(
            "MEDISUITE_FHIR_BASE", "http://localhost:8090/fhir")).rstrip("/")
        self.timeout = float(timeout if timeout is not None
                             else os.environ.get("MEDISUITE_FHIR_TIMEOUT", 3.0))
        self._opener = opener  # injection pour tests

    # ── couche transport ──────────────────────────────────────────────────────
    def _request(self, method: str, path: str, body: dict | None = None,
                 accept_indexed_params: dict | None = None) -> dict:
        url = self.base + path
        if accept_indexed_params:
            url += "?" + urllib.parse.urlencode(accept_indexed_params)
        req = urllib.request.Request(url, method=method)
        req.add_header("Accept", "application/fhir+json")
        if body is not None:
            req.add_header("Content-Type", "application/fhir+json")
            req.data = json.dumps(body).encode("utf-8")
        urlopen = self._opener or urllib.request.urlopen
        try:
            with urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw.strip() else {}
        except FhirError:
            raise
        except urllib.error.HTTPError as exc:
            raise FhirError(f"HTTP {exc.code} sur {method} {path} : "
                            f"{exc.reason}") from exc
        except Exception as exc:  # URLError, TimeoutError, JSONDecode…
            raise FhirError(f"serveur FHIR injoignable ({self.base}) : "
                            f"{exc}") from exc

    # ── API haut niveau ───────────────────────────────────────────────────────
    def capabilities(self) -> dict:
        """CapabilityStatement du serveur (GET /metadata)."""
        return self._request("GET", "/metadata")

    def ping(self) -> bool:
        """True si le serveur expose une CapabilityStatement R4 — jamais d'exception."""
        try:
            cap = self.capabilities()
            return cap.get("fhirVersion") == "4.0.1"
        except FhirError:
            return False

    def create(self, resource_type: str, resource: dict) -> dict:
        """Création d'une ressource → renvoie id, version et url relative."""
        out = self._request("POST", f"/{resource_type}", body=resource)
        meta = out.get("meta") or {}
        return {"id": out.get("id", ""),
                "version": str(meta.get("versionId", "")),
                "resourceType": resource_type}

    def read(self, resource_type: str, resource_id: str) -> dict:
        """Lecture unitaire GET [base]/{type}/{id}."""
        return self._request("GET", f"/{resource_type}/{resource_id}")

    def search_patients(self, family: str | None = None,
                        identifier: str | None = None,
                        count: int = 20) -> dict:
        """Recherche Patient → Bundle searchset (family, identifier, _count)."""
        params: dict[str, int | str] = {"_count": int(count)}
        if family:
            params["family"] = family
        if identifier:
            params["identifier"] = identifier
        return self._request("GET", "/Patient", accept_indexed_params=params)

    def transaction(self, bundle: dict) -> dict:
        """Transaction/batch FHIR : POST [base]/ d'un Bundle type transaction."""
        if bundle.get("resourceType") != "Bundle":
            raise FhirError("transaction : payload doit être un Bundle")
        return self._request("POST", "/", body=bundle)
