"""Résultats de tests diagnostiques."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class TestResult:
    test_code: str
    value: str | None = None          # 'positive', 'negative', '3+', numérique...
    numeric: float | None = None
    unit: str | None = None
    normal_range: str | None = None
    performed_date: str | None = None
    raw: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, d: dict) -> "TestResult":
        return cls(
            test_code=str(d.get("test", d.get("test_code", ""))),
            value=d.get("value"),
            numeric=d.get("numeric"),
            unit=d.get("unit"),
            normal_range=d.get("normal_range"),
            performed_date=d.get("performed_date"),
            raw=dict(d),
        )

    def is_positive(self) -> bool:
        return str(self.value).lower() in ("positive", "positif", "pos", "1", "yes", "oui", "reactive", "detected", "present")

    def is_negative(self) -> bool:
        return str(self.value).lower() in ("negative", "negatif", "neg", "0", "no", "non", "not detected", "absent")

    def is_below(self, threshold: float) -> bool | None:
        return self.numeric is not None and self.numeric < threshold


def parse_lab_results(entries: list[dict] | None) -> list[TestResult]:
    return [_normalize_units(TestResult.from_dict(e))
            for e in (entries or []) if e.get("test") or e.get("test_code")]


# ---------------------------------------------------------------------------
# Normalisation déterministe des unités (V1.2 — paludisme rénal)
# ---------------------------------------------------------------------------

_CREAT_UMOL_PER_MGDL = 88.4  # facteur de conversion µmol/L → mg/dL


def _normalize_units(tr: TestResult) -> TestResult:
    """Harmonise les unités biologiques pour que les seuils DSL (conventions OMS)
    s'appliquent quel que soit le format du laboratoire de terrain.

    Conversions appliquées (déterministes, aucune perte d'information d'origine —
    la valeur brute est conservée dans ``raw``) :

    - créatinine : µmol/L → mg/dL (÷ 88,4) — seuil OMS paludisme sévère : 3 mg/dL
      (≈ 265 µmol/L) ; la Côte d'Ivoire rapporte majoritairement en µmol/L ;
    - kaliémie : mEq/L ≡ mmol/L (identique numériquement, aucune conversion).

    Toute autre unité passe telle quelle : les seuils des règles sont exprimés
    dans les conventions OMS documentées dans chaque fichier YAML.
    """
    if tr.numeric is None or not tr.unit:
        return tr
    unit = str(tr.unit).lower().replace("µ", "u").replace(" ", "")
    if tr.test_code == "creatinine" and "umol" in unit:
        # préserver l'original pour l'audit
        tr.raw.setdefault("original_numeric", tr.numeric)
        tr.raw.setdefault("original_unit", tr.unit)
        tr.numeric = round(tr.numeric / _CREAT_UMOL_PER_MGDL, 2)
        tr.unit = "mg/dL"
    return tr
