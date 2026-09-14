"""Tracing léger — contextvars, corrélation request_id/case_id."""
from __future__ import annotations

import contextvars

request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="")
case_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("case_id", default="")


def set_request_id(rid: str) -> None:
    request_id_var.set(rid)


def set_case_id(cid: str) -> None:
    case_id_var.set(cid)


def current() -> dict:
    return {"request_id": request_id_var.get(), "case_id": case_id_var.get()}
