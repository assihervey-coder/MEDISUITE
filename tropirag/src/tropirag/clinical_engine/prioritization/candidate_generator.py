"""Génération des maladies candidates — à partir du contexte géographique + symptômes."""
from __future__ import annotations

from tropirag.core.enums import SymptomCategory
from tropirag.domain.clinical_case.entities import ClinicalCase
from tropirag.domain.diseases.taxonomy import DISEASE_GROUPS


def candidate_diseases(case: ClinicalCase) -> list[str]:
    """Pré-filtre du différentiel : candidats plausibles AVANT les règles."""
    out: set[str] = set()
    codes = case.symptom_codes()
    # fièvre + voyage → tout le spectre fébrile tropical
    if codes & {"fever", "high_fever"}:
        if case.travel.segments:
            out.update(DISEASE_GROUPS["parasitic"] + DISEASE_GROUPS["arboviruses"] + DISEASE_GROUPS["bacterial"])
        else:
            out.update(["influenza", "covid19"])
    if codes & {"jaundice", "dark_urine"}:
        out.update(["yellow_fever", "malaria", "hepatitis_a", "leptospirosis"])
    if "arthralgia" in codes:
        out.update(["chikungunya", "dengue", "zika"])
    if codes & {"bleeding_gums", "epistaxis", "petechiae", "abnormal_bleeding"}:
        out.update(["dengue", "severe_dengue", "ebola", "lassa", "meningococcal"])
    if "neck_stiffness" in codes:
        out.add("meningococcal")
    # formes sévères si red flags présents
    if codes & {"coma", "confusion", "convulsions", "prostration"}:
        out.update(["severe_malaria", "meningococcal"])
    return sorted(out)
