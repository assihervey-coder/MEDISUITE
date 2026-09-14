"""Normalisation des symptômes : texte libre FR/EN → codes canoniques.

Dictionnaire de synonymes ouest-africains inclus (argot clinique inclus).
Entrée : « le malade a des frissons et vomit beaucoup »
Sortie : ['chills', 'vomiting']
"""
from __future__ import annotations

import re

from tropirag.core.datetime import parse_date_flexible, parse_duration
from tropirag.domain.symptoms.entities import Symptom
from tropirag.domain.symptoms.taxonomy import SYMPTOMS, SymptomCategory

# ---------------------------------------------------------------------------
# Synonymes FR/EN → code canonique (minuscule, sans accents)
# ---------------------------------------------------------------------------
_SYNONYMS: dict[str, str] = {
    # fièvre
    "fievre": "fever", "fever": "fever", "temperature": "fever", "pyrexie": "fever",
    "corps chaud": "fever", "chaud le corps": "fever", "fievre elevee": "high_fever",
    "high fever": "high_fever", "fievre a 39": "high_fever", "fievre a 40": "high_fever",
    "fievre haute": "high_fever", "hyperthermie": "fever",
    # frissons / sueurs
    "frissons": "chills", "frisson": "chills", "chills": "chills", "tremblements": "chills",
    "sueurs": "sweats", "sueur": "sweats", "sweats": "sweats", "transpiration": "sweats",
    "sueurs nocturnes": "night_sweats", "night sweats": "night_sweats",
    # neuro
    "cephalees": "headache", "cephalee": "headache", "mal de tete": "headache",
    "headache": "headache", "tete qui fait mal": "headache", "migraine": "headache",
    "vertiges": "dizziness", "vertige": "dizziness", "dizziness": "dizziness", "etourdissements": "dizziness",
    "confusion": "confusion", "confus": "confusion", "desorientation": "confusion",
    "somnolence": "confusion", "obnubilation": "confusion",
    "coma": "coma", "inconscient": "coma", "comateux": "coma", "unresponsive": "coma",
    "convulsions": "convulsions", "convulsion": "convulsions", "crise convulsive": "convulsions",
    "seizures": "convulsions", "seizure": "convulsions", "crises": "convulsions",
    "raideur de nuque": "neck_stiffness", "nuque raide": "neck_stiffness",
    "neck stiffness": "neck_stiffness", "raideur nuque": "neck_stiffness",
    "photophobie": "photophobia", "photophobia": "photophobia", "lumiere gene": "photophobia",
    "douleur retro orbitaire": "retro_orbital_pain", "retro orbital pain": "retro_orbital_pain",
    "douleur derriere les yeux": "retro_orbital_pain", "yeux qui font mal": "retro_orbital_pain",
    # musculo
    "myalgies": "myalgia", "myalgie": "myalgia", "douleurs musculaires": "myalgia",
    "muscle pain": "myalgia", "courbatures": "myalgia", "corps qui casse": "myalgia", "corps casse": "myalgia", "corps brise": "myalgia",
    "arthralgies": "arthralgia", "arthralgie": "arthralgia", "douleurs articulaires": "arthralgia",
    "joint pain": "arthralgia", "articulations douloureuses": "arthralgia",
    "lombalgies": "back_pain", "lombalgie": "back_pain", "dos douloureux": "back_pain",
    "back pain": "back_pain", "rein qui fait mal": "back_pain",
    # general
    "asthenie": "fatigue", "fatigue": "fatigue", "faiblesse": "fatigue",
    "tiredness": "fatigue", "epuisement": "fatigue", "corps mou": "fatigue",
    "prostration": "prostration", "prostre": "prostration", "ne tient plus debout": "prostration",
    "amaigrissement": "weight_loss", "perte de poids": "weight_loss", "weight loss": "weight_loss",
    "maigrit": "weight_loss",
    # gastro
    "nausees": "nausea", "nausee": "nausea", "nausea": "nausea", "envie de vomir": "nausea",
    "vomissements": "vomiting", "vomissement": "vomiting", "vomiting": "vomiting",
    "vomit": "vomiting", "vomi": "vomiting", "rend tout": "vomiting",
    "diarrhee": "diarrhea", "diarrhea": "diarrhea", "selles liquides": "diarrhea",
    "ventre qui coule": "diarrhea", "selles frequentes": "diarrhea",
    "douleurs abdominales": "abdominal_pain", "douleur abdominale": "abdominal_pain",
    "abdominal pain": "abdominal_pain", "ventre douloureux": "abdominal_pain",
    "mal au ventre": "abdominal_pain", "epigastralgies": "abdominal_pain",
    "constipation": "constipation", "constipe": "constipation",
    "anorexie": "anorexia", "ne mange plus": "anorexia", "perte d appetit": "anorexia",
    "appetit perdu": "anorexia", "anorexia": "anorexia",
    # cutané / hémorragique
    "ictere": "jaundice", "jaundice": "jaundice", "jaunisse": "jaundice",
    "icterique": "jaundice", "fievre icterique": "jaundice", "subicterique": "jaundice",
    "icteres": "jaundice", "jaune des yeux et de la peau": "jaundice",
    "yeux jaunes": "jaundice", "peau jaune": "jaundice", "ict conj": "jaundice",
    "urines foncees": "dark_urine", "urine foncee": "dark_urine", "dark urine": "dark_urine",
    "eruption": "rash", "eruption cutanee": "rash", "rash": "rash", "taches": "rash",
    "taches rouges": "rash", " eruption sur le corps": "rash", "exantheme": "rash",
    "petechies": "petechiae", "petechiae": "petechiae", "points rouges": "petechiae",
    "ecchymoses": "ecchymoses", "ecchymosis": "ecchymoses", "bleus": "ecchymoses",
    # V1.3 — purpura de terrain (méningocoque pédiatrique)
    "purpura": "petechiae", "taches violettes": "petechiae",
    "taches violettes sur la peau": "petechiae", "taches rouges qui ne s effacent pas": "petechiae",
    "petites taches rouges": "petechiae", "taches rouges qui ne partent pas": "petechiae",
    "hemorragies sous cutanees": "petechiae", "hematomes multiples": "ecchymoses",
    "marbrures": "pallor", "peau marbree": "pallor", "mottling": "pallor",
    "saignement des gencives": "bleeding_gums", "saignements des gencives": "bleeding_gums",
    "sang au niveau des gencives": "bleeding_gums", "gencives qui saignent": "bleeding_gums",
    "bleeding gums": "bleeding_gums",
    "epistaxis": "epistaxis", "saignement de nez": "epistaxis", "nez qui saigne": "epistaxis",
    "nose bleed": "epistaxis", "sang dans le nez": "epistaxis",
    "hematemese": "hematemesis", "hematemesis": "hematemesis", "vomi sanglant": "hematemesis",
    "vomi du sang": "hematemesis", "vomissement de sang": "hematemesis", "blood vomiting": "hematemesis",
    "melena": "melena", "melaena": "melena", "selles noires": "melena",
    "sang dans les selles": "melena", "black stool": "melena",
    "hematurie": "hematuria", "hematuria": "hematuria", "urine rouge": "hematuria",
    "sang dans les urines": "hematuria", "sang dans l urine": "hematuria",
    "saignement": "abnormal_bleeding", "bleeding": "abnormal_bleeding",
    "hemorragie": "abnormal_bleeding", "saignements anormaux": "abnormal_bleeding",
    "abnormal bleeding": "abnormal_bleeding", "saigne beaucoup": "abnormal_bleeding",
    # respiratoire / cardio
    "toux": "cough", "cough": "cough", "tousse": "cough",
    "angine": "sore_throat", "gorge rouge": "sore_throat", "sore throat": "sore_throat",
    "mal de gorge": "sore_throat", "gorge douloureuse": "sore_throat",
    "rhinorrhee": "rhinorrhea", "nez qui coule": "rhinorrhea", "rhinorrhea": "rhinorrhea",
    "dyspnee": "dyspnea", "dyspnea": "dyspnea", "essoufflement": "dyspnea",
    "difficulte a respirer": "dyspnea", "shortness of breath": "dyspnea",
    "respiration rapide": "dyspnea", "polypnee": "dyspnea",
    "douleur thoracique": "chest_pain", "chest pain": "chest_pain", "poitrine douloureuse": "chest_pain",
    "douleur dans la poitrine": "chest_pain", "mal a la poitrine": "chest_pain",
    "douleur a la poitrine": "chest_pain",
    "palpitations": "palpitations", "coeur qui bat vite": "palpitations",
    "oedemes": "edema", "edeme": "edema", "edema": "edema", "jambes gonflees": "edema",
    "hemptysie": "hemoptysis", "hemoptysie": "hemoptysis", "hemoptysis": "hemoptysis",
    "crachats sanglants": "hemoptysis", "toux de sang": "hemoptysis",
    # divers
    "conjonctives injectees": "conjunctival_injection", "yeux rouges": "conjunctival_injection",
    "red eyes": "conjunctival_injection", "conjunctival injection": "conjunctival_injection",
    "urticaire": "urticaria", "urticaria": "urticaria",
    "prurit": "pruritus", "pruritus": "pruritus", "demangeaisons": "pruritus", "gratte": "pruritus",
    "odynophagie": "odynophagia", "odynophagia": "odynophagia",
    "difficulte a avaler": "odynophagia", "painful swallowing": "odynophagia",
    "aphtes": "aphthae", "aphthae": "aphthae", "aphte": "aphthae",
    "hepatomegalie": "hepatomegaly", "hepatomegaly": "hepatomegaly", "foie gros": "hepatomegaly",
    "splenomegalie": "splenomegaly", "splenomegaly": "splenomegaly", "rate gros": "splenomegaly",
    "hepatosplenomegalie": "heatosplenomegaly", "hepatosplenomegaly": "heatosplenomegaly",
    "dysurie": "dysuria", "dysuria": "dysuria", "brulures mictionnelles": "dysuria",
    # --- drépanocytose / grossesse (V1.1) -----------------------------------
    "douleurs osseuses": "bone_pain", "douleur osseuse": "bone_pain", "bone pain": "bone_pain",
    "os qui font mal": "bone_pain", "crise osseuse": "bone_pain", "crise drepano": "bone_pain",
    "crise vaso occlusive": "bone_pain", "douleurs des os": "bone_pain",
    "hemiplegie": "focal_deficit", "paralysie": "focal_deficit", "paralysie faciale": "focal_deficit",
    "deficit moteur": "focal_deficit", "bouche deviee": "focal_deficit",
    "faiblesse d un cote": "focal_deficit", "faiblesse d un cote du corps": "focal_deficit",
    "hemiparese": "focal_deficit", "hemiparesie": "focal_deficit",
    "faiblesse d un seul cote": "focal_deficit", "trouble de la conscience": "confusion",
    "focal deficit": "focal_deficit", "faiblesse musculaire d un cote": "focal_deficit",
    "pale": "pallor", "paleur": "pallor", "pallor": "pallor", "blanc comme un linge": "pallor",
    "yeux blancs": "pallor", "conjonctives decolorees": "pallor", "anemie clinique": "pallor",
    "oligurie": "oliguria", "anurie": "oliguria", "ne urine plus": "oliguria",
    "urine peu": "oliguria", "oliguria": "oliguria", "urine tres peu": "oliguria",
    "urine tres peu depuis hier": "oliguria", "urines rares": "oliguria",
    "metrorragies": "vaginal_bleeding", "metrorragie": "vaginal_bleeding",
    "saignement vaginal": "vaginal_bleeding", "pertes de sang": "vaginal_bleeding",
    "regles abondantes": "vaginal_bleeding", "vaginal bleeding": "vaginal_bleeding",
    "bebe bouge moins": "decreased_fetal_movements", "bebe ne bouge plus": "decreased_fetal_movements",
    "mouvements actifs diminues": "decreased_fetal_movements",
    "decreased fetal movements": "decreased_fetal_movements",
    "le foetus bouge moins": "decreased_fetal_movements",
    # --- leptospirose + méningocoque pédiatrique (V1.3) ----------------------
    "douleurs musculaires a la palpation": "muscle_tenderness",
    "muscles sensibles": "muscle_tenderness", "muscle tenderness": "muscle_tenderness",
    "mollets durs": "muscle_tenderness", "douleur des mollets": "muscle_tenderness",
    "enfant irritable": "irritability", "irritabilite": "irritability",
    "irritability": "irritability", "pleure sans arret": "irritability",
    "enfant inconsolable": "irritability", "geignements": "irritability",
    "agitation": "irritability", "cri incoercible": "irritability",
    "refus alimentaire": "poor_feeding", "refuse de manger": "poor_feeding",
    "ne mange plus": "poor_feeding", "poor feeding": "poor_feeding",
    "arret des prises de biberon": "poor_feeding", "descente des prises": "poor_feeding",
    "ne tete plus": "poor_feeding", "anorexie du nourrisson": "poor_feeding",
    "fontanelle bombee": "bulging_fontanelle", "fontanelle tendue": "bulging_fontanelle",
    "tete molle gonflee": "bulging_fontanelle", "bulging fontanelle": "bulging_fontanelle",
    "bombe la fontanelle": "bulging_fontanelle", "fontanelle dure": "bulging_fontanelle",
    "fontanelle bombee et tendue": "bulging_fontanelle",
}

# Qualificatifs de sévérité → marquer severe
_SEVERE_MARKERS = ("beaucoup", "important", "importante", "severe", "severes",
                  "intense", "violents", "violente", "incoercibles", "abondants",
                  "extreme", "tres fort", "abondante")

# Regex d'extraction d'intensité thermique : « fièvre 39,6 », « 39.5 °C », « T° 38.2 »
_TEMP_RE = re.compile(r"(\d{2}(?:[.,]\d)?)\s*(?:°\s*c\b|degres?|c\b)", re.IGNORECASE)
_TEMP_AFTER_FEVER = re.compile(
    r"(?:fievre|fever|temperature|hyperthermie|t°|t ?= ?)\D{0,12}(\d{2}(?:[.,]\d)?)", re.IGNORECASE
)


def _norm(text: str) -> str:
    import unicodedata

    t = unicodedata.normalize("NFKD", text.lower().strip())
    t = "".join(c for c in t if not unicodedata.combining(c))
    # V1.1 : apostrophes typographiques/droites → espace (« d'un » → « d un »)
    t = t.replace("'", " ").replace("\u2019", " ").replace("\u2018", " ")
    return re.sub(r"\s+", " ", t)


def normalize_symptoms(text: str | list[str] | None) -> list[Symptom]:
    """Extrait les symptômes canoniques d'un texte libre FR/EN.

    - détection par synonymes (longueur décroissante pour éviter les sous-chaînes)
    - « fièvre 39,5 » → high_fever
    - qualificatifs de sévérité → severity='severe'
    """
    if not text:
        return []
    raw = " ".join(text) if isinstance(text, list) else str(text)
    n = _norm(raw)
    found: dict[str, str] = {}  # code -> severity

    for syn, code in sorted(_SYNONYMS.items(), key=lambda kv: -len(kv[0])):
        if syn in n:
            found.setdefault(code, "present")

    # température explicite : « 39,6 °C », « fièvre 39,6 », « T° 38.2 »
    tval: float | None = None
    m = _TEMP_RE.search(n) or _TEMP_AFTER_FEVER.search(n)
    if m:
        try:
            tval = float(m.group(1).replace(",", "."))
        except ValueError:
            tval = None
    if tval is not None and tval >= 38.0:
        if tval >= 39.5:
            found["high_fever"] = "present"
        found["fever"] = "present"

    # sévérité par qualificatifs proches
    severe_affected = any(mk in n for mk in _SEVERE_MARKERS)

    out: list[Symptom] = []
    for code, sev in found.items():
        meta = SYMPTOMS.get(code, {})
        sev_final = "severe" if severe_affected and sev == "present" else sev
        out.append(
            Symptom(
                code=code,
                label_fr=meta.get("fr", code),
                category=meta.get("cat", SymptomCategory.GENERAL),
                severity=sev_final,
            )
        )
    # tri stable par code pour la reproductibilité
    out.sort(key=lambda s: s.code)
    return out


def symptom_codes(text: str | list[str] | None) -> list[str]:
    return [s.code for s in normalize_symptoms(text)]


def parse_symptom_entries(entries: list[dict] | None) -> list[Symptom]:
    """Parse des entrées structurées [{'code': 'fever', 'onset': '2025-08-01',
    'duration': '3 jours', 'severity': 'severe'}, ...]."""
    out: list[Symptom] = []
    for e in entries or []:
        code = str(e.get("code", "")).strip()
        if not code or code not in SYMPTOMS:
            continue
        meta = SYMPTOMS[code]
        onset = parse_date_flexible(e.get("onset"))
        dur = parse_duration(e.get("duration"))
        out.append(
            Symptom(
                code=code,
                label_fr=meta.get("fr", code),
                category=meta.get("cat", SymptomCategory.GENERAL),
                severity=str(e.get("severity", "present")),
                onset_date=onset,
                duration_days=dur.days if dur else None,
            )
        )
    return sorted(out, key=lambda s: s.code)
