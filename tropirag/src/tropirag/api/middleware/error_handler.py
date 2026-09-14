"""Middleware — gestion d'erreurs unifiée (jamais de stack trace en clair)."""
from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from tropirag.core.errors import TropiRAGError
from tropirag.observability.logging import get_logger

log = get_logger("errors")


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except TropiRAGError as e:
            log.error("erreur métier: %s [%s] %s", e.code, e.message, e.details)
            return JSONResponse(
                {"error": {"code": e.code, "message": e.message, "details": e.details}},
                status_code=422)
        except Exception as e:  # noqa: BLE001
            log.error("erreur interne: %s", e, exc_info=True)
            return JSONResponse(
                {"error": {"code": "E_INTERNAL", "message": "Erreur interne"}},
                status_code=500)
