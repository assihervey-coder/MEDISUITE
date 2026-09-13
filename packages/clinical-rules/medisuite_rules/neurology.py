"""Neurologie : AVC, conscience, cognition, SEP, Parkinson.

Référentiels : ASPECTS (Barber 2000), NIHSS simplifié 11 items (Lyden 2001),
MMSE (Folstein 1975), MoCA (Nasreddine 2005, seuil CI adapté), EDSS (Kurtzke),
Critères de McDonald 2017, UPDRS part III (MDS 2008).
"""
from __future__ import annotations

from .scores import grade, sum_score


def aspects(scores_regions: dict[str, int]) -> dict:
    """ASPECTS (Barber et al., Lancet 2000) — 10 régions du territoire sylvien.

    Chaque région : 1 (saine) ou 0 (ischémie). Score 10 = normal.
    Régions : caudate, insula, internal_capsule, M1..M6, lenticular.
    """
    attendues = {"caudate", "insula", "internal_capsule", "M1", "M2", "M3",
                 "M4", "M5", "M6", "lenticular"}
    if set(scores_regions) != attendues:
        raise ValueError(f"régions attendues : {sorted(attendues)}")
    score = sum(scores_regions.values())
    return {"score": score,
            "thrombectomie_candidate": score >= 6,
            "interpretation": ("ischémie étendue (<7 : dénutrition) — discussion"
                               if score < 7 else "ischémie limitée")}


def nihss(items: dict[str, int]) -> dict:
    """NIHSS simplifié (11 items, 0-38) (Lyden et al. 2001) — sévérité AVC.

    items : niveau_conscience, regard, champ_visuel, facial, moteur_bras_g/d,
    moteur_jambe_g/d, ataxie, sensoriel, langage, dysarthrie, extinction.
    """
    attendus = {"niveau_conscience", "regard", "champ_visuel", "facial",
                "moteur_bras_g", "moteur_bras_d", "moteur_jambe_g", "moteur_jambe_d",
                "ataxie", "sensoriel", "langage", "dysarthrie", "extinction"}
    manquants = attendus - set(items)
    if manquants:
        raise ValueError(f"items NIHSS manquants : {sorted(manquants)}")
    score = sum(items.values())
    return {"score": score,
            "gravite": grade(score, [(4, "mineur"), (15, "modéré"),
                                     (20, "modéré-sévère"), (42, "sévère")]),
            "thrombolyse_candidate": score >= 4}


def mmse(items: dict[str, int]) -> dict:
    """MMSE (Folstein 1975) — 30 points ; ajusté pour faible scolarité (CI :
    seuil abaissé à 23-24 selon l'étude EPIDEMCA 2012 en Afrique subsaharienne)."""
    attendus = {"orientation_temporelle", "orientation_spatiale", "memoire_immédiate",
                "attention_calcul", "rappel", "langage", "praxie_visuoconstructive"}
    score = sum(items.values())
    manquants = attendus - set(items)
    return {"score": score,
            "manquants": sorted(manquants) if manquants else [],
            "cognition": grade(score, [(10, "démence sévère"), (17, "démence modérée"),
                                       (23, "démence légère"), (27, "douteux"),
                                       (30, "normal")])}


def moca(score_brut: int, scolarite_moins_12_ans: bool) -> dict:
    """MoCA (Nasreddine 2005) — +1 point si ≤12 ans de scolarité ; cible ≥26."""
    ajuste = min(30, score_brut + (1 if scolarite_moins_12_ans else 0))
    return {"score": ajuste, "normal": ajuste >= 26,
            "atteinte_cognitive_legere": 18 <= ajuste < 26}


def edss(systemes: dict[str, int]) -> dict:
    """EDSS simplifié (Kurtzke 1983) — 7 systèmes FS 0-5(6) + marche dérivée.

    systemes : pyramidal, cerebelleux, tronc_cerebral, sensoriel, sphincter,
    visuel, cerebral (fonctions supérieures)."""
    attendus = {"pyramidal", "cerebelleux", "tronc_cerebral", "sensoriel",
                "sphincter", "visuel", "cerebral"}
    if set(systemes) != attendus:
        raise ValueError("EDSS : 7 systèmes requis")
    marche = systemes["pyramidal"] * 1.5
    score = min(10.0, sum(systemes.values()) * 0.5 + marche * 0.3)
    return {"edss": round(score, 1),
            "gravite": grade(score, [(2.4, "faible"), (4.4, "modérée"),
                                     (6.4, "sévère"), (10, "très sévère")])}


def mcdonald_ms(dissemination_espace: bool, dissemination_temps: bool,
                bande_oligoclonales: bool | None = None) -> dict:
    """Critères de McDonald 2017 — sclérose en plaques (IRM + LCR)."""
    confident = dissemination_espace and dissemination_temps
    if not confident and bande_oligoclonales:
        return {"sep": "possible (bandes oligoclonales positives, DIS seul)",
                "conduite": "IRM de suivi à 3-6 mois"}
    return {"sep": confident, "conduite": "diagnostic posé" if confident
            else "poursuivre évaluation"}


def updrs_part3_total(items_scores: list[int]) -> dict:
    """UPDRS Part III (MDS-UPDRS 2008) — somme 0-132 (33 items ×4)."""
    if any(not 0 <= s <= 4 for s in items_scores):
        raise ValueError("items UPDRS 0-4")
    total = sum(items_scores)
    return {"score": total,
            "severite": grade(total, [(15, "léger"), (30, "modéré"),
                                      (60, "sévère"), (132, "très sévère")])}
