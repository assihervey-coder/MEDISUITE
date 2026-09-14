"""Modèles d'export DHIS2 — dataValueSets (JSON), CSV, ADX 2.0 (XML)."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass(slots=True)
class DataValue:
    """Une valeur agrégée — l'atome de tout export DHIS2."""

    data_element: str        # UID de l'élément de données
    org_unit: str            # UID de l'organisation
    period: str              # ex. 2026W37 (hebdomadaire ISO)
    value: str               # valeur stringifiée (DHIS2 attend du texte)
    category_option_combo: str = "default"
    stored_by: str = "tropirag"
    created: str = field(default_factory=_now_iso)

    def to_json(self) -> dict:
        return {
            "dataElement": self.data_element,
            "orgUnit": self.org_unit,
            "period": self.period,
            "value": self.value,
            "categoryOptionCombo": self.category_option_combo,
            "storedBy": self.stored_by,
            "created": self.created,
        }


@dataclass(slots=True)
class DataValueSet:
    """Jeu de valeurs prêt pour l'API DHIS2 (POST /api/dataValueSets)."""

    data_values: list[DataValue] = field(default_factory=list)
    org_unit: str = ""          # pour ADX (groupe)
    period: str = ""            # pour ADX (groupe)
    exported_at: str = field(default_factory=_now_iso)

    def to_json_payload(self) -> dict:
        return {
            "dataValues": [dv.to_json() for dv in self.data_values],
        }

    def to_csv(self) -> str:
        lines = ["dataelement,orgunit,period,value,categoryoptioncombo"]
        for dv in self.data_values:
            lines.append(
                f"{dv.data_element},{dv.org_unit},{dv.period},{dv.value},{dv.category_option_combo}")
        return "\n".join(lines) + "\n"

    def to_adx(self) -> str:
        """ADX 2.0 (IHE urn:ihe:iti:adx:2015) — interopérabilité sémantique."""
        rows = "\n".join(
            f'      <adx:dataValue dataElement="{dv.data_element}" value="{dv.value}"/>'
            for dv in self.data_values)
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<adx:dataValueSet xmlns:adx="urn:ihe:iti:adx:2015" '
            f'exportedTimestamp="{self.exported_at}">\n'
            f'  <adx:group orgUnit="{self.org_unit}" period="{self.period}">\n'
            f'{rows}\n'
            '  </adx:group>\n'
            '</adx:dataValueSet>\n')

    def __len__(self) -> int:
        return len(self.data_values)


@dataclass(slots=True)
class ExportResult:
    """Compte-rendu d'un export (auditabilité locale)."""

    period: str
    org_unit: str
    counts: dict = field(default_factory=dict)
    data_values: list[DataValue] = field(default_factory=list)
    enqueued: bool = False
    pushed: bool = False
    notes: list[str] = field(default_factory=list)
