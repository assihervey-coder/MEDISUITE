"""Compatibility Engine — 9 dimensions, verdict global."""
from __future__ import annotations

import importlib
from typing import Any

from ..._bridge import register

register()
_domain_compat = importlib.import_module("ecp.domain.compatibility.api")
_report = importlib.import_module("ecp.domain.compatibility.report")


def check(change_set_id: str, facts: dict[str, Any]) -> dict[str, Any]:
    """facts : ce que l'implémentation déclare toucher.

    Clés attendues (toutes optionnelles) :
      endpoints_before/after, drop_columns, expand_only,
      events_before/after, fhir_profiles, dicom_sop_changed,
      hl7_segments, model_changed, lineage_complete, threshold_changed
    """
    f = dict(facts)
    report = _report.CompatibilityReport(change_set_id=change_set_id)

    api = _domain_compat.ApiCompat()
    verdict, detail = api.check(f.get("endpoints_before", {}) or {},
                                f.get("endpoints_after", {}) or {})
    report.add(api.dimension, verdict, detail)

    db = _domain_compat.DatabaseCompat()
    if not any(k in f for k in ("drop_columns", "expand_only")):
        report.add("database", "NOT_APPLICABLE", "base de données inchangée")
    else:
        verdict, detail = db.check(f.get("drop_columns", []) or [],
                                   bool(f.get("expand_only", False)))
        report.add(db.dimension, verdict, detail)

    ev = _domain_compat.EventCompat()
    verdict, detail = ev.check(set(f.get("events_before", []) or []),
                               set(f.get("events_after", []) or {}))
    report.add(ev.dimension, verdict, detail)

    fh = _domain_compat.FhirCompat()
    verdict, detail = fh.check(list(f.get("fhir_profiles", []) or []))
    report.add(fh.dimension, verdict, detail)

    dc = _domain_compat.DicomCompat()
    verdict, detail = dc.check(bool(f.get("dicom_sop_changed", False)))
    report.add(dc.dimension, verdict, detail)

    hl = _domain_compat.Hl7Compat()
    verdict, detail = hl.check(list(f.get("hl7_segments", []) or []))
    report.add(hl.dimension, verdict, detail)

    ai = _domain_compat.AiCompat()
    verdict, detail = ai.check(bool(f.get("model_changed", False)),
                               bool(f.get("lineage_complete", False)),
                               bool(f.get("threshold_changed", False)))
    report.add(ai.dimension, verdict, detail)

    # clinical + configuration : évaluées côté moteur (V1 = règles simples)
    report.add("clinical",
               "REVIEW_REQUIRED" if f.get("clinical_touched") else "NOT_APPLICABLE",
               "toute modification clinique exige revue" if f.get("clinical_touched") else "")
    report.add("configuration",
               "WARNING" if f.get("config_undocumented") else "PASS",
               "changement de config non documenté" if f.get("config_undocumented") else "")

    return report.to_dict()
