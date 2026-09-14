"""Médicaments — base déterministe des contraintes et interactions.

⚠️ PRINCIPE ABSOLU : aucune dose n'est JAMAIS produite par un LLM.
L'IA extrait ; le Drug Engine vérifie de façon déterministe.
Les données ci-dessous sont des CONTRAINTES de sécurité, pas des posologies
complètes — la posologie finale relève du protocole et du clinicien.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Drug:
    code: str
    label_fr: str
    drug_class: str
    contraindicated_in: dict[str, str] = field(default_factory=dict)  # maladie/état → raison
    interacts_with: list[str] = field(default_factory=list)
    pregnancy_category: str = "C"      # A/B/C/D/X (approximation prudente)
    notes: str = ""


DRUGS: dict[str, Drug] = {
    # --- Antipaludiques ---------------------------------------------------
    "artemether_lumefantrine": Drug(
        code="artemether_lumefantrine", label_fr="Artéméther-luméfantrine (CTA)",
        drug_class="ACT",
        contraindicated_in={"severe_malaria": "Forme sévère → artésunate IV requis",
                            "cardiac_arrhythmia": "Allongement QT — prudence"},
        pregnancy_category="B",
    ),
    "artesunate_iv": Drug(
        code="artesunate_iv", label_fr="Artésunate IV",
        drug_class="antipaludique sévère",
        pregnancy_category="B",
    ),
    "quinine_iv": Drug(
        code="quinine_iv", label_fr="Quinine IV",
        drug_class="antipaludique sévère",
        contraindicated_in={"cardiac_arrhythmia": "Risque de torsades"},
        notes="Grossesse : hypoglycémies fréquentes — surveiller la glycémie",
    ),
    # V1.1 — grossesse / drépanocytose --------------------------------------------------
    "primaquine": Drug(
        code="primaquine", label_fr="Primaquine",
        drug_class="8-aminoquinoléine (cure radicale P. vivax/ovale)",
        contraindicated_in={
            "pregnancy": "CONTRE-INDIQUÉE pendant toute la grossesse — hémolyse fœtale",
            "g6pd_deficiency": "Hémolyse sévère possible si déficit en G6PD",
            "infant": "CI chez le nourrisson",
        },
        pregnancy_category="X",
    ),
    "sulfadoxine_pyrimethamine": Drug(
        code="sulfadoxine_pyrimethamine", label_fr="Sulfadoxine-pyriméthamine (SP)",
        drug_class="antifolate (IPTp)",
        contraindicated_in={
            "first_trimester": "CI au 1er trimestre d'aménorrhée",
            "sulfonamide_allergy": "Allergie sulfamides",
        },
        pregnancy_category="C",
        notes="IPTp à partir du 2e trimestre en zone d'endémie — avec acide folique",
    ),
    "doxycycline": Drug(
        code="doxycycline", label_fr="Doxycycline",
        drug_class="tétracycline",
        contraindicated_in={
            "pregnancy": "CI pendant la grossesse (dyschromie dentaire fœtale)",
            "child": "CI avant 8 ans",
        },
        pregnancy_category="D",
    ),
    "mefloquine": Drug(
        code="mefloquine", label_fr="Méfloquine",
        drug_class="antipaludique (prophylaxie/traitement)",
        contraindicated_in={"psychiatric_history": "CI si antécédents neuropsychiatriques"},
        pregnancy_category="C",
        notes="Grossesse : envisageable au-delà du 1er trimestre si absence d'alternative",
    ),
    "folic_acid": Drug(
        code="folic_acid", label_fr="Acide folique",
        drug_class="supplémentation",
        pregnancy_category="A",
        notes="Drépanocytose : supplémentation chronique ; grossesse : systématique",
    ),
    "hydroxycarbamide": Drug(
        code="hydroxycarbamide", label_fr="Hydroxycarbamide (hydroxyurée)",
        drug_class="cytoréducteur (drépanocytose)",
        contraindicated_in={
            "pregnancy": "CI pendant la grossesse — cytotoxique, tératogène",
        },
        pregnancy_category="D",
        notes="Traitement de fond SCD — arrêt préalable obligatoire en cas de projet de grossesse",
    ),
    # --- Antalgiques / AINS ------------------------------------------------
    "paracetamol": Drug(
        code="paracetamol", label_fr="Paracétamol",
        drug_class="antalgique-antipyrétique",
        contraindicated_in={"hepatic_failure": "Hépatotoxicité"},
        interacts_with=["warfarin"],
        pregnancy_category="B",
    ),
    "ibuprofen": Drug(
        code="ibuprofen", label_fr="Ibuprofène",
        drug_class="AINS",
        contraindicated_in={
            "dengue": "AINS formellement déconseillés en dengue : risque hémorragique",
            "severe_dengue": "CONTRE-INDICATION — risque hémorragique majeur",
            "renal_failure": "Néphrotoxicité",
            "gastric_ulcer": "Ulcère gastrique",
            "third_trimester": "CI au 3e trimestre — fermeture prématurée du canal artériel",
            "dehydration_scd": "Drépanocytose : majoration du risque de néphropathie et de syndrome thoracique aigu",
        },
        interacts_with=["warfarin", "ace_inhibitors"],
        pregnancy_category="C",
        notes="À éviter dès le 2e trimestre de grossesse ; si indispensable, dose minimale la plus courte",
    ),
    "aspirin": Drug(
        code="aspirin", label_fr="Acide acétylsalicylique",
        drug_class="AINS/antiagrégant",
        contraindicated_in={
            "dengue": "CONTRE-INDIQUÉ en dengue suspectée : risque hémorragique",
            "severe_dengue": "CONTRE-INDICATION absolue",
            "child_viral": "Syndrome de Reye chez l'enfant avec virose",
        },
        pregnancy_category="C",
    ),
    "diclofenac": Drug(
        code="diclofenac", label_fr="Diclofénac",
        drug_class="AINS",
        contraindicated_in={"dengue": "Risque hémorragique", "severe_dengue": "CONTRE-INDICATION"},
    ),
    # --- Antibiotiques ------------------------------------------------------
    "ceftriaxone": Drug(
        code="ceftriaxone", label_fr="Ceftriaxone",
        drug_class="céphalosporine 3G",
        contraindicated_in={"jaundice_neonate": "Contre-indiqué chez le nouveau-né ictérique"},
        pregnancy_category="B",
    ),
    "azithromycin": Drug(
        code="azithromycin", label_fr="Azithromycine",
        drug_class="macrolide",
        pregnancy_category="B",
    ),
    "ciprofloxacin": Drug(
        code="ciprofloxacin", label_fr="Ciprofloxacine",
        drug_class="fluoroquinolone",
        contraindicated_in={"pregnancy": "Éviter pendant la grossesse",
                            "child": "Éviter chez l'enfant (articulations)"},
        pregnancy_category="C",
    ),
    # V1.2 — typhoïde XDR ------------------------------------------------------------
    "cefixime": Drug(
        code="cefixime", label_fr="Céfixime",
        drug_class="céphalosporine 3G orale",
        pregnancy_category="B",
        notes="Typhoïde : alternative orale en relais — inactive sur XDR documentée",
    ),
    "meropenem": Drug(
        code="meropenem", label_fr="Méropénème",
        drug_class="carbapénème IV",
        pregnancy_category="B",
        notes="Typhoïde XDR sévère : antibiotique de référence — usage hospitalier réservé",
    ),
    # V1.3 — leptospirose / méningocoque ------------------------------------------------
    "benzylpenicillin": Drug(
        code="benzylpenicillin", label_fr="Pénicilline G (benzylpénicilline)",
        drug_class="bêtalactamine IV",
        pregnancy_category="B",
        notes="Leptospirose sévère (Weil) : traitement de référence IV ; méningocoque : alternative si ceftriaxone indisponible",
    ),
    "rifampicin": Drug(
        code="rifampicin", label_fr="Rifampicine",
        drug_class="antituberculeux/protocole national",
        notes="Prophylaxie des contacts de méningocoque (protocole national MSP-CI)",
    ),
    # --- Divers ---------------------------------------------------------------
    "metoclopramide": Drug(
        code="metoclopramide", label_fr="Métoclopramide",
        drug_class="antiémétique",
        contraindicated_in={"child": "Dystonies chez l'enfant — prudence"},
        notes="Grossesse : antiémétique de référence si nécessaire",
    ),
    "vitamin_k": Drug(code="vitamin_k", label_fr="Vitamine K", drug_class="hémostatique"),
    "ringer_lactate": Drug(code="ringer_lactate", label_fr="Ringer lactate",
                           drug_class="soluté de réanimation", pregnancy_category="A"),
    "normal_saline": Drug(code="normal_saline", label_fr="Sérum salé isotonique 0,9 %",
                          drug_class="soluté", pregnancy_category="A"),
}


# Médicaments courants → code (extraction IA puis mapping déterministe)
NAME_TO_CODE: dict[str, str] = {
    "paracetamol": "paracetamol", "acetaminophen": "paracetamol", "doliprane": "paracetamol",
    "efferalgan": "paracetamol", "ibi": "ibuprofen", "ibuprofene": "ibuprofen",
    "ibuprofen": "ibuprofen", "advil": "ibuprofen", "brufen": "ibuprofen", "nurofen": "ibuprofen",
    "aspirine": "aspirin", "aspirin": "aspirin", "acide acetylsalicylique": "aspirin",
    "diclofenac": "diclofenac", "voltarene": "diclofenac",
    "ceftriaxone": "ceftriaxone", "rocephine": "ceftriaxone",
    "azithromycine": "azithromycin", "azithromycin": "azithromycin", "zithromax": "azithromycin",
    "ciprofloxacine": "ciprofloxacin", "ciprofloxacin": "ciprofloxacin", "ciflox": "ciprofloxacin",
    # V1.2 — typhoïde XDR
    "cefixime": "cefixime", "oroken": "cefixime",
    "meropenem": "meropenem", "meronem": "meropenem", "meronem iv": "meropenem",
    # V1.3 — leptospirose / méningocoque
    "penicilline g": "benzylpenicillin", "penicilline": "benzylpenicillin",
    "benzylpenicilline": "benzylpenicillin", "benzylpenicillin": "benzylpenicillin",
    "penicillin g": "benzylpenicillin", "penniciline g": "benzylpenicillin",
    "rifampicine": "rifampicin", "rifampicin": "rifampicin", "rimactan": "rifampicin",
    "artemether": "artemether_lumefantrine", "artemether lumefantrine": "artemether_lumefantrine",
    "coartem": "artemether_lumefantrine", "lonart": "artemether_lumefantrine",
    "artesunate": "artesunate_iv", "artesunate iv": "artesunate_iv",
    "quinine": "quinine_iv",
    "metoclopramide": "metoclopramide", "primperan": "metoclopramide",
    "vitamine k": "vitamin_k",
    # V1.1 — grossesse / drépanocytose
    "primaquine": "primaquine", "sulfadoxine pyrimethamine": "sulfadoxine_pyrimethamine",
    "fansidar": "sulfadoxine_pyrimethamine", "sp": "sulfadoxine_pyrimethamine",
    "doxycycline": "doxycycline", "vibramycine": "doxycycline",
    "mefloquine": "mefloquine", "lariam": "mefloquine",
    "acide folique": "folic_acid", "folique": "folic_acid", "folic acid": "folic_acid",
    "hydroxyuree": "hydroxycarbamide", "hydroxycarbamide": "hydroxycarbamide",
    "hydrea": "hydroxycarbamide",
}


def normalize_drug_name(name: str) -> str | None:
    import re
    import unicodedata

    t = unicodedata.normalize("NFKD", name.lower().strip())
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"\s+", " ", t)
    return NAME_TO_CODE.get(t)
