"""Middleware — ID de requête propagé partout."""
from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from tropirag.core.identifiers import new_request_id
from tropirag.observability.tracing import set_request_id


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rid = request.headers.get("X-Request-ID") or new_request_id()
        set_request_id(rid)
        request.state.request_id = rid
        response = await call_next(request)
        response.headers["X-Request-ID"] = rid
        return response
