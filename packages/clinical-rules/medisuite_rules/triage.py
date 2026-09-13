"""Règles de triage et défaillance d'organe — urgences et réanimation.

Référentiels : ESI 4e éd. (AHRQ 2020), CTMP (triage préhospitalier ivoirien),
qSOFA / SOFA (Surviving Sepsis Campaign 2021), NEWS2 (RCP 2017).
"""
from __future__ import annotations

from .scores import grade, sum_score


# ----------------------------------------------------------------- ESI

def esi(niveau_ressources: int, voies_aeriennes_stables: bool = True,
        conscience_stable: bool = True, signes_vitaux_dangereux: bool = False,
        facteur_risque_haut: bool = False, douleur_severe: bool = False,
        saignement_actif: bool = False) -> dict:
    """Emergency Severity Index v4 (AHRQ, 2020) — niveaux 1 à 5.

    niveau_ressources : nombre de ressources prédites (0→1, 1→2, 2→3, ≥3→4/5).
    """
    if not (voies_aeriennes_stables and conscience_stable) or signes_vitaux_dangereux:
        return {"niveau": 1, "couleur": "rouge", "libelle": "réanimation immédiate"}
    if facteur_risque_haut or douleur_severe or saignement_actif:
        return {"niveau": 2, "couleur": "orange", "libelle": "émergent (<10 min)"}
    if niveau_ressources >= 3:
        return {"niveau": 4, "couleur": "vert", "libelle": "moins urgent (60 min)"}
    if niveau_ressources == 2:
        return {"niveau": 3, "couleur": "jaune", "libelle": "urgent (30 min)"}
    return {"niveau": 5, "couleur": "bleu", "libelle": "non urgent (2 h)"}


# ----------------------------------------------------------------- CTMP (Côte d'Ivoire)

def ctmp(score: int) -> dict:
    """Clinical Triage & Management Protocol — triage préhospitalier ivoirien.

    Score 0-10 ; couleur de destination : rouge (détresse vitale),
    jaune (urgence relative), vert (urgence mineure), noir (décès / soins palliatifs).
    """
    mapping = [(2, "noir"), (4, "rouge"), (6, "jaune"), (10, "vert")]
    for seuil, couleur in mapping:
        if score <= seuil:
            label = {"noir": "décédé / comfort care", "rouge": "détresse vitale",
                     "jaune": "urgence relative", "vert": "urgence mineure"}[couleur]
            return {"score": score, "couleur": couleur, "libelle": label}
    return {"score": score, "couleur": "vert", "libelle": "urgence mineure"}


# ----------------------------------------------------------------- Sepsis

def qsofa(freq_resp: int, pas_systolique: int, gcs_ou_avpu: str) -> dict:
    """qSOFA (Singer et al., JAMA 2016 ; Surviving Sepsis 2021).

    gcs_ou_avpu : 'GCS<15' ou 'V/P/U' → +1.
    """
    points = sum_score([
        freq_resp >= 22,
        pas_systolique <= 100,
        gcs_ou_avpu.upper() in ("GCS<15", "V", "P", "U"),
    ])
    return {"score": points,
            "risque": "élevé (mortalité ≥10 %)" if points >= 2 else "faible",
            "action": "évaluer SOFA + lactates" if points >= 2
                      else "surveillance standard"}


def sofa(respiration_pa02_fio2: int, plaquettes_kul: int,
         map_mmhg_ou_vasopresseurs: str, gcs: int,
         bilirubine_mgdl: float, creatinine_mgdl: float) -> dict:
    """SOFA complet (Vincent et al. 1996, mise à jour SCCM 2021).

    map_mmhg_ou_vasopresseurs : 'MAP<70' | 'dopa≤5' | 'dopa>5/épi≤0.1' | 'dopa>15/épi>0.1'
    """
    grid_resp = [(100, 400), (200, 300), (300, 0), (400, 0)]
    p_f = respiration_pa02_fio2
    s = 0
    if p_f < 400:
        for lo, hi in grid_resp:
            if p_f < hi or hi == 0 and p_f < lo:
                s = max(s, grid_resp.index((lo, hi)) + 1)
    s_plaq = 4 if plaquettes_kul < 20 else 3 if plaquettes_kul < 50 else \
        2 if plaquettes_kul < 100 else 1 if plaquettes_kul < 150 else 0
    s_cv = {"normal": 0, "MAP<70": 1, "dopa≤5": 2, "dopa>5/épi≤0.1": 3,
            "dopa>15/épi>0.1": 4}.get(map_mmhg_ou_vasopresseurs, 0)
    s_gcs = 4 if gcs < 6 else 3 if gcs < 10 else 2 if gcs < 13 else 1 if gcs < 15 else 0
    s_bili = 4 if bilirubine_mgdl >= 12 else 3 if bilirubine_mgdl >= 6 else \
        2 if bilirubine_mgdl >= 2 else 1 if bilirubine_mgdl >= 1.2 else 0
    s_crea = 4 if creatinine_mgdl >= 5 else 3 if creatinine_mgdl >= 3.5 else \
        2 if creatinine_mgdl >= 2 else 1 if creatinine_mgdl >= 1.2 else 0
    total = max(s, 0) + s_plaq + s_cv + s_gcs + s_bili + s_crea
    return {"score": total,
            "gravite": grade(total, [(5, "faible"), (9, "modérée"), (24, "sévère")]),
            "mortalite_estimee": f"~{min(95, total * 8 + 5)} %"}


def news2(freq_resp: int, spo2: int, o2_supplementaire: bool,
          pas: int, pouls: int, conscience: str, temperature: float) -> dict:
    """National Early Warning Score 2 (RCP, 2017) — détection précoce détérioration."""
    fr = 3 if freq_resp <= 8 else 2 if freq_resp == 9 else 1 if freq_resp in (10, 11) \
        else 0 if freq_resp in (12, 13, 14, 15, 16, 17, 18, 19, 20) \
        else 2 if freq_resp in (21, 22, 23) else 3
    sats = 3 if spo2 <= 91 else 2 if spo2 in (92, 93) else 1 if spo2 in (94, 95) else 0
    temp = 3 if temperature <= 35.0 else 1 if temperature <= 36.0 else 0 \
        if temperature <= 38.0 else 1 if temperature <= 39.0 else 2
    pas_s = 3 if pas <= 90 else 2 if pas in (91, 92, 93, 94, 95, 96, 97, 98, 99) \
        else 1 if pas <= 109 else 2 if pas <= 219 else 3
    pouls_s = 3 if pouls <= 40 else 1 if pouls <= 50 else 0 if pouls <= 90 \
        else 1 if pouls <= 110 else 2 if pouls <= 130 else 3
    conc = {"alerte": 0, "V": 3, "P": 3, "U": 3}.get(conscience, 3 if conscience != "alerte" else 0)
    total = fr + sats + (2 if o2_supplementaire else 0) + pas_s + pouls_s + conc + temp
    return {"score": total,
            "niveau": grade(total, [(4, "faible — observation 12 h"),
                                    (6, "clé — revue clinique urgente"),
                                    (24, "émergent — évaluation continue")])}
