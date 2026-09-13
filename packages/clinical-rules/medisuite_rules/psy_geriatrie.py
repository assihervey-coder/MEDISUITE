"""Psychiatrie & gériatrie : PHQ-9, GAD-7, C-SSRS, Fried, TUG, Braden, Barthel, MNA.

Référentiels : PHQ-9 (Kroenke 2001), GAD-7 (Spitzer 2006), C-SSRS (Posner 2011),
AUDIT-C (Bush 1998), Fried frailty (2001), Clinical Frailty Scale (Rockwood 2005),
Timed Up & Go (Podsiadlo 1991), Braden 1987, Barthel (Mahoney 1965), MNA-SF
(Vellas 1999), critères de Beers 2023 (subset), STOPP/START v3 2023 (subset).
"""
from __future__ import annotations

from .scores import grade, sum_score


def phq9(scores_items: list[int]) -> dict:
    """PHQ-9 (Kroenke et al., J Gen Intern Med 2001) — 9 items 0-3 = 27 max."""
    if len(scores_items) != 9 or any(not 0 <= s <= 3 for s in scores_items):
        raise ValueError("PHQ-9 : 9 items de 0 à 3")
    total = sum(scores_items)
    return {"score": total,
            "severite": grade(total, [(4, "minimale"), (9, "légère"),
                                      (14, "modérée"), (19, "modérément sévère"),
                                      (27, "sévère")]),
            "item9_positif": scores_items[8] >= 1}


def gad7(scores_items: list[int]) -> dict:
    """GAD-7 (Spitzer et al., Arch Intern Med 2006) — 7 items 0-3 = 21 max."""
    if len(scores_items) != 7 or any(not 0 <= s <= 3 for s in scores_items):
        raise ValueError("GAD-7 : 7 items de 0 à 3")
    total = sum(scores_items)
    return {"score": total,
            "severite": grade(total, [(4, "minimale"), (9, "légère"),
                                      (14, "modérée"), (21, "sévère")])}


def cssrs_risk(ideation_passive: bool, ideation_active: bool,
               intention: bool, plan: bool, tentative_antecedente: bool) -> dict:
    """C-SSRS screening version (Posner et al., Am J Psychiatry 2011) —
    idée passive → surveillance ; intention/plan → évaluation psychiatrique urgente."""
    if intention or plan:
        return {"niveau": 5 if plan else 4,
                "conduite": "URGENCE — évaluation psychiatrique immédiate, 1:1"}
    if ideation_active:
        return {"niveau": 3, "conduite": "évaluation psychiatrique sous 24 h"}
    if ideation_passive:
        return {"niveau": 2, "conduite": "entretien ciblé + suivi rapproché"}
    return {"niveau": 1, "conduite": "pas de risque détecté"}


def audit_c(nb_jours_boisson_semaine: int, verres_jour_type: int,
            episodes_6verres: int) -> dict:
    """AUDIT-C (Bush et al. 1998) — dépistage consommation d'alcool risquée."""
    items = [min(nb_jours_boisson_semaine, 4), min(verres_jour_type, 4),
             min(episodes_6verres, 4)]
    total = sum(items)
    return {"score": total,
            "positif": total >= (3 if True else 4) and total >= 3,  # seuil F: ≥3, H: ≥4
            "note": "seuil recommandé ≥3 (femmes) / ≥4 (hommes)"}


def fried(fatigue_epuisee: bool, perte_poids_recente: bool,
          faible_prise_force: bool, marche_lente: bool,
          activite_physique_basse: bool) -> dict:
    """Phénotype de fragilité de Fried (J Gerontol 2001) — 3/5 critères = fragile."""
    n = sum_score([fatigue_epuisee, perte_poids_recente, faible_prise_force,
                   marche_lente, activite_physique_basse])
    return {"critères": n,
            "phenotype": "fragile" if n >= 3 else "pré-fragile" if n >= 1
            else "robuste"}


def timed_up_and_go(secondes: float, marche_canne: bool = False) -> dict:
    """Timed Up & Go (Podsiadlo & Richardson 1991) — risque de chute."""
    ajuste = secondes + (2 if marche_canne else 0)
    return {"secondes": secondes,
            "risque_chute": grade(ajuste, [(10, "faible"), (19, "modéré"),
                                           (999, "élevé (>20 s : chute probable)")])}


def braden(perception: int, humidite: int, activite: int, mobilite: int,
           nutrition: int, frottement: int) -> dict:
    """Échelle de Braden (Bergstrom 1987) — risque d'escarre (6 items 1-4)."""
    items = [perception, humidite, activite, mobilite, nutrition, frottement]
    if any(not 1 <= v <= 4 for v in items):
        raise ValueError("Braden : chaque item 1-4")
    total = sum(items)
    return {"score": total,
            "risque": grade(total, [(9, "très élevé"), (12, "élevé"),
                                    (14, "modéré"), (18, "faible"), (23, "minimal")]),
            "prevention_matelas": total <= 14}


def barthel(items: dict[str, int]) -> dict:
    """Indice de Barthel (Mahoney & Barthel 1965) — dépendance ADL (0-100)."""
    attendus = {"alimentation", "transfert_lit_chaise", "toilette", "toilettes",
                "bain", "deplacement", "escaliers", "habillage", "controle_selles",
                "controle_urinaire"}
    manquants = attendus - set(items)
    if manquants:
        raise ValueError(f"items Barthel manquants : {sorted(manquants)}")
    total = sum(items.values())
    return {"score": total,
            "dependance": grade(100 - total, [(0, "indépendant"), (24, "légère"),
                                              (49, "modérée"), (74, "sévère"),
                                              (100, "totale")])}


def mna_sf(declin_repas: bool, perte_poids: bool, mobilite_reduite: bool,
           stress_maladie: bool, neuropsychologique: bool, imc_value: float) -> dict:
    """MNA-SF (Vellas et al. 1999) — dépistage malnutrition sujet âgé."""
    score = sum_score([declin_repas, perte_poids, mobilite_reduite,
                       stress_maladie, neuropsychologique], weights=[2, 3, 2, 3, 2])
    score += 3 if imc_value >= 23 else 2 if imc_value >= 22 else 1 if imc_value >= 21 else 0
    return {"score": score,
            "statut": grade(score, [(7, "malnutri"), (11, "risque de malnutrition"),
                                    (14, "normal")])}


def beers_risky_medicaments(medicaments: list[str]) -> dict:
    """Critères de Beers 2023 — subset des médicaments à éviter chez 65+."""
    liste = {"diazépam", "lorazépam", "alprazolam", "zolpidem", "amitriptyline",
             "fluoxétine", "ibuprofène", "kétoprofène", "diclofénac", "ranitidine",
             "hydroxyzine", "prométhazine", "glycopyrrolate", "chlorpromazine"}
    trouves = [m for m in medicaments if m.lower() in liste]
    return {"a_eviter": trouves, "charge": len(trouves),
            "conduite": "déprescription progressive (STOPP-START v3)" if trouves
            else "conforme Beers 2023"}
