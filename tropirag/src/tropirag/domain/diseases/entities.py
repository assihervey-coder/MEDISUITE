"""Taxonomie des maladies ciblées par TropiRAG V1 (fièvre + voyage)."""
from __future__ import annotations

from dataclasses import dataclass, field

from tropirag.core.enums import DiseaseCategory, Severity


@dataclass(slots=True)
class Disease:
    code: str                     # 'malaria', 'dengue', ...
    label_fr: str
    label_en: str
    category: DiseaseCategory
    incubation_key: str | None = None   # clé INCUBATION_WINDOWS_DAYS
    baseline_priority: float = 0.5     # priorité a priori (0–1)
    must_not_miss: bool = False        # ne jamais rater → escalade si suspecté
    evidence_refs: list[str] = field(default_factory=list)


DISEASES: dict[str, Disease] = {
    "malaria": Disease(
        code="malaria", label_fr="Paludisme", label_en="Malaria",
        category=DiseaseCategory.PARASITIC, incubation_key="malaria_falciparum",
        baseline_priority=0.85, must_not_miss=True,
        evidence_refs=["who-malaria-2023", "msf-malaria-guidelines"],
    ),
    "severe_malaria": Disease(
        code="severe_malaria", label_fr="Paludisme sévère", label_en="Severe malaria",
        category=DiseaseCategory.PARASITIC, incubation_key="malaria_falciparum",
        baseline_priority=0.95, must_not_miss=True,
        evidence_refs=["who-malaria-severe-2023"],
    ),
    "dengue": Disease(
        code="dengue", label_fr="Dengue", label_en="Dengue",
        category=DiseaseCategory.VIRAL, incubation_key="dengue",
        baseline_priority=0.55, must_not_miss=False,
        evidence_refs=["who-dengue-2024", "msf-dengue"],
    ),
    "severe_dengue": Disease(
        code="severe_dengue", label_fr="Dengue sévère", label_en="Severe dengue",
        category=DiseaseCategory.VIRAL, incubation_key="dengue",
        baseline_priority=0.9, must_not_miss=True,
        evidence_refs=["who-dengue-2024"],
    ),
    "enteric_fever": Disease(
        code="enteric_fever", label_fr="Fièvre typhoïde", label_en="Enteric fever",
        category=DiseaseCategory.BACTERIAL, incubation_key="enteric_fever",
        baseline_priority=0.45, must_not_miss=False,
        evidence_refs=["who-typhoid-2018", "cdc-typhoid"],
    ),
    "chikungunya": Disease(
        code="chikungunya", label_fr="Chikungunya", label_en="Chikungunya",
        category=DiseaseCategory.VIRAL, incubation_key="chikungunya",
        baseline_priority=0.35, evidence_refs=["who-chikungunya"],
    ),
    "zika": Disease(
        code="zika", label_fr="Zika", label_en="Zika",
        category=DiseaseCategory.VIRAL, incubation_key="zika",
        baseline_priority=0.2, evidence_refs=["who-zika"],
    ),
    "yellow_fever": Disease(
        code="yellow_fever", label_fr="Fièvre jaune", label_en="Yellow fever",
        category=DiseaseCategory.VIRAL, incubation_key="yellow_fever",
        baseline_priority=0.6, must_not_miss=True,
        evidence_refs=["who-yf"],
    ),
    "ebola": Disease(
        code="ebola", label_fr="Maladie à virus Ebola", label_en="Ebola virus disease",
        category=DiseaseCategory.VIRAL, incubation_key="ebola",
        baseline_priority=0.99, must_not_miss=True,
        evidence_refs=["who-ebola-2024"],
    ),
    "marburg": Disease(
        code="marburg", label_fr="Maladie à virus Marburg", label_en="Marburg virus disease",
        category=DiseaseCategory.VIRAL, incubation_key="marburg",
        baseline_priority=0.99, must_not_miss=True,
        evidence_refs=["who-marburg"],
    ),
    "lassa": Disease(
        code="lassa", label_fr="Fièvre de Lassa", label_en="Lassa fever",
        category=DiseaseCategory.VIRAL, incubation_key="lassa",
        baseline_priority=0.9, must_not_miss=True,
        evidence_refs=["who-lassa"],
    ),
    "meningococcal": Disease(
        code="meningococcal", label_fr="Méningite à méningocoque", label_en="Meningococcal meningitis",
        category=DiseaseCategory.BACTERIAL, incubation_key="meningococcal",
        baseline_priority=0.8, must_not_miss=True,
        evidence_refs=["who-meningitis"],
    ),
    "rickettsial": Disease(
        code="rickettsial", label_fr="Rickettsiose (fièvre boutonneuse)", label_en="Rickettsiosis",
        category=DiseaseCategory.RICKETTSIAL, incubation_key="rickettsial",
        baseline_priority=0.3, evidence_refs=["msf-rickettsia"],
    ),
    "leptospirosis": Disease(
        code="leptospirosis", label_fr="Leptospirose", label_en="Leptospirosis",
        category=DiseaseCategory.BACTERIAL, incubation_key="leptospirosis",
        baseline_priority=0.25, evidence_refs=["who-lepto"],
    ),
    "influenza": Disease(
        code="influenza", label_fr="Syndrome grippal", label_en="Influenza",
        category=DiseaseCategory.VIRAL, incubation_key="influenza",
        baseline_priority=0.3, evidence_refs=["cdc-flu"],
    ),
    "covid19": Disease(
        code="covid19", label_fr="COVID-19", label_en="COVID-19",
        category=DiseaseCategory.VIRAL, incubation_key="covid19",
        baseline_priority=0.2, evidence_refs=["who-covid"],
    ),
    "hepatitis_a": Disease(
        code="hepatitis_a", label_fr="Hépatite A", label_en="Hepatitis A",
        category=DiseaseCategory.VIRAL, incubation_key="hepatitis_a",
        baseline_priority=0.15, evidence_refs=["who-hepa"],
    ),
    # --- V1.1 : drépanocytose / grossesse (comorbidités et contextes) --------
    "sickle_cell_disease": Disease(
        code="sickle_cell_disease", label_fr="Drépanocytose", label_en="Sickle cell disease",
        category=DiseaseCategory.UNKNOWN, baseline_priority=0.7, must_not_miss=False,
        evidence_refs=["who-scd-2024"],
    ),
    "acute_chest_syndrome": Disease(
        code="acute_chest_syndrome", label_fr="Syndrome thoracique aigu (SCD)",
        label_en="Acute chest syndrome", category=DiseaseCategory.UNKNOWN,
        baseline_priority=0.95, must_not_miss=True, evidence_refs=["who-scd-2024"],
    ),
    "invasive_bacterial_infection": Disease(
        code="invasive_bacterial_infection", label_fr="Infection bactérienne invasive",
        label_en="Invasive bacterial infection", category=DiseaseCategory.BACTERIAL,
        baseline_priority=0.8, must_not_miss=True, evidence_refs=["who-scd-2024"],
    ),
    "osteomyelitis": Disease(
        code="osteomyelitis", label_fr="Ostéomyélite", label_en="Osteomyelitis",
        category=DiseaseCategory.BACTERIAL, baseline_priority=0.3,
        evidence_refs=["who-scd-2024"],
    ),
    "acute_hemolysis": Disease(
        code="acute_hemolysis", label_fr="Hémolyse aiguë", label_en="Acute hemolysis",
        category=DiseaseCategory.UNKNOWN, baseline_priority=0.5,
        evidence_refs=["who-scd-2024"],
    ),
    "malaria_in_pregnancy": Disease(
        code="malaria_in_pregnancy", label_fr="Paludisme gestationnel",
        label_en="Malaria in pregnancy", category=DiseaseCategory.PARASITIC,
        incubation_key="malaria_falciparum", baseline_priority=0.9, must_not_miss=True,
        evidence_refs=["who-malaria-pregnancy-2023"],
    ),
}


def disease(code: str) -> Disease | None:
    return DISEASES.get(code)


def diseases_by_codes(codes: list[str]) -> list[Disease]:
    return [DISEASES[c] for c in codes if c in DISEASES]
