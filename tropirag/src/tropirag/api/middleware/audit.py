"""Middleware — audit de chaque requête."""
from __future__ import annotations

import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from tropirag.observability.logging import get_logger
from tropirag.observability.metrics import Metrics

log = get_logger("audit")


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        t0 = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - t0) * 1000
        Metrics.instance().observe("tropirag_http_ms", duration_ms, path=request.url.path)
        Metrics.instance().inc("tropirag_http_total", 1.0,
                               status=str(response.status_code))
        if request.url.path != "/health":
            log.info("%s %s -> %s (%.1f ms)",
                     request.method, request.url.path, response.status_code, duration_ms)
        return response
