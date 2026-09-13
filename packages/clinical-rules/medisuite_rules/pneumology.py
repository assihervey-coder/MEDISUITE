"""Pneumologie : BPCO, spirométrie, apnées du sommeil, dépistage TB (endémie forte).

Référentiels : GOLD 2024 (BPCO), ATS/ERS 2019 & GINA 2024 (spirométrie/asthme),
AASM (AHI), critères OMS de dépistage tuberculose 2013 — pertinents en Côte d'Ivoire
(co-infection VIH/TB : ~40 % des cas TB).
"""
from __future__ import annotations

from .scores import grade, sum_score


def spirometry_interpretation(fev1_l: float, fvc_l: float,
                              fev1_theo_pct: float) -> dict:
    """Interprétation spirométrique ATS/ERS 2019 :
    obstruction si VEMS/CVG < 0.70 (corrigé âge en pédiatrie, hors périmètre v0.1)."""
    ratio = fev1_l / fvc_l if fvc_l > 0 else 0
    obstruction = ratio < 0.70
    restriction = (not obstruction) and fvc_l < 0.8 * 4.0  # CVF théorique ~4 L moyen adulte
    gravite = grade(100 - fev1_theo_pct, [(0, "normale"), (30, "légère"),
                                          (50, "modérée"), (80, "sévère"),
                                          (100, "très sévère")]) if obstruction else "n/a"
    return {"ratio_tiffeneau": round(ratio, 2),
            "pattern": "obstructif" if obstruction else
                       "restrictif possible" if restriction else "normal",
            "gravite_obstruction": gravite,
            "reversibilite_a_tester": obstruction}


def gold_group(mmc_pct: int, dyspnee_mrc: int, exacerbations_12m: int,
               hospitalisation_exacerbation: bool) -> dict:
    """GOLD 2024 — classification ABE et gravité spirométrique.

    mmc_pct : tolérance à l'exercice (mMRC transposé 0-100) ;
    dyspnee_mrc : 0-4 (échelle mMRC)."""
    spirometric = grade(100 - mmc_pct, [(30, "GOLD 1 (léger)"), (50, "GOLD 2 (modéré)"),
                                        (80, "GOLD 3 (sévère)"), (100, "GOLD 4 (très sévère)")])
    if hospitalisation_exacerbation or exacerbations_12m >= 2:
        groupe = "E"
    elif dyspnee_mrc >= 2:
        groupe = "B"
    else:
        groupe = "A"
    return {"groupe": groupe, "spirometrie": spirometric,
            "traitement_initial": {"A": "bronchodilatateur", "B": "LABA+LAMA",
                                    "E": "LABA+LAMA±CDI"}[groupe]}


def ahi_severity(ahi: int) -> dict:
    """Index apnée-hypopnée (AASM 2017) : normal <5, léger <15, modéré <30, sévère ≥30."""
    return {"ahi": ahi, "gravite": grade(ahi, [(4, "normale"), (14, "SAOS léger"),
                                               (29, "SAOS modéré"), (999, "SAOS sévère")])}


def stop_bang(snorring: bool, fatigue: bool, apnee_obseree: bool,
              pression_arterielle_haute: bool, imc_over_35: bool,
              age_over_50: bool, tour_cou_over_40cm: bool, sexe_masculin: bool) -> dict:
    """STOP-BANG (Chung et al., Anesthesiology 2008) — dépistage SAOS pré-opératoire."""
    points = sum_score([snorring, fatigue, apnee_obseree, pression_arterielle_haute,
                        imc_over_35, age_over_50, tour_cou_over_40cm, sexe_masculin])
    return {"score": points,
            "risque": "faible" if points <= 2 else "intermédiaire" if points <= 4
                      else "élevé (SAOS modéré-sévère probable)"}


def tb_who_screen(toux_2sem_plus: bool, fievre: bool, sueurs_nocturnes: bool,
                  perte_poids: bool, contact_tb: bool, vih_positif: bool) -> dict:
    """Dépistage TB — critères OMS 2013 (End TB Strategy), adaptés endémie CI.
    Tout positif chez VIH+ → interrogation systématique (WHO 2019)."""
    symptomes = [toux_2sem_plus, fievre, sueurs_nocturnes, perte_poids]
    points = sum_score(symptomes)
    suspicion = points >= 1 or contact_tb or vih_positif
    return {"symptomes_positifs": points,
            "suspicion_tb": suspicion,
            "conduite": ("GeneXpert MTB/RIF + bacilloscopie" if suspicion
                         else "aucun examen TB requis"),
            "priorite_vih": vih_positif}


def hypoxemie_severite(spo2: int, pa02_fio2: int | None = None) -> dict:
    """Classifie l'hypoxémie (spO2 ; PaO₂/FiO₂ si gazométrie : Berlin ARDS 2012)."""
    niv = grade(spo2, [(85, "sévère"), (90, "modérée"), (94, "légère"), (100, "normale")])
    ards = ""
    if pa02_fio2 is not None:
        ards = "SDRA" if pa02_fio2 <= 200 else "SDRA léger" if pa02_fio2 <= 300 else ""
    return {"niveau": niv, "sdra_berlin": ards}
