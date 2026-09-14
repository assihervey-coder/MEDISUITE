"""Builder du cas clinique — de l'entrée brute (JSON/dict) à l'agrégat validé.

Tolérant en entrée (champs multiples acceptés), strict en sortie (agrégat
cohérent avec chronologie et expositions calculées).
"""
from __future__ import annotations

import re

from tropirag.core.datetime import parse_date_flexible, parse_duration
from tropirag.core.identifiers import new_id
from tropirag.domain.clinical_case.entities import ClinicalCase
from tropirag.domain.diagnostics.results import parse_lab_results
from tropirag.domain.medications.prescriptions import MedicationOrder
from tropirag.domain.patient.entities import Patient
from tropirag.domain.patient.value_objects import VitalSigns
from tropirag.domain.symptoms.entities import Symptom
from tropirag.domain.symptoms.normalization import normalize_symptoms, parse_symptom_entries
from tropirag.domain.symptoms.taxonomy import SYMPTOMS
from tropirag.domain.travel.entities import TravelHistory
from tropirag.domain.travel.exposures import summarize_exposures
from tropirag.domain.travel.timeline import build_timeline
from tropirag.core.enums import SymptomCategory
from tropirag.core.datetime import local_now


def _first(d: dict, *keys, default=None):
    for k in keys:
        if k in d and d[k] not in (None, ""):
            return d[k]
    return default


def build_case(data: dict | None) -> ClinicalCase:
    """Construit un ClinicalCase depuis un dict d'entrée libre.

    Champs acceptés (exhaustif mais tolérant) :
      patient{...}, symptoms[] (codes et/ou texte libre), vitals{...},
      labs[]/lab_results[], travel{...}, medications[], consultation_date,
      free_text...
    """
    data = data or {}

    patient = Patient.from_dict(data.get("patient") or {})

    # --- symptômes : trois sources fusionnées --------------------------------
    symptoms: list[Symptom] = []
    seen: set[str] = set()

    # 1) entrées structurées [{'code': ...}]
    for s in parse_symptom_entries(_first(data, "symptoms", "symptom_list", default=[]) or []):
        if s.code not in seen:
            symptoms.append(s)
            seen.add(s.code)

    # 2) texte libre symptomatique
    free = str(_first(data, "free_text", "symptoms_text", "history", default="") or "")
    for s in normalize_symptoms(free):
        if s.code not in seen:
            symptoms.append(s)
            seen.add(s.code)

    # 3) codes bruts ['fever', ...]
    for code in _first(data, "symptom_codes", default=[]) or []:
        code = str(code).strip()
        if code in SYMPTOMS and code not in seen:
            meta = SYMPTOMS[code]
            symptoms.append(Symptom(code=code, label_fr=meta["fr"],
                                    category=meta.get("cat", SymptomCategory.GENERAL)))
            seen.add(code)

    symptoms.sort(key=lambda s: s.code)

    # date d'apparition : champ dédié ou premier onset trouvé
    onset = parse_date_flexible(_first(data, "symptom_onset", "onset_date"))
    if onset is None:
        for s in symptoms:
            if s.onset_date:
                onset = s.onset_date
                break
    if onset is None:
        # durée inline dans le texte libre : « depuis 4 jours »
        m = re.search(r"depuis\s+(\d+(?:\.\d+)?)\s*(jours?|j|semaines?|heures?|h)", free, re.IGNORECASE)
        if m:
            n = float(m.group(1))
            unit = m.group(2).lower()
            if unit.startswith(("heure", "h")):
                dur = parse_duration(f"{n / 24} jours")
            elif unit.startswith("sem"):
                dur = parse_duration(f"{n * 7} jours")
            else:
                dur = parse_duration(f"{n} jours")
            from datetime import timedelta

            onset = (parse_date_flexible(_first(data, "consultation_date"))
                     or local_now().date()) - timedelta(days=round(dur.days))
    if onset is None:
        d = _first(data, "symptom_duration", "fever_duration")
        if d is not None:
            dur = parse_duration(d)
            if dur is not None:
                onset = (data.get("consultation_date") and parse_date_flexible(data["consultation_date"]) or local_now().date())
                from datetime import timedelta

                onset = onset - timedelta(days=round(dur.days))

    # --- constantes -----------------------------------------------------------
    vd = data.get("vitals") or data.get("vital_signs") or {}
    vitals = VitalSigns(
        temperature_c=vd.get("temperature_c") or (float(vd["temperature"].replace(",", ".")) if isinstance(vd.get("temperature"), str) else vd.get("temperature")),
        systolic_bp=vd.get("systolic_bp") or vd.get("bp_systolic"),
        diastolic_bp=vd.get("diastolic_bp") or vd.get("bp_diastolic"),
        heart_rate=vd.get("heart_rate") or vd.get("pulse"),
        respiratory_rate=vd.get("respiratory_rate"),
        spo2_pct=vd.get("spo2_pct") or vd.get("spo2"),
        capillary_refill_s=vd.get("capillary_refill_s"),
        consciousness=vd.get("consciousness"),
    )
    # fièvre documentée par constantes → symptôme si absent
    if vitals.temperature_c is not None and vitals.temperature_c >= 38.0 and "fever" not in seen:
        code = "high_fever" if vitals.temperature_c >= 39.5 else "fever"
        meta = SYMPTOMS[code]
        symptoms.append(Symptom(code=code, label_fr=meta["fr"], category=meta["cat"], onset_date=onset))
        seen.add(code)
        symptoms.sort(key=lambda s: s.code)

    # --- biologie ------------------------------------------------------------
    labs = parse_lab_results(_first(data, "lab_results", "labs", default=[]) or [])

    # --- voyage ---------------------------------------------------------------
    travel = TravelHistory.from_dict(data.get("travel") or {})

    # --- médicaments -----------------------------------------------------------
    meds = [MedicationOrder.from_dict(m) for m in (data.get("medications") or [])]

    # --- chronologie + expositions ----------------------------------------------
    consult = parse_date_flexible(_first(data, "consultation_date", default=None)) or local_now().date()
    timeline = build_timeline(consult, onset, travel)
    exposures = summarize_exposures(travel)

    return ClinicalCase(
        case_id=data.get("case_id") or new_id("case"),
        patient=patient,
        symptoms=symptoms,
        vitals=vitals,
        lab_results=labs,
        travel=travel,
        exposures=exposures,
        timeline=timeline,
        medications=meds,
        free_text=free,
        consultation_date=consult,
    )
