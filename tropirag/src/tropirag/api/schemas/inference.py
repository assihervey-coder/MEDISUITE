"""Schémas API d'inférence."""
from __future__ import annotations

from pydantic import BaseModel


class DictationIn(BaseModel):
    audio_b64: str
    language: str = "fr"


class ImageIn(BaseModel):
    image_b64: str
    clinical_context: str = ""
    language: str = "fr"
