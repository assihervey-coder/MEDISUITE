"""Taxonomie des symptômes — vocabulaire canonique fièvre + voyage (Afrique de l'Ouest).

Codes stables (utilisés dans les règles YAML — ne pas renommer sans migration).
"""
from __future__ import annotations

from tropirag.core.enums import SymptomCategory

# (code, label FR, label EN, catégorie, sévère si qualificatif)
SYMPTOMS: dict[str, dict] = {
    "fever":                    {"fr": "fièvre", "en": "fever", "cat": SymptomCategory.GENERAL},
    "high_fever":               {"fr": "fièvre élevée ≥ 39,5 °C", "en": "high fever", "cat": SymptomCategory.GENERAL},
    "chills":                   {"fr": "frissons", "en": "chills", "cat": SymptomCategory.GENERAL},
    "sweats":                   {"fr": "sueurs", "en": "sweats", "cat": SymptomCategory.GENERAL},
    "headache":                 {"fr": "céphalées", "en": "headache", "cat": SymptomCategory.NEUROLOGICAL},
    "myalgia":                  {"fr": "myalgies", "en": "myalgia", "cat": SymptomCategory.MUSCULOSKELETAL},
    "arthralgia":               {"fr": "arthralgies", "en": "arthralgia", "cat": SymptomCategory.MUSCULOSKELETAL},
    "back_pain":                {"fr": "lombalgies", "en": "back pain", "cat": SymptomCategory.MUSCULOSKELETAL},
    "fatigue":                  {"fr": "asthénie", "en": "fatigue", "cat": SymptomCategory.GENERAL},
    "prostration":              {"fr": "prostration", "en": "prostration", "cat": SymptomCategory.GENERAL},
    "coma":                      {"fr": "coma", "en": "coma", "cat": SymptomCategory.NEUROLOGICAL},
    "confusion":                {"fr": "confusion", "en": "confusion", "cat": SymptomCategory.NEUROLOGICAL},
    "convulsions":              {"fr": "convulsions", "en": "seizures", "cat": SymptomCategory.NEUROLOGICAL},
    "neck_stiffness":           {"fr": "raideur de nuque", "en": "neck stiffness", "cat": SymptomCategory.NEUROLOGICAL},
    "photophobia":              {"fr": "photophobie", "en": "photophobia", "cat": SymptomCategory.NEUROLOGICAL},
    "nausea":                   {"fr": "nausées", "en": "nausea", "cat": SymptomCategory.GASTROINTESTINAL},
    "vomiting":                 {"fr": "vomissements", "en": "vomiting", "cat": SymptomCategory.GASTROINTESTINAL},
    "diarrhea":                 {"fr": "diarrhée", "en": "diarrhea", "cat": SymptomCategory.GASTROINTESTINAL},
    "abdominal_pain":           {"fr": "douleurs abdominales", "en": "abdominal pain", "cat": SymptomCategory.GASTROINTESTINAL},
    "constipation":             {"fr": "constipation", "en": "constipation", "cat": SymptomCategory.GASTROINTESTINAL},
    "anorexia":                 {"fr": "anorexie", "en": "anorexia", "cat": SymptomCategory.GASTROINTESTINAL},
    "jaundice":                 {"fr": "ictère", "en": "jaundice", "cat": SymptomCategory.CUTANEOUS},
    "dark_urine":               {"fr": "urines foncées", "en": "dark urine", "cat": SymptomCategory.GENITOURINARY},
    "rash":                     {"fr": "éruption cutanée", "en": "rash", "cat": SymptomCategory.CUTANEOUS},
    "petechiae":                {"fr": "pétéchies", "en": "petechiae", "cat": SymptomCategory.HEMORRHAGIC},
    "ecchymoses":               {"fr": "ecchymoses", "en": "ecchymoses", "cat": SymptomCategory.HEMORRHAGIC},
    "bleeding_gums":            {"fr": "saignements gingivaux", "en": "bleeding gums", "cat": SymptomCategory.HEMORRHAGIC},
    "epistaxis":                {"fr": "épistaxis", "en": "epistaxis", "cat": SymptomCategory.HEMORRHAGIC},
    "hematemesis":              {"fr": "hématémèse", "en": "hematemesis", "cat": SymptomCategory.HEMORRHAGIC},
    "melena":                   {"fr": "méléna", "en": "melena", "cat": SymptomCategory.HEMORRHAGIC},
    "hematuria":                {"fr": "hématurie", "en": "hematuria", "cat": SymptomCategory.HEMORRHAGIC},
    "abnormal_bleeding":        {"fr": "saignements anormaux", "en": "abnormal bleeding", "cat": SymptomCategory.HEMORRHAGIC},
    "cough":                    {"fr": "toux", "en": "cough", "cat": SymptomCategory.RESPIRATORY},
    "sore_throat":              {"fr": "angine", "en": "sore throat", "cat": SymptomCategory.RESPIRATORY},
    "rhinorrhea":               {"fr": "rhinorrhée", "en": "rhinorrhea", "cat": SymptomCategory.RESPIRATORY},
    "dyspnea":                  {"fr": "dyspnée", "en": "dyspnea", "cat": SymptomCategory.RESPIRATORY},
    "chest_pain":               {"fr": "douleur thoracique", "en": "chest pain", "cat": SymptomCategory.CARDIOVASCULAR},
    "palpitations":             {"fr": "palpitations", "en": "palpitations", "cat": SymptomCategory.CARDIOVASCULAR},
    "edema":                    {"fr": "œdèmes", "en": "edema", "cat": SymptomCategory.CARDIOVASCULAR},
    "dizziness":                {"fr": "vertiges", "en": "dizziness", "cat": SymptomCategory.NEUROLOGICAL},
    "conjunctival_injection":    {"fr": "injection conjonctivale", "en": "conjunctival injection", "cat": SymptomCategory.CUTANEOUS},
    "retro_orbital_pain":       {"fr": "douleur rétro-orbitaire", "en": "retro-orbital pain", "cat": SymptomCategory.NEUROLOGICAL},
    "urticaria":                {"fr": "urticaire", "en": "urticaria", "cat": SymptomCategory.CUTANEOUS},
    "pruritus":                 {"fr": "prurit", "en": "pruritus", "cat": SymptomCategory.CUTANEOUS},
    "odynophagia":              {"fr": "odynophagie", "en": "odynophagia", "cat": SymptomCategory.RESPIRATORY},
    "aphthae":                  {"fr": "aphtes", "en": "aphthae", "cat": SymptomCategory.CUTANEOUS},
    "odynophagia_severe":       {"fr": "odynophagie sévère", "en": "severe odynophagia", "cat": SymptomCategory.RESPIRATORY},
    "weight_loss":              {"fr": "amaigrissement", "en": "weight loss", "cat": SymptomCategory.GENERAL},
    "night_sweats":             {"fr": "sueurs nocturnes", "en": "night sweats", "cat": SymptomCategory.GENERAL},
    "hemoptysis":               {"fr": "hémoptysie", "en": "hemoptysis", "cat": SymptomCategory.HEMORRHAGIC},
    "hepatomegaly":             {"fr": "hépatomégalie", "en": "hepatomegaly", "cat": SymptomCategory.GASTROINTESTINAL},
    "splenomegaly":             {"fr": "splénomégalie", "en": "splenomegaly", "cat": SymptomCategory.GASTROINTESTINAL},
    "heatosplenomegaly":        {"fr": "hépatosplénomégalie", "en": "hepatosplenomegaly", "cat": SymptomCategory.GASTROINTESTINAL},
    "dysuria":                  {"fr": "dysurie", "en": "dysuria", "cat": SymptomCategory.GENITOURINARY},
    # --- drépanocytose / grossesse (itération V1.1) -----------------------
    "bone_pain":                {"fr": "douleurs osseuses", "en": "bone pain", "cat": SymptomCategory.MUSCULOSKELETAL},
    "focal_deficit":             {"fr": "déficit neurologique focal", "en": "focal neurologic deficit", "cat": SymptomCategory.NEUROLOGICAL},
    "pallor":                    {"fr": "pâleur conjonctivale", "en": "pallor", "cat": SymptomCategory.GENERAL},
    "oliguria":                   {"fr": "oligurie / anurie", "en": "oliguria", "cat": SymptomCategory.GENITOURINARY},
    "vaginal_bleeding":          {"fr": "métrorragies", "en": "vaginal bleeding", "cat": SymptomCategory.GENITOURINARY},
    "decreased_fetal_movements": {"fr": "diminution des mouvements actifs fœtaux", "en": "decreased fetal movements", "cat": SymptomCategory.GENITOURINARY},
    # --- V1.3 : leptospirose + méningocoque pédiatrique -------------------
    "muscle_tenderness":        {"fr": "douleurs musculaires à la palpation", "en": "muscle tenderness", "cat": SymptomCategory.MUSCULOSKELETAL},
    "irritability":             {"fr": "irritabilité / enfant inconsolable", "en": "irritability (inconsolable crying)", "cat": SymptomCategory.NEUROLOGICAL},
    "poor_feeding":              {"fr": "refus alimentaire / arrêt des prises", "en": "poor feeding", "cat": SymptomCategory.GASTROINTESTINAL},
    "bulging_fontanelle":       {"fr": "fontanelle bombée", "en": "bulging fontanelle", "cat": SymptomCategory.NEUROLOGICAL},
}

# Symptômes "sévères par nature" (red flags potentiels)
INTRINSICALLY_SEVERE: set[str] = {
    "coma", "convulsions", "hematemesis", "melena", "hemoptysis",
    "high_fever", "prostration", "abnormal_bleeding",
    "focal_deficit", "decreased_fetal_movements",
}


def symptom_label(code: str, lang: str = "fr") -> str:
    meta = SYMPTOMS.get(code)
    if not meta:
        return code
    return meta.get("fr" if lang == "fr" else "en", code)


def symptom_category(code: str) -> SymptomCategory | None:
    meta = SYMPTOMS.get(code)
    return meta["cat"] if meta else None
