"""Cardiologie : fibrillation atriale, insuffisance cardiaque, SCA, risque CV.

Référentiels : CHA₂DS₂-VASc & HAS-BLED (ESC AF 2020/2024), NYHA, Killip-Kimball,
TIMI UA/NSTEMI (Antman 2000), HEART score (Six 2008), Framingham (Wilson 1998).
"""
from __future__ import annotations

from .scores import grade, sum_score


def chads2ds2vasc(insuffisance_cardiaque: bool, hta: bool, diabete: bool,
                  avc_ou_atcd_thrombose: bool, maladie_vasculaire: bool,
                  age: int, sexe_feminin: bool) -> dict:
    """CHA₂DS₂-VASc (Lip et al. 2010 ; ESC 2020) — indication anticoagulation FA."""
    points = sum_score([
        insuffisance_cardiaque, hta, diabete, avc_ou_atcd_thrombose,
        maladie_vasculaire, age in range(65, 75), sexe_feminin,
        age >= 75,
    ], weights=[1, 1, 1, 2, 1, 1, 1, 2])
    return {"score": points,
            "risque_avc_annuel": f"{min(15, points * 2.5):.1f} %",
            "anticoagulation": "recommandée" if points >= 2
            else "à discuter" if points == 1 else "non recommandée"}


def hasbled(hta: bool, fonction_renale_ou_hepatique_alteree: bool, avc: bool,
            saignement_antecedent: bool, inr_labile: bool, age_over_65: bool,
            medicaments_ou_alcool: bool) -> dict:
    """HAS-BLED (Pisters et al. 2010) — risque hémorragique sous AOD/AVK."""
    points = sum_score([hta, fonction_renale_ou_hepatique_alteree, avc,
                        saignement_antecedent, inr_labile, age_over_65,
                        medicaments_ou_alcool])
    return {"score": points,
            "risque_saignement": grade(points, [(1, "faible"),
                                                (2, "moyen"), (9, "élevé — prudence")])}


def nyha(classe_tolerances: str) -> dict:
    """NYHA I-IV (NYHA 1994) — limitation fonctionnelle insuffisance cardiaque.

    classe_tolerances ∈ {'aucune','effort_ordinaire','effort_faible','repos'}.
    """
    mapping = {"aucune": 1, "effort_ordinaire": 2, "effort_faible": 3, "repos": 4}
    if classe_tolerances not in mapping:
        raise ValueError(f"attendu un de {list(mapping)}")
    n = mapping[classe_tolerances]
    return {"classe": n, "libelle": f"NYHA {n}",
            "pronostic": ["favorable", "intermédiaire", "défavorable",
                          "très défavorable"][n - 1]}


def killip(congestion_pulmonaire: bool, rales_s3: bool, choc: bool) -> dict:
    """Killip-Kimball (1967) — insuffisance cardiaque post-infarctus."""
    if choc:
        n = 4
    elif rales_s3:
        n = 3
    elif congestion_pulmonaire:
        n = 2
    else:
        n = 1
    return {"classe": n, "mortalite_30j_estimee": f"~{[6, 17, 38, 81][n-1]} %"}


def timi_ua_nstemi(age_over_65: bool, facteurs_risque_cvn: int,
                   stenose_significative: bool, deviation_st: bool,
                   angine_recidive_24h: bool, aspirine_7j: bool,
                   marqueurs_necrose: bool) -> dict:
    """TIMI risk score UA/NSTEMI 0-7 (Antman et al., Circulation 2000)."""
    points = sum_score([age_over_65, facteurs_risque_cvn >= 3, stenose_significative,
                        deviation_st, angine_recidive_24h, aspirine_7j,
                        marqueurs_necrose])
    return {"score": points,
            "mortalite_ou_ischemie_14j": f"~{[5, 8, 13, 20, 26, 41][min(points, 5)]} %",
            "strategie": "invasive précoce" if points >= 4 else "conservatrice possible"}


def heart_score(anamnese: str, ecg: str, age: int, facteurs_risque: int,
                troponine: str) -> dict:
    """HEART score (Six et al., Neth Heart J 2008) — douleur thoracique aux urgences.

    anamnese ∈ {hautement_suspect, modérément, faiblement} ; ecg ∈ {ST-dév, non-spécifique, normal} ;
    troponine ∈ {x3, x2, x1, normale}.
    """
    a = {"hautement_suspect": 2, "modérément": 1, "faiblement": 0}.get(anamnese, 0)
    e = {"ST-dév": 2, "non-spécifique": 1, "normal": 0}.get(ecg, 0)
    ag = 2 if age >= 65 else 1 if age >= 45 else 0
    fr = 2 if facteurs_risque >= 3 else 1 if facteurs_risque >= 1 else 0
    t = {"x3": 2, "x2": 1, "x1": 1, "normale": 0}.get(troponine, 0)
    total = a + e + ag + fr + t
    return {"score": total,
            "mve_6sem": f"~{[2, 16, 50][min(total // 4, 2)]} %",
            "conduite": grade(total, [(3, "sortie avec suivi"),
                                       (6, "hospitalisation, tests ischémiques"),
                                       (10, "SCA probable — prise en charge invasive")])}


def framingham_10y(age: int, cholesterol_mgdl: int, hdl_mgdl: int,
                   pas: int, hta_traitee: bool, fumeur: bool,
                   diabete: bool, sexe: str) -> dict:
    """Framingham 10 ans (Wilson et al., Circulation 1998) — coefficients simplifiés
    version adulte 30-74 ans ; retourne le risque CV en %."""
    ln_age = {"M": 3.06117, "F": 2.32888}[sexe]
    ln_chol = {"M": 1.12370, "F": 1.20904}[sexe]
    ln_hdl = {"M": -0.93263, "F": -0.70833}[sexe]
    ln_pas_t = {"M": 1.93303, "F": 2.76157}[sexe]
    ln_pas_nt = {"M": 1.80993, "F": 1.79706}[sexe]
    import math
    log = math.log
    lp = (ln_age * log(age) + ln_chol * log(cholesterol_mgdl)
          + ln_hdl * log(hdl_mgdl)
          + (ln_pas_t if hta_traitee else ln_pas_nt) * log(pas)
          + (0.65451 if sexe == "M" else 0.52873) * fumeur
          + (0.57367 if sexe == "M" else 0.69154) * diabete)
    mean = {"M": 23.9802, "F": 26.1931}[sexe]
    coeff = {"M": 0.88936, "F": 0.95012}[sexe]
    risk = 1 - math.exp(-math.exp(lp - mean) * coeff)
    return {"risque_10y_pct": round(risk * 100, 1),
            "categorie": grade(risk * 100, [(4.9, "faible"), (9.9, "modéré"),
                                            (19.9, "élevé"), (100, "très élevé")])}
