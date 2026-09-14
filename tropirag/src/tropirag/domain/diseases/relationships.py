"""Relations cliniques entre entités maladie."""
from __future__ import annotations

from tropirag.domain.diseases.taxonomy import SEVERE_FORM


def severe_form_of(code: str) -> str | None:
    return SEVERE_FORM.get(code)


def is_severe_form(code: str) -> bool:
    return code in SEVERE_FORM.values()
