"""Mapper DHIS2 — transforme les analyses persistées en indicateurs agrégés.

Chaque indicateur dérive EXCLUSIVEMENT des analyses déterministes persistées
(table ``analyses``) : différentiels, règles matchées, urgence et sévérité.
Aucune IA ne participe au comptage — l'export est auditable ligne à ligne.
"""
from __future__ import annotations

import json
from datetime import date, timedelta

from tropirag.integrations.dhis2.models import DataValue, DataValueSet
from tropirag.integrations.dhis2.settings import Dhis2Config


# ---------------------------------------------------------------------------
# Périodes — hebdomadaire ISO (format DHIS2 : YYYYWww)
# ---------------------------------------------------------------------------

def period_from_date(d: date) -> str:
    """2026-09-12 → 2026W37 (semaine ISO 8601, deux chiffres)."""
    iso = d.isocalendar()
    return f"{iso.year}W{iso.week:02d}"


def period_bounds(period: str) -> tuple[date, date] | None:
    """'2026W37' → (lundi, dimanche) ; None si format invalide."""
    try:
        year, week = int(period[:4]), int(period[5:7])
        monday = date.fromisocalendar(year, week, 1)
        return monday, monday + timedelta(days=6)
    except (ValueError, IndexError):
        return None


def _parse_rules(row: dict) -> list[str]:
    try:
        return list(json.loads(row.get("matched_rules_json") or "[]"))
    except (json.JSONDecodeError, TypeError):
        return []


def _parse_differentials(row: dict) -> list[dict]:
    try:
        return list(json.loads(row.get("differentials_json") or "[]"))
    except (json.JSONDecodeError, TypeError):
        return []


# ---------------------------------------------------------------------------
# Mapper
# ---------------------------------------------------------------------------

class Dhis2Mapper:
    """Agrège les analyses d'une période en valeurs DHIS2 comptables."""

    def __init__(self, cfg: Dhis2Config | None = None) -> None:
        self.cfg = cfg or Dhis2Config()

    def counts(self, rows: list[dict]) -> dict[str, int]:
        """Compteurs logiques — l'audit de référence avant mapping UID."""
        c = {key: 0 for key in self.cfg.data_elements}
        c["total_cases"] = len(rows)

        for row in rows:
            rules = _parse_rules(row)
            diffs = _parse_differentials(row)
            diseases = {str(d.get("disease")) for d in diffs}

            if "malaria" in diseases or "severe_malaria" in diseases:
                c["suspect_malaria"] += 1
            if "severe_malaria" in diseases or any(r.startswith("mal-sev-") for r in rules):
                c["suspect_severe_malaria"] += 1
            if any(r.startswith("mal-renal-") and
                   r != "mal-renal-avoid-nephrotoxins-007" for r in rules):
                c["malaria_renal_rrt"] += 1

            if "dengue" in diseases or "severe_dengue" in diseases:
                c["suspect_dengue"] += 1
            if "severe_dengue" in diseases or any(
                    r.startswith(("den-sev-", "den-warn-")) for r in rules):
                c["suspect_severe_dengue"] += 1
            if any(r.startswith("den-peds-") for r in rules):
                c["dengue_peds_critical"] += 1

            if "enteric_fever" in diseases:
                c["suspect_enteric_fever"] += 1
            if any(r.startswith("typ-xdr-") for r in rules):
                c["typhoid_xdr"] += 1

            if "yellow_fever" in diseases:
                c["suspect_yellow_fever"] += 1
            if any("vhf" in r for r in rules) or "marburg" in diseases or "ebola" in diseases \
                    or "lassa" in diseases:
                c["suspected_vhf"] += 1
            # V1.3 — leptospirose + méningocoque (surveillance élargie)
            if "leptospirosis" in diseases or any(r.startswith("lepto-") for r in rules):
                c["suspect_leptospirosis"] += 1
            if "meningococcal" in diseases or any(r.startswith("men-") for r in rules):
                c["suspect_meningococcal"] += 1

            if "zika" in diseases:
                c["suspect_zika"] += 1
            if any(r.startswith("zik-") and "pregn" in r for r in rules):
                c["zika_pregnant"] += 1

            if any(r.startswith("scd-") for r in rules):
                c["scd_fever"] += 1
            if "malaria" in diseases and any(r.startswith("preg-") for r in rules):
                c["pregnancy_malaria"] += 1

            if str(row.get("urgency")) in ("emergency", "immediate"):
                c["urgent_cases"] += 1
            if str(row.get("severity")) == "critical":
                c["critical_cases"] += 1
        return c

    def map(self, rows: list[dict], period: str) -> DataValueSet:
        """Construit le jeu de valeurs DHIS2 de la période."""
        c = self.counts(rows)
        values: list[DataValue] = []
        for key, n in sorted(c.items()):
            uid = self.cfg.data_element_uid(key)
            if uid is None or n == 0:
                continue  # pas d'élément mappé ou rien à signaler
            values.append(DataValue(
                data_element=uid, org_unit=self.cfg.org_unit,
                period=period, value=str(n),
                category_option_combo=self.cfg.category_option_combo,
            ))
        return DataValueSet(data_values=values, org_unit=self.cfg.org_unit,
                            period=period)
