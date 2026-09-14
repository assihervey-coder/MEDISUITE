"""Moteur temporel — incubations, compatibilité chronologique, fenêtres de risque."""
from __future__ import annotations

from dataclasses import dataclass

from tropirag.core.constants import INCUBATION_WINDOWS_DAYS
from tropirag.domain.clinical_case.entities import ClinicalCase
from tropirag.domain.diseases.entities import DISEASES


@dataclass(slots=True)
class IncubationCheck:
    disease: str
    window_days: tuple[float, float]
    days_since_return: float | None
    compatible: bool
    reason: str

    def to_dict(self) -> dict:
        return {
            "disease": self.disease,
            "window_days": list(self.window_days),
            "days_since_return": self.days_since_return,
            "compatible": self.compatible,
            "reason": self.reason,
        }


class IncubationEngine:
    """Vérifie que la chronologie voyage → symptômes est compatible par maladie."""

    def check_all(self, case: ClinicalCase, candidates: list[str] | None = None) -> list[IncubationCheck]:
        tl = case.timeline
        d = tl.days_since_return() if tl else None
        checks: list[IncubationCheck] = []
        for code in candidates or []:
            meta = DISEASES.get(code)
            key = (meta.incubation_key if meta else None) or code
            window = INCUBATION_WINDOWS_DAYS.get(key)
            if not window:
                continue
            if d is None:
                reason = "Dates de voyage incomplètes — chronologie non évaluable, pathologie non exclue"
                compatible = True
            elif d < 0:
                reason = f"Symptômes apparus avant le retour ({d:.0f} j) — contamination possible en cours de séjour"
                compatible = True
            elif window[0] <= d <= window[1]:
                reason = f"Délai {d:.0f} j compatible avec l'incubation [{window[0]:.0f}–{window[1]:.0f} j]"
                compatible = True
            elif d < window[0]:
                reason = (f"Trop précoce ({d:.0f} j < incubation minimale {window[0]:.0f} j) — "
                          f"possible mais atypique ; réévaluer")
                compatible = False
            else:
                reason = f"Trop tardif ({d:.0f} j > incubation maximale {window[1]:.0f} j) — très improbable"
                compatible = False
            checks.append(IncubationCheck(disease=code, window_days=window,
                                          days_since_return=d, compatible=compatible, reason=reason))
        return checks


class TemporalReasoner:
    """Résumé humain de la chronologie pour la réponse clinique."""

    def narrate(self, case: ClinicalCase) -> list[str]:
        lines: list[str] = []
        tl = case.timeline
        if tl is None:
            return lines
        onset = tl.anchor.symptom_onset
        if onset and case.consultation_date:
            dur = tl.anchor.days_since_onset
            if dur is not None:
                lines.append(f"Symptômes débutés il y a {dur:.0f} jour(s) (J-{dur:.0f}).")
        ret = tl.travel.last_return()
        if ret and case.consultation_date:
            d = tl.days_since_return()
            lines.append(f"Retour de voyage il y a {d:.0f} jour(s).")
            if onset:
                d2 = tl.days_onset_after_return()
                if d2 is not None:
                    if d2 >= 0:
                        lines.append(f"Début des symptômes {d2:.0f} jour(s) APRÈS le retour.")
                    else:
                        lines.append(f"Début des symptômes {-d2:.0f} jour(s) AVANT le retour (malade sur place).")
        segs = case.travel.countries_visited()
        if segs:
            lines.append(f"Pays visités : {', '.join(segs)}.")
        return lines
