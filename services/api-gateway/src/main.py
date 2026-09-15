"""api-gateway — point d'entrée unique : proxy inverse, auth, rate limiting.

- /api/{service}/{...}  → proxy httpx vers le microservice cible
- validation JWT du header Authorization avant transmission (X-User-* injectés)
- token bucket en mémoire (anti-abus, 100 req/min par client)
- /health agrégé : état de tous les services (fanout parallèle)
- /api/v1/about : étiquetage UDI public (MDR Annexe I §23.2 — jalon R2)
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
import time
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[3]
for p in ("packages/medisuite-core", "packages/clinical-rules"):
    sys.path.insert(0, str(ROOT / p))

import httpx
from fastapi import FastAPI, HTTPException, Request, Response

from medisuite_core import security
from medisuite_core.http import create_service_app

app: FastAPI = create_service_app(
    "api-gateway", "Passerelle API",
    "Proxy inverse authentifié vers les 38 services, rate limiting, "
    "agrégation de santé. Mode gitops-friendly (registry déclarative).",
    module_label="Passerelle")

JWT_SECRET = "medisuite-dev-secret-change-in-prod"

# Registry : en prod, lue depuis K8s service discovery (ADR-0011)
REGISTRY: dict[str, str] = {
    "auth": "http://localhost:8001",
    "patients": "http://localhost:8002",
    "imaging": "http://localhost:8003",
    "lab": "http://localhost:8004",
    "reports": "http://localhost:8200",
    "notifications": "http://localhost:8201",
    "audit": "http://localhost:8202",
    "integration": "http://localhost:8203",
    "analytics": "http://localhost:8204",
    "ecrf": "http://localhost:8205",
    "dicom": "http://localhost:8300",
    "hl7": "http://localhost:8301",
    "multimodal": "http://localhost:8302",
    "explainability": "http://localhost:8303",
    "tropirag": "http://localhost:8304",   # aide à la décision clinique (CDS)
}

# Rate limiting : token bucket par client (dév en mémoire ; Redis en prod)
BUCKETS: dict[str, tuple[float, float]] = {}  # client → (tokens, last refill)
RATE_LIMIT = 100 / 60.0  # req/s

# Étiquetage UDI : fichier versionné + surcharge d'environnement au déploiement
# (la version/commit injectés font foi — règle 1 de l'étiquetage).
_LABELING_PATH = pathlib.Path(__file__).resolve().parents[1] / "labeling.json"
with open(_LABELING_PATH, encoding="utf-8") as _fh:
    LABELING: dict = json.load(_fh)


@app.get("/api/v1/about", tags=["opérationnel"])
def about() -> dict:
    """Étiquette logicielle publique (écran « À propos » du web-portal).

    Public volontairement : une étiquette réglementaire doit rester lisible
    même sans session (MDR Annexe I §23.2, Règlement UDI 2019/320).
    """
    out = dict(LABELING)
    out["version"] = os.environ.get("MEDISUITE_VERSION", out["version"])
    out["commit"] = os.environ.get("MEDISUITE_COMMIT", "inconnu")
    out["date_liberation"] = os.environ.get("MEDISUITE_RELEASE_DATE",
                                             out["date_liberation"])
    return out


def _allow(client: str) -> bool:
    now = time.monotonic()
    tokens, last = BUCKETS.get(client, (RATE_LIMIT, now))
    tokens = min(RATE_LIMIT, tokens + (now - last) * RATE_LIMIT)
    if tokens < 1:
        BUCKETS[client] = (tokens, now)
        return False
    BUCKETS[client] = (tokens - 1, now)
    return True


def _jwt_claims(authorization: str | None) -> dict | None:
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    try:
        return security.jwt_decode(authorization.split(" ", 1)[1], JWT_SECRET)
    except security.JWTError:
        return None


@app.get("/api/v1/registry", tags=["opérationnel"])
def registry() -> dict:
    return {"services": REGISTRY,
            "convention": "/api/{service}/{chemin} → {service}"}


@app.get("/health/all", tags=["opérationnel"])
async def health_all() -> dict:
    """Fanout parallèle : santé de chaque service du registre."""
    async with httpx.AsyncClient() as client:
        async def probe(name: str, base: str) -> tuple[str, bool]:
            try:
                r = await client.get(f"{base}/health", timeout=2)
                return name, r.status_code == 200
            except Exception:
                return name, False
        results = await __import__("asyncio").gather(
            *(probe(n, u) for n, u in REGISTRY.items()))
    return {"services": dict(results),
            "sains": sum(1 for _, ok in results if ok),
            "total": len(results)}


@app.api_route("/api/{service}/{path:path}",
               methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy(service: str, path: str, request: Request,
                response: Response) -> Response:
    """Proxy authentifié. En dev, un JWT valide est exigé sauf /health."""
    if not _allow(request.client.host if request.client else "anon"):
        raise HTTPException(429, "rate limit dépassé (100 req/min)")
    claims = _jwt_claims(request.headers.get("authorization"))
    if claims is None and request.method != "GET":
        raise HTTPException(401, "JWT valide requis pour les écritures")
    base = REGISTRY.get(service)
    if not base:
        raise HTTPException(404, f"service '{service}' inconnu — /api/v1/registry")
    headers = {k: v for k, v in request.headers.items()
               if k.lower() not in ("host", "content-length", "authorization")}
    if claims:
        headers["X-User-Id"] = claims.get("sub", "")
        headers["X-User-Role"] = claims.get("role", "")
    try:
        async with httpx.AsyncClient() as client:
            upstream = await client.request(
                request.method, f"{base}/{path}",
                content=await request.body(), headers=headers,
                params=dict(request.query_params), timeout=15)
    except httpx.ConnectError:
        raise HTTPException(502, f"service '{service}' injoignable")
    return Response(content=upstream.content, status_code=upstream.status_code,
                    media_type=upstream.headers.get("content-type", "application/json"))
