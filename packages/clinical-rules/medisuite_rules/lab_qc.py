"""Assurance qualité laboratoire : Westgard, Levey-Jennings, delta check, critiques.

Référentiels : Westgard Multi-rules (Westgard et al., Clin Chem 1981 ; clinchem
best practice 2021), Levey-Jennings, delta check (Miller, Clin Chem 2015),
valeurs critiques (collège américain de pathologie, adapté CI).
"""
from __future__ import annotations

from .scores import grade


def westgard(values: list[float], mean: float, sd: float) -> dict:
    """Règles de Westgard appliquées à une suite de contrôles QC.

    1₂ₛ avertissement · 1₃ₛ rejet · 2₂ₛ biais systématique · R₄ₛ dispersion ·
    4₁ₛ biais moyen · 10x dérive. Retourne la décision d'acceptation du run.
    """
    if not values or sd <= 0:
        raise ValueError("contrôles invalides")
    z = [(v - mean) / sd for v in values]
    rules = {
        "1_3s": any(abs(zz) > 3 for zz in z),
        "2_2s": any(abs(z[i]) > 2 and z[i] * z[i + 1] > 0 and abs(z[i + 1]) > 2
                    for i in range(len(z) - 1)) or (
            len(z) >= 2 and abs(z[-1]) > 2 and abs(z[-2]) > 2
            and z[-1] * z[-2] > 0),
        "R_4s": any(z[i] * z[i + 1] < 0 and abs(z[i] - z[i + 1]) >= 4
                    for i in range(len(z) - 1)),
        "4_1s": any(abs(z[i]) > 1 and all(abs(zz) > 1 and zz * z[i] > 0
                                          for zz in z[i:i + 4])
                    for i in range(max(0, len(z) - 4))) and len(z) >= 4,
        "10x": len(z) >= 10 and all(zz * z[-1] > 0 for zz in z[-10:]),
    }
    warning = rules["1_3s"] is False and (abs(z[-1]) > 2)
    reject = rules["1_3s"] or rules["2_2s"] or rules["R_4s"] or rules["4_1s"] or rules["10x"]
    violations = [k for k, v in rules.items() if v]
    return {"z_scores": [round(zz, 2) for zz in z],
            "violations": violations,
            "decision": "rejet du run — analyser cause" if reject
            else "avertissement 1₂ₛ — surveiller" if warning else "accepté",
            "samples_released": not reject}


def levey_jennings(value: float, mean: float, sd: float) -> dict:
    """Point Levey-Jennings : z-score et zone (±1σ, ±2σ, ±3σ)."""
    z = round((value - mean) / sd, 2) if sd else 0.0
    zone = "±1σ" if abs(z) <= 1 else "±2σ" if abs(z) <= 2 else "±3σ" if abs(z) <= 3 \
        else "hors limites"
    return {"value": value, "z": z, "zone": zone, "in_control": abs(z) <= 2}


def delta_check(value: float, previous: float, analyte: str) -> dict:
    """Delta check (Miller, Clin Chem 2015) — détection erreur pré-analytique.
    Seuils de variation relative par analyte (subsets usuels)."""
    seuils = {"hemoglobine": 20, "hematocrite": 20, "plaquettes": 50,
              "creatinine": 50, "potassium": 30, "sodium": 8, "glucose": 50,
              "hba1c": 25}
    if previous == 0:
        return {"delta_pct": None, "alerte": False,
                "note": "pas de valeur antérieure"}
    delta = abs(value - previous) / abs(previous) * 100
    seuil = seuils.get(analyte, 40)
    return {"analyte": analyte, "delta_pct": round(delta, 1),
            "seuil": seuil, "alerte": delta > seuil,
            "conduite": "vérifier échantillon (échange, hémolyse, confusions ID)"
                        if delta > seuil else "cohérent"}


# ------------------------------------------------------------ références LOINC

REFERENCE_RANGES = {
    # analyte: (LOINC, unité, bas, haut, critique_bas, critique_haut)
    "hemoglobine": ("718-7", "g/dL", 12, 16, 7, 20),
    "leucocytes": ("6690-2", "/µL", 4000, 10000, 1000, 30000),
    "plaquettes": ("777-3", "/µL", 150000, 400000, 20000, 1000000),
    "creatinine": ("2160-0", "mg/dL", 0.6, 1.3, 0.2, 5.0),
    "glucose": ("1558-6", "mg/dL", 70, 110, 40, 400),
    "potassium": ("2823-3", "mmol/L", 3.5, 5.1, 2.5, 6.5),
    "sodium": ("2951-2", "mmol/L", 135, 145, 120, 160),
    "hba1c": ("4548-4", "%", 4, 6, 0, 14),
    "crp": ("1988-5", "mg/L", 0, 5, 0, 300),
}


def analyser_resultat(analyte: str, valeur: float) -> dict:
    """Analyse complète d'un résultat : flag de référence + alerte critique.

    Retourne le statut FHIR 'normal'/'abnormal'/'critical' et l'action attendue.
    """
    ref = REFERENCE_RANGES.get(analyte)
    if not ref:
        raise ValueError(f"analyte inconnu : {analyte}")
    loinc, unite, bas, haut, cbas, chaut = ref
    if valeur < bas:
        flag = "abnormal_low"
    elif valeur > haut:
        flag = "abnormal_high"
    else:
        flag = "normal"
    critical = valeur < cbas or valeur > chaut
    return {"analyte": analyte, "loinc": loinc, "unite": unite,
            "valeur": valeur, "reference": f"{bas}-{haut} {unite}",
            "flag": flag, "critical": critical,
            "statut_fhir": "critical" if critical else
                           ("abnormal" if flag != "normal" else "normal"),
            "notification_urgente": critical}


def paludisme_tdr_positive(parasitemie_pL: int) -> dict:
    """TDR/TDR+ paludisme (OMS 2015) : densité parasitaire → sévérité."""
    return {"parasitemie": parasitemie_pL,
            "severite": grade(parasitemie_pL,
                              [(1000, "faible"), (10000, "modérée"),
                               (100000, "élevée"), (10**9, "très élevée (critère sévérité)")]),
            "traitement": "ACT + hospitalisation si critères de sévérité OMS"
                          if parasitemie_pL >= 100000 else "ACT ambulatoire"}
