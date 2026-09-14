"""Entités diagnostiques (tests et résultats)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class DiagnosticTest:
    code: str           # 'rdt_malaria', 'thick_smear', 'dengue_ns1'...
    label_fr: str
    sample: str         # sang, urines, LCR
    turnaround: str      # '15 min', '24-48 h'
    availability: str   # 'periphery' | 'hospital' | 'reference'


TESTS: dict[str, DiagnosticTest] = {
    "rdt_malaria":  DiagnosticTest("rdt_malaria", "TDR paludisme (HRP2/pLDH)", "sang", "15 min", "periphery"),
    "thick_smear":  DiagnosticTest("thick_smear", "Goutte épaisse + frottis", "sang", "4-24 h", "hospital"),
    "cbc":          DiagnosticTest("cbc", "NFS (hémoglobine, plaquettes, leucocytes)", "sang", "1-4 h", "hospital"),
    "dengue_ns1":   DiagnosticTest("dengue_ns1", "Antigène NS1 dengue", "sang", "1-2 h", "hospital"),
    "dengue_igm":   DiagnosticTest("dengue_igm", "IgM anti-dengue (MAC-ELISA)", "sang", "24-48 h", "reference"),
    "blood_culture": DiagnosticTest("blood_culture", "Hémoculture", "sang", "48-72 h", "reference"),
    "widal":        DiagnosticTest("widal", "Sérodiagnostic de Widal (sensibilité limitée)", "sang", "24 h", "hospital"),
    "crp":          DiagnosticTest("crp", "CRP", "sang", "1 h", "hospital"),
    "creatinine":   DiagnosticTest("creatinine", "Créatininémie", "sang", "1-2 h", "hospital"),
    "liver_panel":  DiagnosticTest("liver_panel", "Bilan hépatique (ASAT/ALAT, bilirubine)", "sang", "2-4 h", "hospital"),
    "lp":           DiagnosticTest("lp", "Ponction lombaire", "LCR", "2 h", "hospital"),
    "rt_pcr_vhf":   DiagnosticTest("rt_pcr_vhf", "RT-PCR fièvres hémorragiques (référence)", "sang", "24-72 h", "reference"),
    "yf_serology":  DiagnosticTest("yf_serology", "Sérologie fièvre jaune (IgM/PCR)", "sang", "48 h", "reference"),
    # V1.2 — typhoïde XDR + paludisme rénal ------------------------------------------------
    "antibiogram":  DiagnosticTest("antibiogram", "Antibiogramme (profil de résistance)", "sang", "48-72 h", "reference"),
    "urea":         DiagnosticTest("urea", "Urée sanguine", "sang", "1-2 h", "hospital"),
    "potassium":    DiagnosticTest("potassium", "Kaliémie", "sang", "1 h", "hospital"),
    "blood_gas":    DiagnosticTest("blood_gas", "Gaz du sang (pH, lactates)", "sang artériel", "30 min", "hospital"),
    # V1.3 — leptospirose + méningocoque ----------------------------------------------------
    "lepto_pcr":    DiagnosticTest("lepto_pcr", "PCR leptospirose (sang/LCR)", "sang", "24-72 h", "reference"),
    "lepto_serology": DiagnosticTest("lepto_serology", "Sérologie leptospirose (IgM ELISA/MAT)", "sang", "48 h", "reference"),
    "blood_culture_men": DiagnosticTest("blood_culture_men", "Hémoculture (suspicion IIM)", "sang", "48-72 h", "reference"),
}
