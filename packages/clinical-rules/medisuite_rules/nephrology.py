"""Néphrologie : DFG, stades KDIGO, insuffisance rénale aiguë, dialyse.

Référentiels : CKD-EPI 2021 sans race (Inker et al., NEJM 2021), KDIGO 2012
(CKD) & 2012 (AKI), Cockcroft-Gault 1976, Daugirdas 2e génération (kt/V).
"""
from __future__ import annotations

from .scores import grade


def ckd_epi_2021(age: int, sexe: str, creatinine_mgdl: float) -> float:
    """DFG CKD-EPI 2021 (sans facteur race) en mL/min/1.73 m².

    sexe ∈ {'M','F'} ; formule créatinine 2021.
    """
    kappa = {"F": 0.7, "M": 0.9}[sexe]
    alpha = {"F": -0.241, "M": -0.302}[sexe]
    factor = 1.012 if sexe == "F" else 1.0
    scr = max(creatinine_mgdl, 0.01)
    term_scr = min(scr / kappa, 1.0) ** alpha if scr / kappa <= 1 \
        else (scr / kappa) ** -1.200
    value = 142 * term_scr * 0.9938 ** age * factor
    return round(value, 1)


def kdigo_ckd_stage(egfr: float, albuminurie_mg_g: int) -> dict:
    """Stade MRC KDIGO 2012 : G1-G5 × A1-A3 (risque matrice)."""
    g = grade(egfr, [(15, "G5"), (29, "G4"), (44, "G3b"), (59, "G3a"),
                     (89, "G2"), (999, "G1")])
    a = grade(albuminurie_mg_g, [(29, "A1"), (299, "A2"), (9999, "A3")])
    grid = {("G1", "A1"): "faible", ("G1", "A2"): "modérément élevé",
            ("G2", "A1"): "faible", ("G2", "A2"): "modérément élevé",
            ("G3a", "A1"): "modérément élevé", ("G3a", "A2"): "modérément élevé",
            ("G3b", "A1"): "élevé", ("G4", "A1"): "élevé", ("G5", "A1"): "très élevé"}
    risque = grid.get((g, a)) or ("élevé" if g in ("G3b", "G4")
                                  else "très élevé" if g == "G5" else "modérément élevé")
    return {"stade_gfr": g, "stade_albuminurie": a, "risque": risque,
            "nephrologue": egfr < 30 or a == "A3"}


def kdigo_aki_stage(creatinine_baseline: float, creatinine_actuelle: float,
                    diurese_ml_kg_h: float) -> dict:
    """AKI KDIGO 2012 (créatinine + diurèse) — stades 0-3."""
    ratio = creatinine_actuelle / max(creatinine_baseline, 0.01)
    stage_cr = 0 if ratio < 1.5 else 1 if ratio < 2 else 2 if ratio < 3 else 3
    stage_uo = 0 if diurese_ml_kg_h >= 0.5 else 1 if diurese_ml_kg_h >= 0.3 \
        else 2 if diurese_ml_kg_h > 0.1 else 3
    stage = max(stage_cr, stage_uo)
    return {"stade": stage, "critere_creatinine": stage_cr, "critere_diurese": stage_uo,
            "eiti_dialyse": creatinine_actuelle > 4 or stage >= 3}


def cockcroft_gault(age: int, poids_kg: float, creatinine_umol_l: float,
                    sexe: str) -> float:
    """Clairance créatinine Cockcroft-Gault (mL/min) — adaptation posologique."""
    facteur = 0.85 if sexe == "F" else 1.0
    cr = max(creatinine_umol_l / 88.4, 0.01)  # µmol/L → mg/dL
    return round((140 - age) * poids_kg * facteur / (72 * cr), 1)


def ktv_daugirdas(uree_pre_mmol_l: float, uree_post_mmol_l: float,
                  uf_total_l: float, poids_post_kg: float,
                  duree_h: float) -> dict:
    """kt/V Daugirdas 2e génération (1993) — adéquation hémodialyse (cible ≥1.2).

    kt/V = -ln(R - 0.008·t) + (4 - 3.5·R)·UF/W, R = urée_post/urée_pre.
    """
    import math
    if uree_pre_mmol_l <= 0:
        raise ValueError("urée pré-dialyse invalide")
    r = uree_post_mmol_l / uree_pre_mmol_l
    urr = 1 - r
    ktv_val = -math.log(max(r - 0.008 * duree_h, 1e-6)) \
        + (4 - 3.5 * r) * (uf_total_l / max(poids_post_kg, 1))
    return {"ktv": round(ktv_val, 2), "urr_pct": round(urr * 100, 1),
            "adequate": ktv_val >= 1.2}
