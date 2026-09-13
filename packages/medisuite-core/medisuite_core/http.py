"""Fabrique d'applications FastAPI : un contrat unique pour les 38 services.

Chaque service obtient gratuitement :
- /health  (liveness) et /ready (readiness avec vérification BDD)
- middleware X-Request-ID + header X-Service-Name
- gestion d'erreurs homogène (dict {"error", "detail"})
- CORS et documentation OpenAPI automatique
"""
from __future__ import annotations

import time
import uuid
from typing import Callable

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

_STARTED_AT = time.time()


def create_service_app(
    name: str,
    title: str,
    description: str,
    version: str = "0.1.0",
    module_label: str = "",
) -> FastAPI:
    """Construit une app FastAPI conforme au contrat de service MEDISUITE."""
    app = FastAPI(
        title=f"MEDISUITE · {title}",
        description=description,
        version=version,
        docs_url="/docs",
        openapi_url="/openapi.json",
    )
    app.state.service_name = name
    app.state.module_label = module_label or title

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # restreint par l'ingress en production
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def _request_context(request: Request, call_next: Callable):
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:16]
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Service-Name"] = name
        response.headers["X-Elapsed-Ms"] = str(elapsed_ms)
        return response

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"error": "internal_error", "detail": str(exc),
                     "service": name},
        )

    @app.get("/health", tags=["opérationnel"])
    def health():
        return {"status": "ok", "service": name, "version": version,
                "module": app.state.module_label,
                "uptime_s": round(time.time() - _STARTED_AT, 1)}

    @app.get("/ready", tags=["opérationnel"])
    def ready():
        db_ok = True
        try:  # vérification légère : session utilisable
            from .db import engine_for
            engine = engine_for(name)
            with engine.connect() as conn:
                conn.exec_driver_sql("SELECT 1")
        except Exception:
            db_ok = False
        return {"status": "ready" if db_ok else "degraded", "database": db_ok}

    return app
