"""Gynécologie & obstétrique : ovaire, SOPK, accouchement, CTG, pré-éclampsie.

Référentiels : IOTA Simple Rules (Timmerman 2008/2016), Rotterdam 2003 (SOPK),
O-RADS US (ACR 2020), Bishop 1964, APGAR 1952, IADPSG/ADA (DG), FIGO CTG 2015,
NICE NG134 (pré-éclampsie).
"""
from __future__ import annotations

from .scores import grade, sum_score


def iota_simple_rules(M_regles: list[str], B_regles: list[str]) -> dict:
    """IOTA Simple Rules (Timmerman et al., Lancet Oncol 2008 ; UOG 2016).

    M = règles de malignité, B = règles de bénignité. ≥1 M sans B → suspect ;
    ≥1 B sans M → bénin ; les deux / aucune → incertain (échographe expert).
    """
    if M_regles and not B_regles:
        verdict = "maligne probable"
    elif B_regles and not M_regles:
        verdict = "bénigne probable"
    elif M_regles and B_regles:
        verdict = "incertaine (règles conflictuelles)"
    else:
        verdict = "incertaine (aucune règle applicable)"
    return {"M": M_regles, "B": B_regles, "verdict": verdict,
            "conduite": ("chirurgie oncologique / référence" if verdict.startswith("maligne")
                         else "surveillance" if verdict.startswith("bénigne")
                         else "avis expert + IRM/O-RADS")}


def rotterdam_pcos(oligo_anovulation: bool, hyperandrogenie_clinique: bool,
                   hyperandrogenie_bio: bool, follicules_2_9mm_par_ovaire: int,
                   volume_ovarien_ml: float) -> dict:
    """Critères de Rotterdam 2003 — 2 critères sur 3 (après exclusion différentielles)."""
    morphologie = follicules_2_9mm_par_ovaire >= 12 or volume_ovarien_ml > 10
    criteres = sum_score([oligo_anovulation,
                          hyperandrogenie_clinique or hyperandrogenie_bio,
                          morphologie])
    return {"criteres_positifs": criteres, "sopk": criteres >= 2,
            "morphologie_sonographique": morphologie,
            "conduite": "confirmer (17-OHP, TSH, prolactine) puis prise en charge"
                        if criteres >= 2 else "chercher autre cause"}


def orads_us(leison_score: int) -> dict:
    """O-RADS US v2022 (ACR) — 0-5 selon score échographique cumulé."""
    cat = grade(leison_score, [(1, "O-RADS 1 (ovaire normal)"),
                               (3, "O-RADS 2 (presque certainement bénin)"),
                               (5, "O-RADS 3 (risque faible-intermédiaire)"),
                               (7, "O-RADS 4 (risque intermédiaire)"),
                               (999, "O-RADS 5 (risque élevé >50 %)")])
    return {"categorie": cat, "IRM_recommandee": "O-RADS 4" in cat}


def bishop(dilatation_cm: int, effacement_pct: int, station: int,
           consistance: str, position: str) -> dict:
    """Score de Bishop (1964) — maturité cervicale avant déclenchement (0-13)."""
    p = {0: 0, 1: 1, 2: 2, 3: 3}.get(min(max(dilatation_cm, 0), 3), 3)
    p += 0 if effacement_pct < 40 else 1 if effacement_pct < 60 else 2 \
        if effacement_pct < 80 else 3
    p += 0 if station < -3 else 1 if station <= -2 else 2 if station <= -1 else 3
    p += 1 if consistance == "molle" else 0
    p += 1 if position == "antérieure" else 0
    return {"score": p, "favorable": p >= 8,
            "conduite": ("déclenchement direct" if p >= 8
                         else "maturation cervicale (prostaglandines/ballonnet)")}
