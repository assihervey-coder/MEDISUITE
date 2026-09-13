"""Urgences vitales : coma, embolie, hémorragie, brûlures, pneumonie communautaire.

Référentiels : Glasgow Coma Scale (Teasdale 1974/2014), Wells 2000 (PE),
Parkland (ABLS 2018), ISS (Baker 1974, AIS-2005), CURB-65 (Lim 2003),
classification hémorragique ATLS 10e éd.
"""
from __future__ import annotations

from .scores import grade, sum_score


def gcs(ouverture_yeux: str, reponse_verbale: str, reponse_motrice: str) -> dict:
    """Glasgow Coma Scale (3-15) — grave ≤8, modérée 9-12, légère 13-15.

    ouvert: aucun|douleur|ordre|spontane ; verbal: aucun|sons|mots|confus|oriente ;
    moteur: aucun|extension|flexion|retrait|douleur_localisee|obey.
    """
    yeux = {"aucun": 1, "douleur": 2, "ordre": 3, "spontane": 4}
    verbal = {"aucun": 1, "sons": 2, "mots": 3, "confus": 4, "oriente": 5}
    moteur = {"aucun": 1, "extension": 2, "flexion": 3, "retrait": 4,
              "douleur_localisee": 5, "obey": 6}
    if (ouverture_yeux not in yeux or reponse_verbale not in verbal
            or reponse_motrice not in moteur):
        raise ValueError("composantes GCS invalides")
    total = yeux[ouverture_yeux] + verbal[reponse_verbale] + moteur[reponse_motrice]
    return {"score": total, "gravite": grade(total, [(8, "grave (intubation ≤8)"),
                                                     (12, "modérée"), (15, "légère")])}


def wells_pe(signes_tvps: bool, diagnostic_alternatif_moins_probable: bool,
             tachycardie: bool, immobilisation_ou_chirurgie: bool,
             embolie_ou_thrombose_antecedent: bool, hemoptysie: bool,
             malignite: bool) -> dict:
    """Score de Wells pour l'embolie pulmonaire (Wells et al., Ann Intern Med 2000)."""
    points = sum_score([signes_tvps, diagnostic_alternatif_moins_probable,
                        tachycardie, immobilisation_ou_chirurgie,
                        embolie_ou_thrombose_antecedent, hemoptysie, malignite],
                       weights=[3, 3, 1.5, 1.5, 1.5, 1, 1])
    niveau = ("faible (<2 %)" if points < 2 else
              "intermédiaire (~20 %)" if points <= 6 else "fort (>40 %)")
    return {"score": points, "probabilite_pretest": niveau,
            "strategie": "D-dimères" if points < 4 else "angio-CT directement"}


def parkland(poids_kg: float, pct_sbc: int, heures_depuis_brule: float) -> dict:
    """Formule de Parkland (ABLS 2018) : 4 mL × kg × %SBC sur 24 h,
    dont la moitié dans les 8 premières heures."""
    if pct_sbc < 0 or pct_sbc > 100:
        raise ValueError("SBC 0-100")
    total_24h = 4 * poids_kg * pct_sbc
    en_retard = max(0.0, (heures_depuis_brule - 8) * total_24h / 24)
    reste_16h = max(0.0, total_24h / 2 - en_retard)
    return {"total_24h_ml": round(total_24h),
            "premiere_8h_ml": round(total_24h / 2),
            "reste_16h_ml": round(reste_16h),
            "debit_actuel_ml_h": round(reste_16h / 16, 1)}


def iss(ais_regions: list[int]) -> dict:
    """Injury Severity Score (Baker 1974) : somme des carrés des 3 AIS les plus
    élevés de régions DIFFÉRENTES. >15 → polytraumatisme majeur."""
    top = sorted(ais_regions, reverse=True)[:3]
    if any(not 0 <= v <= 6 for v in ais_regions):
        raise ValueError("AIS 0-6")
    score = sum(v * v for v in top)
    return {"score": score, "majeur": score > 15,
            "mortalite_estimee": f"{min(90, max(0, round((score - 15) * 1.8)))} %"
            if score > 15 else "<1 %"}


def curbs65(confusion: bool, uree_mmol_l: float, freq_resp: int,
            pas_systolique: int, age: int) -> dict:
    """CURB-65 (Lim et al., Thorax 2003) — pneumonie communautaire, admission ?"""
    points = sum_score([confusion, uree_mmol_l > 7, freq_resp >= 30,
                        pas_systolique < 90 or pas_systolique <= 60, age >= 65])
    return {"score": points,
            "conduite": {0: "ambulatoire", 1: "ambulatoire ou courte hospitalisation",
                         2: "hospitalisation", 3: "hospitalisation, évaluer réanimation",
                         4: "réanimation probable", 5: "réanimation"}[points]}


def choc_atls(pouls: int, pas_systolique: int, freq_resp: int,
              conscience: str) -> dict:
    """Classification hémorragique I-IV (ATLS 10e éd., 2018)."""
    classe = 4
    if pas_systolique >= 100 and pouls <= 100 and freq_resp <= 14 and conscience == "alerte":
        classe = 1
    elif pas_systolique >= 90 and pouls <= 120 and freq_resp <= 20:
        classe = 2
    elif pas_systolique >= 70 and pouls <= 140 and freq_resp <= 30:
        classe = 3
    perte = ["<15 % (≈750 mL)", "15-30 % (750-1500 mL)",
             "30-40 % (1500-2000 mL)", ">40 % (>2000 mL)"][classe - 1]
    return {"classe": classe, "perte_volémique": perte,
            "transfusion_massive": classe >= 3}


def shock_index(pouls: int, pas_systolique: int) -> dict:
    """Shock Index (Allgöwer 1967) : FC/PAS > 0.9 → choc occulte (avant hypotension)."""
    if pas_systolique <= 0:
        raise ValueError("PAS invalide")
    index = round(pouls / pas_systolique, 2)
    return {"index": index, "alerte": index > 0.9,
            "interpretation": "choc occulte probable" if index > 0.9 else "stable"}
