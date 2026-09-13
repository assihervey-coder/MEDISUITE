"""Oncologie : BI-RADS, Fleischner, Lung-RADS, stadification TNM, performance status.

Référentiels : BI-RADS 5e éd. (ACR 2013), Fleischner 2017 (MacMahon, Radiology),
Lung-RADS v2022, AJCC 8e éd. (sein, simplifié), ECOG PS (Oken 1982).
"""
from __future__ import annotations

from .scores import grade, sum_score


def birads(masse: bool, microcalcifications: str, asymetrie: bool,
           aire_axillaire: bool, densite_acr: str = "b") -> dict:
    """BI-RADS 5e édition (ACR 2013) — catégorisation mammographique.

    microcalcifications ∈ {'aucune','bénignes','indéterminées','suspectes'}.
    """
    score = 2
    if masse:
        score = max(score, 4)
    if microcalcifications == "suspectes":
        score = max(score, 4)
    if microcalcifications == "indéterminées":
        score = max(score, 3)
    if asymetrie:
        score = max(score, 3)
    if aire_axillaire:
        score = max(score, 4)
    conduite = {1: "contrôle annuel", 2: "contrôle annuel",
                3: "contrôle à 6 mois (probabilité bénigne >98 %)",
                4: "biopsie (probabilité malignité 2-95 %)",
                5: "biopsie (probabilité malignité >95 %)"}[score]
    return {"categorie": f"BI-RADS {score}", "conduite": conduite,
            "densite_acr": densite_acr}


def fleischner(nodule_mm: float, risque_eleve: bool, nodule_solide: bool,
               lobes_superieurs_multiple: bool = False) -> dict:
    """Fleischner Society 2017 — nodules pulmonaires solides fortuits ≥6 mm
    (patients ≥35 ans, non dépistage)."""
    if nodule_mm < 6:
        return {"conduite": "aucun suivi recommandé (<6 mm)", "delai": "n/a"}
    if nodule_solide:
        if nodule_mm < 8:
            delai_low, delai_high = "6-12 mois", "6-12 mois puis CT 18-24 mois"
        else:
            delai_low, delai_high = "3-6 mois", "3-6 mois puis CT 18-24 mois"
        return {"conduite": delai_low if not risque_eleve else delai_high,
                "delai": "CT basse dose",
                "multiples_supérieurs": lobes_superieurs_multiple}
    return {"conduite": "CT 6-12 mois (nodule sub-solide)" if nodule_mm >= 6
            else "n/a", "delai": "suivre Fleischner sub-solide"}


def lung_rads(nodule_mm: float, croissance: bool, nodules_solid_mass: bool,
              ganglions_suspects: bool) -> dict:
    """Lung-RADS v2022 (ACR) — programme de dépistage scanner faible dose."""
    if ganglions_suspects or nodule_mm >= 15:
        cat = 4
    elif croissance or (nodules_solid_mass and nodule_mm >= 8):
        cat = 3
    elif nodule_mm >= 6:
        cat = 2
    else:
        cat = 1
    conduite = {1: "dépistage annuel continu", 2: "dépistage annuel continu",
                3: "CT à 6 mois", 4: "PET-CT ± biopsie (1A <8 mm → CT 3 mois)"}[cat]
    return {"categorie": f"Lung-RADS {cat}",
            "probabilite_malignite": ["<1 %", "<1 %", "1-2 %", "5-15 %+"][cat - 1],
            "conduite": conduite}


def tnm_breast_stage(t_taille_cm: float, n_ganglionnaire: str, m_metastase: bool,
                     grade_histologique: int) -> dict:
    """AJCC 8e éd. — stade mammaire simplifié (cTNM anatomique + grade).

    n_ganglionnaire ∈ {'cN0','cN1','cN2','cN3'} ; retourne stade I-IV clinique.
    """
    if m_metastase:
        return {"stade": "IV", "conduite": "traitement systémique, discussion MDT"}
    n_factor = {"cN0": 0, "cN1": 1, "cN2": 2, "cN3": 3}[n_ganglionnaire]
    t_factor = grade(t_taille_cm, [(2, 1), (5, 2), (99, 3)])
    g_factor = min(max(grade_histologique, 1), 3)
    if n_factor >= 2 or (n_factor == 1 and t_factor >= 2):
        stade = "IIIB" if g_factor <= 2 else "IIIC"
    elif n_factor == 1 or t_factor >= 2 or g_factor == 3:
        stade = "IIA" if t_factor <= 2 and n_factor == 0 else "IIB"
    else:
        stade = "I"
    return {"stade": stade, "t_factor": f"T{t_factor}",
            "n_factor": n_ganglionnaire, "grade": f"G{g_factor}"}


def ecog(karnofsky: int | None = None, description: str = "") -> dict:
    """ECOG Performance Status (Oken 1982) avec conversion Karnofsky."""
    mapping = {100: 0, 90: 0, 80: 1, 70: 1, 60: 2, 50: 2, 40: 3, 30: 3,
               20: 4, 10: 4, 0: 5}
    ps = mapping.get(karnofsky) if karnofsky is not None else None
    if ps is None:
        ps = {"asymptomatique": 0, "symptomes_effort": 1, "symptomes_repos_partiel": 2,
              "lit_plus_moitié": 3, "alitement_total": 4}.get(description, 0)
    return {"ecog": ps, "chimio_curative_possible": ps <= 2}


def roma_score(ca125: float, he4: float, menopausee: bool) -> dict:
    """ROMA (Moore et al. 2011) — risque de malignité ovaire (CA-125 + HE4).

    Retourne une probabilité simplifiée ; seuils : 11.4 % (pré-M) / 29.9 % (post-M).
    """
    import math
    pi = (math.log(he4) * (1.0 if menopausee else 0.0)
          + math.log(ca125) * (1.0 if menopausee else 1.0))  # poids simplifiés
    prob = 1 / (1 + math.exp(-pi)) * 100
    seuil = 29.9 if menopausee else 11.4
    return {"probabilite_pct": round(prob, 1), "seuil_pct": seuil,
            "eleve": prob >= seuil}
