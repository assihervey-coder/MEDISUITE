"""Middleware de gouvernance — tampon `investigation` sur les sorties CDS.

Défense en profondeur : chaque réponse décisionnelle (cf. DECISION_PATHS)
porte l'interdiction réglementaire en DOUBLE canal :
    - en-têtes  X-Governance-Status / X-Governance-Lock / X-Governance-Decision
      (visibles même quand le consommateur n'analyse pas le corps) ;
    - corps JSON `governance: {…}` injecté en fin de document (lisible par
      tout client, conservé en journal d'audit).

Le tampon s'applique AUSSI en mode `certified` (statut ≠ investigation) —
la traçabilité réglementaire d'une sortie CDS ne se retire jamais.
Seuls les corps JSON applicatifs (application/json, objet JSON racine)
sont modifiés ; les erreurs, fichiers, flux et dashboard restent intacts.
"""
from __future__ import annotations

import json
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from tropirag.governance.investigation import (
    DECISION_PATHS,
    LOCK_LABEL,
    is_decisional_use_allowed,
    stamp,
)

#: Chemins NON décisionnels (dashboard, santé, docs, métriques) — jamais
#: tamponnés même s'ils partagent un préfixe.
_EXCLUDED_PREFIXES: tuple[str, ...] = (
    "/api/docs",
    "/api/openapi.json",
    "/metrics",
    "/health",
    "/api/v1/health",
    "/static",
    "/assets",
    "/favicon",
    "/web",
    "/mobile",
)


def is_decision_path(path: str) -> bool:
    """Chemin décisionnel ? Sorties CDS uniquement (cases/evidence/surveillance)."""
    if any(path == p or path.startswith(p) for p in _EXCLUDED_PREFIXES):
        return False
    return any(path.startswith(p) for p in DECISION_PATHS)


class GovernanceMiddleware(BaseHTTPMiddleware):
    """Tamponne les sorties d'investigation — jamais silencieux."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        if not is_decision_path(request.url.path):
            return response
        allowed = is_decisional_use_allowed()
        response.headers["X-Governance-Status"] = "certified" if allowed else "investigation"
        response.headers["X-Governance-Lock"] = LOCK_LABEL
        response.headers["X-Governance-Decision"] = "autorisée" if allowed else "interdite"

        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type or response.status_code >= 400:
            return response

        # Bufferiser le corps streamé (BaseHTTPMiddleware) puis réinjecter.
        chunks: list[bytes] = []
        async for chunk in response.body_iterator:  # type: ignore[attr-defined]
            chunks.append(chunk if isinstance(chunk, bytes) else str(chunk).encode())
        raw = b"".join(chunks)
        # Le Content-Length d'origine ne correspond plus après réécriture —
        # Response le recalcule s'il est absent (sinon IncompleteRead côté client).
        headers = dict(response.headers)
        headers.pop("content-length", None)
        try:
            body: Any = json.loads(raw or b"{}")
        except Exception:  # pragma: no cover — corps non JSON improbable ici
            return Response(
                content=raw, status_code=response.status_code,
                headers=headers, media_type="application/json",
            )
        if not isinstance(body, dict) or "governance" in body:
            return Response(
                content=raw, status_code=response.status_code,
                headers=headers, media_type="application/json",
            )
        body["governance"] = stamp()
        return Response(
            content=json.dumps(body, ensure_ascii=False, default=str).encode("utf-8"),
            status_code=response.status_code,
            headers=headers,
            media_type="application/json",
        )
