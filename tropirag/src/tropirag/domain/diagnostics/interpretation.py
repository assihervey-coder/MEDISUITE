"""Interprétation élémentaire des résultats biologiques (déterministe)."""
from __future__ import annotations

from tropirag.core.constants import (
    MODERATE_ANEMIA_HB, SEVERE_ANEMIA_HB, SEVERE_THROMBOCYTOPENIA_PLT,
    THROMBOCYTOPENIA_PLT, CREATININE_ELEVATED_UMOL, LEUKOPENIA_WBC,
)
from tropirag.domain.diagnostics.results import TestResult


def interpret(test: TestResult) -> list[str]:
    """Renvoie les anomalies lisibles d'un résultat."""
    notes: list[str] = []
    if test.test_code == "cbc":
        if test.numeric is not None and test.unit == "g/dL" and "hb" in (test.raw.get("component", "") or "").lower():
            if test.numeric < SEVERE_ANEMIA_HB:
                notes.append(f"Anémie sévère (Hb {test.numeric} g/dL)")
            elif test.numeric < MODERATE_ANEMIA_HB:
                notes.append(f"Anémie (Hb {test.numeric} g/dL)")
        if test.numeric is not None and test.unit in ("/µL", "/ul", "G/L") and "plt" in (test.raw.get("component", "") or "").lower():
            v = test.numeric / 1000 if test.unit == "G/L" and test.numeric > 1000 else test.numeric
            if v < SEVERE_THROMBOCYTOPENIA_PLT:
                notes.append(f"Thrombopénie sévère ({v:.0f}/µL)")
            elif v < THROMBOCYTOPENIA_PLT:
                notes.append(f"Thrombopénie ({v:.0f}/µL)")
    if test.numeric is not None and test.test_code == "creatinine" and test.numeric > CREATININE_ELEVATED_UMOL:
        notes.append(f"Créatinine élevée ({test.numeric} µmol/L)")
    return notes
