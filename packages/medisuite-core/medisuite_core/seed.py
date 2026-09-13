"""Données de démonstration ivoiriennes : identités, structures sanitaires, tarifs.

Utilisées par le seed de chaque service. Aucune donnée réelle : générateur
déterministe (seed) pour des tests reproductibles.
"""
from __future__ import annotations

import random
from datetime import date, timedelta

NOMS = ["Kouassi", "Koné", "Traoré", "Yao", "Aka", "Bamba", "Ouattara", "Diomandé",
        "Kouamé", "N'Guessan", "Gnahoré", "Adjoua", "Amani", "Cissé", "Doumbia",
        "Sangaré", "Touré", "Séry", "Guéi", "Tanoh", "Béchio", "Gbamié", "Zadi"]
PRENOMS_M = ["Yao", "Koffi", "Konan", "Serge", "Ibrahim", "Aboubacar", "Emmanuel",
             "Sylvain", "Aristide", "Bakary", "Franck", "Didier", "Charles"]
PRENOMS_F = ["Aya", "Affoué", "Marie", "Fatoumata", "Rokia", "Adjoua", "Estelle",
             "Céline", "Salimata", "Rachelle", "Awa", "Bintou", "Kadidja"]
COMMUNES = ["Cocody", "Yopougon", "Abobo", "Adjamé", "Treichville", "Marcory",
            "Koumassi", "Port-Bouët", "Bingerville", "Songon", "Anyama"]
VILLES = ["Abidjan", "Bouaké", "Yamoussoukro", "San-Pédro", "Korhogo", "Daloa",
          "Man", "Gagnoa", "Abengourou", "Bondoukou"]
ETABLISSEMENTS = [
    ("CHU de Cocody", "CHU", "Abidjan"),
    ("CHU de Treichville", "CHU", "Abidjan"),
    ("CHU de Yopougon", "CHU", "Abidjan"),
    ("CHU de Bouaké", "CHU", "Bouaké"),
    ("Hôpital Général d'Abobo", "HGR", "Abidjan"),
    ("Hôpital Régional de Korhogo", "HGR", "Korhogo"),
    ("Centre de Santé Urbain de Daloa", "CSU", "Daloa"),
]
# Tarifs de référence (FCFA) — indicatifs, alignés sur la nomenclature CNAM
TARIFS_FCFA = {
    "consultation_generale": 3000, "consultation_specialiste": 10000,
    "radio_thorax": 8000, "echographie_abdominale": 20000, "scanner_cerebral": 60000,
    "irm_cerebrale": 150000, "nfs": 3000, "glycemie": 1500, "hba1c": 8000,
    "creatinine": 2000, "paludisme_tdr": 1500, "hemoculture": 5000,
}


def generate_patient(rng: random.Random, n: int) -> list[dict]:
    """Génère n dossiers patients synthétiques (déterministes via rng)."""
    patients = []
    for i in range(n):
        sexe = rng.choice("MF")
        nom = rng.choice(NOMS)
        prenoms = rng.choice(PRENOMS_M if sexe == "M" else PRENOMS_F)
        naissance = date(1940 + rng.randint(0, 75), rng.randint(1, 12),
                         rng.randint(1, 28))
        patients.append({
            "id": f"pat{rng.getrandbits(48):012x}",
            "numero_dossier": f"MS-2026-{1000 + i:05d}",
            "nom": nom, "prenoms": prenoms, "sexe": sexe,
            "date_naissance": naissance.isoformat(),
            "telephone": f"+225 0{rng.randint(1, 9)} {rng.randint(10, 99)} "
                         f"{rng.randint(10, 99)} {rng.randint(10, 99)} "
                         f"{rng.randint(10, 99)}",
            "ville": rng.choice(VILLES), "commune": rng.choice(COMMUNES),
            "cnam": f"CNAM-{rng.randint(100000, 999999)}",
            "groupe_sanguin": rng.choice(["A+", "A-", "B+", "B-", "O+", "O-", "AB+",
                                          "AB-"]),
        })
    return patients


def age_from(date_naissance: str, ref: date | None = None) -> int:
    d = date.fromisoformat(date_naissance)
    ref = ref or date.today()
    return ref.year - d.year - ((ref.month, ref.day) < (d.month, d.day))


def prochain_rdv(rng: random.Random, jours_max: int = 30) -> str:
    return (date.today() + timedelta(days=rng.randint(1, jours_max))).isoformat()
