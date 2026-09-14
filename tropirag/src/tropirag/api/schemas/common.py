"""Schémas communs."""
from __future__ import annotations

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: dict = Field(default_factory=dict)


class OkResponse(BaseModel):
    ok: bool = True
    message: str = ""
