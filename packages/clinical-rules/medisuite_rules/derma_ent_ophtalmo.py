"""Dermatologie, ORL & ophtalmologie : mélanome, PASI, audiogramme, Lund-Mackay, DR.

Référentiels : ABCDE & 7-point checklist (Argenziano 1998), Breslow (staging),
PASI (Fredriksson & Pettersson 1978), SCORAD (European Task Force 1993),
PTA audiométrique (WHO 2021 grades), Lund-Mackay 1984, ICDR-SS (DR grading),
cup/disc ratio (ISNT / OHTS).
"""
from __future__ import annotations

from .scores import grade, sum_score


def abcde(asymetrie: bool, bord_irregulier: bool, couleur_multipe: bool,
          diametre_mm: float, evolution: bool) -> dict:
    """Règle ABCDE du mélanome — signes d'alerte dermoscopique."""
    alertes = sum_score([asymetrie, bord_irregulier, couleur_multipe,
                         diametre_mm > 6, evolution])
    return {"alertes": alertes,
            "conduite": "dermoscopie + biopsie d'exérèse" if alertes >= 2
            else "photographie de surveillance" if alertes == 1 else "réassurance"}


def checklist_7points(points: int) -> dict:
    """7-point checklist (Argenziano et al. 1998) — seuil 3 → excision."""
    return {"points": points,
            "conduite": "excision recommandée" if points >= 3 else "surveillance"}


def breslow_stage(epaisseur_mm: float, ulceration: bool) -> dict:
    """Stade de Breslow (AJCC 8e éd.) — épaisseur d'invasion du mélanome."""
    stage = grade(epaisseur_mm, [(1.0, "T1"), (2.0, "T2"), (4.0, "T3"), (99, "T4")])
    plus = "a" if not ulceration else "b"
    return {"stade_t": f"{stage}{plus}", "ulceration": ulceration,
            "ganglion_sentinelle_discutee": epaisseur_mm >= 1.0}


def pasi(erytheme: int, infiltration: int, desquamation: int,
         surface_pcts: list[int]) -> dict:
    """PASI (Fredriksson & Pettersson 1978) — 4 régions (tête, tronc, bras, jambes).

    surface_pcts : surface atteinte par région (0-100) ;
    gravité clinique par item 0-4 (x1 tête, x2 tronc, x3 bras, x4 jambes)."""
    if len(surface_pcts) != 4:
        raise ValueError("4 régions requises")
    zones = [(0.1, surface_pcts[0]), (0.2, surface_pcts[1]),
             (0.3, surface_pcts[2]), (0.4, surface_pcts[3])]
    total = 0.0
    for poids, surface in zones:
        area_factor = 0 if surface == 0 else 1 if surface < 10 else 2 if surface < 30 \
            else 3 if surface < 50 else 4 if surface < 70 else 5 if surface < 90 else 6
        total += poids * (erytheme + infiltration + desquamation) * area_factor
    total = round(total, 1)
    return {"pasi": total,
            "severite": grade(total, [(4.9, "légère"), (9.9, "modérée"),
                                      (19.9, "sévère"), (72, "très sévère")]),
            "traitement_systemique": total >= 10}


def scorad(surface_pct: int, prurit_0_10: int, erytheme: int, oedema: int,
           croutes: int, lichenification: int, secheresse: int,
           insomnie_0_10: int = 0) -> dict:
    """SCORAD (European Task Force on Atopic Dermatitis 1993).

    A = surface/2 ; B = intensité (prurit + insomnie) ; C = signes cutanés
    (érythème, œdème, croûtes, lichenification) ×3.5 ; sécheresse notée à part."""
    a = surface_pct / 2
    b = prurit_0_10 + insomnie_0_10
    c = (erytheme + oedema + croutes + lichenification) * 3.5
    score = round(a + b + c, 1)
    return {"scorad": score,
            "severite": grade(score, [(24, "légère"), (49, "modérée"), (104, "sévère")])}


def pta_audiogramme(seuils_db_4freq: dict[str, float]) -> dict:
    """Seuil tonal moyen PTA 500/1k/2k/4k Hz (WHO 2021 grades) par oreille."""
    freqs = ["500", "1000", "2000", "4000"]
    pta = round(sum(seuils_db_4freq[f] for f in freqs) / 4, 1)
    return {"pta_db": pta,
            "grade_oms": grade(pta, [(20, "normal"), (35, "perte légère"),
                                     (50, "perte modérée"), (65, "perte modérément sévère"),
                                     (80, "perte sévère"), (999, "cophose")])}


def lund_mackay(scores_sinusiens: dict[str, int]) -> dict:
    """Score de Lund-Mackay (1984) — TDM sinusites chroniques (0-24).

    Par sinus (maxillaire x2, antérieur x2, postérieur x2, sphénoïde x2,
    frontal x2) : 0 clair, 1 partiel, 2 opacité ; ostium : 0/2 ; cellules : 0-2."""
    attendus = {"maxillaire_d", "maxillaire_g", "ethmoide_ant_d", "ethmoide_ant_g",
                "ethmoide_post_d", "ethmoide_post_g", "sphenoid_d", "sphenoid_g",
                "frontal_d", "frontal_g", "ostium_d", "ostium_g", "cells"}
    total = sum(scores_sinusiens.values())
    manquants = attendus - set(scores_sinusiens)
    return {"score": total,
            "manquants": sorted(manquants) if manquants else [],
            "chirurgie_endoscopique_discutee": total >= 12}


def bppv_interpretation(hallpike_droit: bool, hallpike_gauche: bool,
                        vertige_latence: bool, fatigue: bool) -> dict:
    """Interprétation Dix-Hallpike — canalithiasis (BPPV) du canal postérieur."""
    if (hallpike_droit or hallpike_gauche) and vertige_latence and fatigue:
        cote = "droit" if hallpike_droit else "gauche"
        return {"bppv": True, "cote": cote,
                "traitement": f"manœuvre d'Epley à droite {'droite' if cote == 'droit' else 'gauche'}"}
    return {"bppv": False,
            "pistes": ["vertige vestibulaire central à éliminer", "Menière", "neuropathie"]}


def glaucome_cdr(ratio_c_d: float, pio_mmhg: int) -> dict:
    """Risque glaucome (OHTS 2002 / ISNT) — cup/disc + PIO."""
    risque = grade(ratio_c_d, [(0.3, "normal"), (0.5, "à surveiller"),
                               (0.7, "suspect"), (1.0, "très suspect")])
    pio = grade(pio_mmhg, [(21, "PIO normale"), (30, "PIO élevée"), (99, "PIO très élevée")])
    return {"ratio": ratio_c_d, "risque_cup": risque, "pio": pio,
            "champ_visuel": "requis" if ratio_c_d >= 0.5 or pio_mmhg > 21 else "annuel"}


def retinopathie_diabetique(microanévrismes: bool, hémorragies_veineuses: bool,
                            exsudats_mous: bool, hémorragies_intrarétiniennes: bool,
                            neovaisseaux: bool, hemorragie_vitree: bool,
                            oedeme_maculaire: bool) -> dict:
    """ICDR-SS (Wilkinson 2003) — grading rétinopathie diabétique."""
    if neovaisseaux or hemorragie_vitree:
        stage = "proliférative"
    elif hémorragies_intrarétiniennes or exsudats_mous:
        stage = "pré-proliférative sévère"
    elif microanévrismes or hémorragies_veineuses:
        stage = "non proliférante légère à modérée"
    else:
        stage = "absente"
    return {"stade_icdr": stage, "oedeme_maculaire": oedeme_maculaire,
            "traitement_anti_vegf": oedeme_maculaire or neovaisseaux,
            "suivi_mois": 3 if neovaisseaux or oedeme_maculaire else 12}
