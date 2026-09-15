"""API TropiRAG — FastAPI, auth API-key, audit, dashboard intégré.

Routes :
    GET  /                       dashboard web
    GET  /mobile                interface mobile terrain (PWA offline-first)
    GET  /map                   carte des éclosions (surveillance par district)
    GET  /health                 santé système
    GET  /api/v1/models          registre du mesh
    POST /api/v1/cases/analyze   analyse clinique complète (pipeline)
    GET  /api/v1/cases           cas récents
    GET  /api/v1/cases/{id}      cas + analyse
    POST /api/v1/drugs/check     vérification médicamenteuse
    POST /api/v1/evidence/query  interrogation RAG
    GET  /api/v1/audit           événements d'audit récents
    GET  /api/v1/surveillance/map    clusters d'éclosion par district CI
    GET  /metrics                format Prometheus
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from tropirag.core.config import get_config
from tropirag.core.enums import Severity, Urgency
from tropirag.core.errors import TropiRAGError
from tropirag.core.identifiers import new_request_id
from tropirag.observability.logging import get_logger, setup_logging
from tropirag.observability.tracing import set_request_id

setup_logging()
log = get_logger("api")


def create_app() -> FastAPI:
    cfg = get_config()
    app = FastAPI(
        title="TropiRAG",
        description="Compagnon clinique de terrain — fièvre + voyage (Afrique de l'Ouest). "
                    "IA encadrée, autorité clinique déterministe.",
        version=cfg.app.version,
        docs_url="/api/docs",
    )
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"],
                       allow_headers=["*"])

    # --- middlewares -----------------------------------------------------
    from tropirag.api.middleware.audit import AuditMiddleware
    from tropirag.api.middleware.authentication import AuthMiddleware
    from tropirag.api.middleware.error_handler import ErrorHandlerMiddleware
    from tropirag.api.middleware.request_id import RequestIdMiddleware

    if cfg.security.require_api_key:
        app.add_middleware(AuthMiddleware, api_key=cfg.security.api_key)
    app.add_middleware(AuditMiddleware)
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(ErrorHandlerMiddleware)
    # V1.4 bis — tampon « investigation » sur les sorties CDS (headers + corps)
    # + garde 451 : toute matérialisation de décision clinique est interdite
    # tant que l'investigation MEDISUITE-CI-01 est ouverte (verrou M+18).
    from tropirag.api.middleware.governance import GovernanceMiddleware

    app.add_middleware(GovernanceMiddleware)

    # --- routes ----------------------------------------------------------
    from tropirag.api.routes import (
        audit as audit_routes,
        cases as case_routes,
        clinical as clinical_routes,
        evidence as evidence_routes,
        export as export_routes,
        health as health_routes,
        inference as inference_routes,
        models as model_routes,
        retrieval as retrieval_routes,
        surveillance as surveillance_routes,
        symptoms as symptom_routes,
        travel as travel_routes,
    )

    app.include_router(health_routes.router, prefix="/api/v1", tags=["health"])
    app.include_router(model_routes.router, prefix="/api/v1", tags=["models"])
    app.include_router(case_routes.router, prefix="/api/v1", tags=["cases"])
    app.include_router(clinical_routes.router, prefix="/api/v1", tags=["clinical"])
    app.include_router(symptom_routes.router, prefix="/api/v1", tags=["symptoms"])
    app.include_router(travel_routes.router, prefix="/api/v1", tags=["travel"])
    app.include_router(evidence_routes.router, prefix="/api/v1", tags=["evidence"])
    app.include_router(retrieval_routes.router, prefix="/api/v1", tags=["retrieval"])
    app.include_router(inference_routes.router, prefix="/api/v1", tags=["inference"])
    app.include_router(audit_routes.router, prefix="/api/v1", tags=["audit"])
    # V1.2 — export DHIS2 pour le MSP-CI
    app.include_router(export_routes.router, prefix="/api/v1", tags=["export"])
    # V1.3 — surveillance et carte des éclosions
    app.include_router(surveillance_routes.router, prefix="/api/v1", tags=["surveillance"])
    # V1.4 bis — gouvernance : état du verrou M+18 + garde de décision 451
    from tropirag.api.routes import governance as governance_routes

    app.include_router(governance_routes.router, prefix="/api/v1", tags=["governance"])

    @app.get("/metrics")
    async def metrics_endpoint() -> Response_Metrics:
        from fastapi.responses import PlainTextResponse

        from tropirag.observability.metrics import prometheus_export

        return PlainTextResponse(prometheus_export(), media_type="text/plain; version=0.0.4")

    # --- interface mobile terrain (PWA offline-first, V1.1) ----------------------
    mobile_dir = Path(__file__).resolve().parents[3] / "frontend" / "mobile"
    if mobile_dir.exists():
        app.mount("/mobile", StaticFiles(directory=str(mobile_dir), html=True), name="mobile")

    # --- dashboard statique -------------------------------------------------
    web_dir = Path(__file__).resolve().parent / "web"
    if web_dir.exists():
        app.mount("/", StaticFiles(directory=str(web_dir), html=True), name="dashboard")

    # --- cron hebdomadaire DHIS2 (MSP-CI) — off par défaut -------------------
    @app.on_event("startup")
    async def _start_dhis2_cron() -> None:
        import os

        from tropirag.integrations.dhis2.scheduler import get_scheduler

        if (os.environ.get("TROPIRAG_DHIS2_AUTO", "off") or "off").lower() != "off":
            get_scheduler().start()

    @app.on_event("shutdown")
    async def _stop_dhis2_cron() -> None:
        from tropirag.integrations.dhis2.scheduler import get_scheduler

        await get_scheduler().stop()

    return app


from fastapi.responses import Response as Response_Metrics  # noqa: E402

app = create_app()
