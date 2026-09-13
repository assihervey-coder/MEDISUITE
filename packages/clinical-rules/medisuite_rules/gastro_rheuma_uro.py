"""Gastro-entéro, rhumatologie & urologie : MICI, hépatologie, DAS28, IPSS, Gleason.

Référentiels : Mayo endoscopic subscore (UC), Forrest 1974, Los Angeles (GERD),
Child-Pugh 1964/72, MELD (Malinchoc 2000), DAS28-ESR (Prevoo 1995), BASDAI,
SLEDAI-2K (Gladman 2000), Kellgren-Lawrence 1957, IPSS (Barry 1992),
Gleason grade groups (ISUP 2014), RENAL nephrometry (Kutikov 2009),
PI-RADS v2.1 (ACR 2019).
"""
from __future__ import annotations

from .scores import grade, sum_score


def mayo_endoscopic(mucosa: str) -> dict:
    """Mayo endoscopic subscore (colite ulcéreuse) : normal → sévère."""
    mapping = {"normale": 0, "erytheme_diminue_vascularisation": 1,
               "erytheme_absence_vascularisation_erosions": 2, "ulcerations_spontanees": 3}
    n = mapping.get(mucosa, 0)
    return {"stade": n, "reponse_mucosaire": "rémission" if n == 0
            else "réponse partielle" if n <= 2 else "activité sévère"}


def forrest(clot_state: str) -> dict:
    """Classification de Forrest (1974) — risque de resaignement ulcère."""
    taux = {"Ia": 90, "Ib": 50, "IIa": 43, "IIb": 34, "IIc": 5, "III": 5}
    r = taux.get(clot_state)
    if r is None:
        raise ValueError(f"stade Forrest inconnu : {clot_state}")
    return {"stade": forrest.__name__, "classe": clot_state,
            "rebleeding_pct": r, "traitement": "protocole adrénaline+coagulation"
            if r >= 40 else "PPI haute dose + surveillance"}


def la_gerd(congestion_grade: str) -> dict:
    """Classification de Los Angeles (1999) — œsophagite peptique A-D."""
    n = {"A": 1, "B": 2, "C": 3, "D": 4}.get(congestion_grade, 0)
    return {"grade": congestion_grade or "aucune", "niveau": n,
            "ipp_double_dose": n >= 3}


def child_pugh(bilirubine_mgdl: float, albumine_gdl: float,
               inr: float, ascite: str, encephalopathie: str) -> dict:
    """Child-Pugh (1964/1972) — pronostic hépatique A/B/C."""
    p_bili = 1 if bilirubine_mgdl < 2 else 2 if bilirubine_mgdl < 3 else 3
    p_alb = 1 if albumine_gdl > 3.5 else 2 if albumine_gdl >= 2.8 else 3
    p_inr = 1 if inr < 1.7 else 2 if inr <= 2.3 else 3
    p_asc = {"aucune": 1, "légère": 2, "réfractaire": 3}.get(ascite, 1)
    p_enc = {"aucune": 1, "grade_1_2": 2, "grade_3_4": 3}.get(encephalopathie, 1)
    total = p_bili + p_alb + p_inr + p_asc + p_enc
    return {"score": total,
            "classe": grade(total, [(6, "A (bien compensée)"), (9, "B (décompensation)"),
                                    (15, "C (sévère)")]),
            "transplantation_discutee": total >= 10}


def meld(bilirubine_mgdl: float, creatinine_mgdl: float, inr: float,
         sodium_mmol_l: float, dialyse: bool) -> dict:
    """MELD-Na (2016, OPTN) — priorité greffe hépatique."""
    import math
    cr = creatinine_mgdl if not dialyse else 3.0
    meld = (6 + 4.2 * math.log(max(bilirubine_mgdl, 1))
            + 11.2 * math.log(max(inr, 1)) + 9.57 * math.log(max(cr, 1)))
    na = min(max(sodium_mmol_l, 125), 137)
    meld_na = meld + 1.32 * (137 - na) - 0.033 * meld * (137 - na)
    val = round(min(max(meld_na, 6), 40), 1)
    return {"meld_na": val, "mortalite_3m_pct": f"~{round(val * 1.9)} %",
            "priorite_greffe": val >= 20}


def das28(tender_count: int, swollen_count: int, vsr_mm_h: float,
          santé_globale_0_100: float) -> dict:
    """DAS28-ESR (Prevoo et al., Arthritis Rheum 1995) — activité polyarthrite."""
    import math
    das = (0.56 * math.sqrt(math.sqrt(tender_count))
           + 0.28 * math.sqrt(math.sqrt(swollen_count))
           + 0.70 * math.log(vsr_mm_h) + 0.014 * santé_globale_0_100)
    val = round(das, 2)
    return {"das28": val,
            "activite": grade(val, [(2.6, "rémission"), (3.2, "faible"),
                                    (5.1, "modérée"), (10, "élevée")]),
            "biotherapie_indiquee": val > 5.1}


def basdai(fatigue: int, douleur_cervicale_dos: int, douleur_peripherique: int,
           douleur_sensibilite: int, raideur_matinale_intensite: int,
           raideur_matinale_duree_h: float) -> dict:
    """BASDAI (Garrett et al. 1994) — activité spondyloarthrite axiale."""
    duree_score = min(raideur_matinale_duree_h / 2, 10)
    total = (fatigue + douleur_cervicale_dos + douleur_peripherique
             + douleur_sensibilite + raideur_matinale_intensite + duree_score) / 6
    val = round(total, 1)
    return {"basdai": val,
            "activite": "élevée" if val >= 4 else "faible",
            "biotherapie_indiquee": val >= 4}


def sledaik(criteres: dict[str, bool]) -> dict:
    """SLEDAI-2K (Gladman et al. 2000) — subset des 24 descripteurs.
    Pondérations : atteintes majeures ×8, mineures ×1-2."""
    poids = {"crise_convulsive": 8, "psychose": 8, "syndrome_organique": 8,
             "atteinte_visuelle": 8, "nevrite_crânienne": 8, "vasculite": 8,
             "lupus_cephalique": 2, "protéinurie": 4, "pyurie": 1,
             "eruption_cutanee": 2, "alopécie": 1, "ulcérations_mucus": 2,
             "pleurésie": 2, "péricardite": 2, "faible_complément": 2,
             "anti_dnab": 2, "arthrite": 2, "leucopénie": 1, "thrombopénie": 1}
    total = sum(poids[k] for k, v in criteres.items() if v and k in poids)
    return {"sledai": total,
            "activite": grade(total, [(5, "faible"), (9, "modérée"),
                                      (19, "élevée"), (105, "très élevée")])}


def kellgren_lawrence(pincement: bool, osteophytes: str, sclerosis: bool,
                      deformite: bool) -> dict:
    """Kellgren & Lawrence (1957) — gonarthrose radiologique 0-IV."""
    stage = 0
    if osteophytes == "douteux":
        stage = 1
    elif osteophytes == "net" and pincement:
        stage = 2
    elif osteophytes == "net" and pincement and sclerosis:
        stage = 3
    if deformite:
        stage = 4
    return {"grade": stage,
            "prothese_discutee": stage >= 4,
            "traitement": ["surveillance", "surveillance", "PT + antalgiques",
                           "infiltrations ± chirurgie", "arthroplastie"][stage]}


def ipss(frequence_nocturne: int, frequence_2h: int, retenue: int,
         jets_faibles: int, straining: int, incomplets: int) -> dict:
    """IPSS (Barry et al., Br J Urol 1992) — symptômes prostatiques 0-35."""
    items = [frequence_nocturne, frequence_2h, retenue, jets_faibles,
             straining, incomplets]
    total = sum(min(i, 5) for i in items)
    return {"score": total,
            "gravite": grade(total, [(7, "légère"), (19, "modérée"), (35, "sévère")]),
            "traitement": ["surveillance", "alpha-bloquant",
                           "alpha-bloquant ± 5-ARI", "chirurgie discutée"]
            [min(total // 8, 3)]}


def gleason_grade_group(primaire: int, secondaire: int) -> dict:
    """Grade Groups ISUP 2014 — pronostic cancer prostate.

    GG1=3+3 · GG2=3+4 · GG3=4+3 · GG4=8 · GG5=9-10."""
    somme = primaire + secondaire
    if (primaire, secondaire) == (3, 3):
        gg = 1
    elif (primaire, secondaire) == (3, 4):
        gg = 2
    elif (primaire, secondaire) == (4, 3):
        gg = 3
    elif somme == 8:
        gg = 4
    else:
        gg = 5
    return {"grade_group": gg, "gleason": f"{primaire}+{secondaire}={somme}",
            "pronostic": ["excellent", "bon", "intermédiaire", "défavorable",
                          "mauvais"][gg - 1]}


def renal_nephrometry(ray_cm: float, endophytique_pct: int, near_urothelium: str,
                      anterieur_posterieur: str, polar: str) -> dict:
    """Score RENAL (Kutikov & Uzzo, J Urol 2009) — complexité néphrectomie partielle."""
    r = 1 if ray_cm <= 2 else 2 if ray_cm < 4 else 3
    e = 1 if endophytique_pct < 50 else 2 if endophytique_pct >= 50 else 3
    n = {"x": 1, "≤4mm": 1, "4-7mm": 2, "≥7mm": 3}.get(near_urothelium, 1)
    a = {"a/x": 1, "a": 1, "p": 2, "x": 1}.get(anterieur_posterieur, 1)
    l = {"1": 1, "2": 2, "3": 3}.get(polar, 1)
    total = r + e + n + a + l
    return {"score": total,
            "complexite": grade(total, [(6, "faible"), (9, "modérée"), (12, "élevée")]),
            "nephrectomie_partielle": total <= 9}


def pirads_lesions(lesions: list[dict]) -> dict:
    """PI-RADS v2.1 (ACR 2019) — score max des lésions T2/ADC/DWI.
    lesion = {'zone': 'transitionnelle|périphérique', 't2': 1-5, 'dw': 1-5}"""
    if not lesions:
        return {"pirads": 1, "biopsie": False}
    best = 1
    for l in lesions:
        score = l.get("dw", 1) if l.get("zone") == "périphérique" \
            else max(l.get("t2", 1), l.get("dw", 1))
        best = max(best, score)
    return {"pirads": best,
            "biopsie_ciblee": best >= 4,
            "probabilite_cancer": ["très faible", "faible", "intermédiaire",
                                   "élevée", "très élevée"][best - 1]}
