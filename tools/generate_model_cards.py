#!/usr/bin/env python3
"""Générateur des 26 model-cards MDR — MEDISUITE.

Chantier « model-cards formelles ×26 » (COUVERTURE-ARBRE-INITIAL §3, GAP v0.10).

Principes :
- SOURCE UNIQUE : les fiches sont DÉRIVÉES des sources de vérité du dépôt
  (datasets/registry.py, ai/multimodal/configs/*.yaml, docs/_audit_data.json)
  et d'une méta clinique embarquée (MODULE_META, alignée docs/MODULES.md) ;
- HONNÊTETÉ D'ÉTAT : métriques = 🔴 à R6-R8, données = 🟠 synthétiques,
  structure = 🟢 livrée. AUCUN chiffre de performance n'est publié avant le
  verrou de base M+18 (ADR-0026 : pas d'analyse hors verrou) ;
- DÉTERMINISME : aucune date courante, sortie triée → régénérable à
  l'identique ; mode --check pour la CI (idempotence) ;
- TRAÇABILITÉ : chaque fiche cite ses sources, ADR, risques FMEA (RM-01…RM-10),
  l'investigation MEDISUITE-CI-01 et le CER TD-11 (MEDDEV 2.7/1 rev 4).

Usage :
    python tools/generate_model_cards.py                # écrit compliance/mdr/model-cards/
    python tools/generate_model_cards.py --check        # vérifie (exit 1 si dérive)
    python tools/generate_model_cards.py --outdir /tmp  # répertoire alternatif
"""
from __future__ import annotations

import argparse
import difflib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
OUTDIR_DEFAULT = ROOT / "compliance" / "mdr" / "model-cards"
FICHE_VERSION = "1.0.0"
PLATFORM_VERSION = "v1.0.0 (cible) — jalons v0.1→v0.9 tagués"

# ---------------------------------------------------------------- sources ---

def _load_registry() -> tuple[list[tuple[int, str]], dict[str, dict]]:
    """Importe datasets/registry.py sans dépendre du CWD."""
    spec = importlib.util.spec_from_file_location(
        "medisuite_datasets_registry", ROOT / "datasets" / "registry.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod.MODULES, mod.SPEC  # type: ignore[return-value]


def _load_json(path: Path) -> Any:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _load_config(no: int, slug: str) -> dict:
    path = ROOT / "ai" / "multimodal" / "configs" / f"{no:02d}_{slug}.yaml"
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


# ------------------------------------------------- méta clinique par module ---
# Alignée sur docs/MODULES.md (périmètre) + intended-purpose.md (fonction).
# `decision` : ce que la sortie IA influence — JAMAIS un diagnostic autonome.
# `rm` : risques ISO 14971 spécifiquement accentués pour ce module
#        (socle commun : RM-01 faux négatif, RM-02 faux positif,
#         RM-03 biais d'automatisation, RM-05 dérive de modèle).

MODULE_META: dict[str, dict] = {
    "imaging": {"nom": "Imagerie — détection d'anomalies", "service": "imaging-service",
        "perimetre": "Radiographie, scanner, IRM, échographie — DICOMweb complet",
        "decision": "priorisation d'examens et orientation diagnostique ; le diagnostic final reste radiologique",
        "rm": ["RM-02", "RM-04"]},
    "laboratory": {"nom": "Laboratoire — sévérité biologique", "service": "laboratory-service",
        "perimetre": "Prescription → prélèvement → analyse → validation (Westgard) → compte-rendu",
        "decision": "triage des dossiers biologiques critiques ; la validation reste au biologiste",
        "rm": ["RM-08"]},
    "oncology": {"nom": "Oncologie — stadification tumorale", "service": "oncology-service",
        "perimetre": "Dépistage (7 organes), BI-RADS, TNM/AJCC 8e, biomarqueurs, RCP",
        "decision": "classe de malignité suspectée → priorisation en RCP ; décision thérapeutique multidisciplinaire",
        "rm": ["RM-02"]},
    "tumor": {"nom": "Tumeurs cérébrales — volumétrie", "service": "tumor-service",
        "perimetre": "Segmentation cérébrale, volumétrie, grading OMS 2021, planification RT",
        "decision": "fraction lésionnelle → suivi volumétrique ; le contouring seul ne suffit pas à planifier la RT",
        "rm": ["RM-04"]},
    "ophthalmology": {"nom": "Ophtalmologie — rétinopathie / glaucome", "service": "ophthalmology-service",
        "perimetre": "Fond d'œil, OCT, glaucome (C/D, RNFL), rétinopathie diabétique",
        "decision": "stade de rétinopathie diabétique → calendrier de dépistage ; urgences orientées en ophtalmologie",
        "rm": []},
    "diabetes": {"nom": "Diabète — risque de complication", "service": "diabetes-service",
        "perimetre": "Risque ADA, HbA1c/TIR, complications, CGM (Dexcom/Libre/Medtronic)",
        "decision": "intensification du suivi ; aucun ajustement thérapeutique autonome",
        "rm": []},
    "traumatology": {"nom": "Traumatologie — polytrauma", "service": "traumatology-service",
        "perimetre": "Fractures AO/OTA, ligaments (LCA…), Cobb, FRAX, polytrauma ISS",
        "decision": "fracture ouverte / atteinte viscérale / chirurgie requise → priorisation du déchoquage",
        "rm": ["RM-07"]},
    "cardiology": {"nom": "Cardiologie — syndrome coronarien", "service": "cardiology-service",
        "perimetre": "ECG 12 dérivations, ETT (FEVG), coro-CT CAD-RADS, Holter, CHA2DS2-VASc",
        "decision": "stable / angor instable / SCA → filière coronarienne ; l'ECG reste l'élément décisionnel premier",
        "rm": ["RM-07"]},
    "pneumology": {"nom": "Pneumologie — TB / BPCO / embolie", "service": "pneumology-service",
        "perimetre": "Nodules (Fleischner/Lung-RADS), TB, BPCO GOLD, embolie (Wells), spirométrie",
        "decision": "signaux multilabel → examens complémentaires (imagerie, D-dimères, spirométrie)",
        "rm": []},
    "obstetrics": {"nom": "Obstétrique — pré-éclampsie", "service": "obstetrics-service",
        "perimetre": "Biométrie fœtale, CTG/FIGO, clarté nucale, pré-éclampsie, Bishop",
        "decision": "risque de pré-éclampsie → surveillance rapprochée mère-foetus",
        "rm": ["RM-07"]},
    "gynecology": {"nom": "Gynécologie — malignité suspectée", "service": "gynecology-service",
        "perimetre": "Pap/Bethesda, HPV, IOTA simple rules, O-RADS, SOPK Rotterdam, ENZIAN",
        "decision": "malignité suspectée → orientation échographie dédiée / RCP gynécologique",
        "rm": []},
    "fertility": {"nom": "Fertilité — pronostic de conception", "service": "fertility-service",
        "perimetre": "Réserve ovarienne (AMH/CFA), spermogramme OMS 2021, sélection embryonnaire",
        "decision": "pronostic → stratégie d'AMP ; décision collégiale",
        "rm": []},
    "neurology": {"nom": "Neurologie — AVC ischémique", "service": "neurology-service",
        "perimetre": "AVC (ASPECTS, NIHSS), épilepsie EEG, MMSE/MoCA, Parkinson UPDRS, McDonald/EDSS",
        "decision": "AVC ischémique probable → activation du code AVC et fenêtre de thrombolyse ; l'horloge LKW est VALIDÉE par le clinicien (RM-10)",
        "rm": ["RM-07", "RM-10"]},
    "psychiatry": {"nom": "Psychiatrie — sévérité globale", "service": "psychiatry-service",
        "perimetre": "PHQ-9, GAD-7, Y-BOCS, C-SSRS risque suicidaire, AUDIT/DAST",
        "decision": "sévérité → intensification du suivi ; un C-SSRS élevé déclenche la conduite clinique immédiate, hors IA",
        "rm": []},
    "pediatrics": {"nom": "Pédiatrie — croissance", "service": "pediatrics-service",
        "perimetre": "APGAR, courbes OMS, ictère néonatal, calendrier vaccinal PEV, Denver",
        "decision": "indice de croissance → dépistage de la malnutrition (courbes OMS)",
        "rm": []},
    "nephrology": {"nom": "Néphrologie — stade d'insuffisance rénale", "service": "nephrology-service",
        "perimetre": "CKD-EPI/KDIGO, AKI KDIGO, kt/V dialyse, néphrométrie RENAL",
        "decision": "stade MRC → référencement néphrologue ; kt/V oriente la dose de dialyse",
        "rm": []},
    "gastroenterology": {"nom": "Gastro-entérologie — hémorragie active", "service": "gastroenterology-service",
        "perimetre": "Polypes, LI-RADS, Mayo/CDEIS (MICI), Los Angeles (RGO), Forrest",
        "decision": "hémorragie active probable → endoscopie urgente (classification Forrest)",
        "rm": ["RM-07"]},
    "dermatology": {"nom": "Dermatologie — lésions pigmentaires", "service": "dermatology-service",
        "perimetre": "Mélanome ABCDE/7-points, Breslow, PASI, SCORAD, VASI",
        "decision": "naevus / douteux / mélanome → biopsie orientée ; le Breslow histologique reste la référence",
        "rm": []},
    "ent": {"nom": "ORL — tumeur suspectée", "service": "ent-service",
        "perimetre": "Audiogramme, BPPV, Lund-Mackay, cancers ORL (HPV)",
        "decision": "tumeur ORL suspectée → imagerie et biopsie orientées",
        "rm": []},
    "rheumatology": {"nom": "Rhumatologie — activité inflammatoire", "service": "rheumatology-service",
        "perimetre": "DAS28, BASDAI/ASDAS, SLEDAI, Kellgren-Lawrence, critères ANCA",
        "decision": "activité → proposition d'ajustement thérapeutique au rhumatologue",
        "rm": []},
    "urology": {"nom": "Urologie — cancer de prostate significatif", "service": "urology-service",
        "perimetre": "PI-RADS, Gleason, IPSS, score RENAL, calculs (SWL/URS)",
        "decision": "cancer significatif probable → biopsies ciblées (PI-RADS)",
        "rm": []},
    "nuclear_medicine": {"nom": "Médecine nucléaire — réponse thérapeutique", "service": "nuclear-medicine-service",
        "perimetre": "SUV, MTV/TLG, PERCIST, dosimétrie MIRD, théranostique Lu-177",
        "decision": "pourcentage de réponse (PERCIST) → poursuite ou modification de la théranostique",
        "rm": ["RM-04"]},
    "radiotherapy": {"nom": "Radiothérapie — toxicité prédite", "service": "radiotherapy-service",
        "perimetre": "GTV/CTV/PTV, IMRT/VMAT, DVH, gamma index, EQD2, QA machine",
        "decision": "toxicité prédite → optimisation de planification (DVH) ; la QA machine reste indépendante",
        "rm": ["RM-04"]},
    "anesthesia": {"nom": "Anesthésie — événement péri-opératoire", "service": "anesthesia-service",
        "perimetre": "ASA, Lee/RCRI, STOP-BANG, SOFA/APACHE II, RASS, analgésie multimodale",
        "decision": "risque péri-opératoire → orientation de la consultation pré-anesthésique",
        "rm": ["RM-07"]},
    "geriatrics": {"nom": "Gériatrie — risque de chute", "service": "geriatrics-service",
        "perimetre": "Fried, Rockwood, TUG, MMSE/MoCA, Beers/STOPP-START, MNA, Braden, Barthel",
        "decision": "risque de chute à 12 mois → programme de prévention (revue Beers, environnement)",
        "rm": []},
    "emergency": {"nom": "Urgences — triage", "service": "emergency-service",
        "perimetre": "ESI/CTMP/Manchester, qSOFA, ISS, NIHSS code AVC, STEMI, Parkland",
        "decision": "catégorie ESI → priorité de prise en charge ; réévaluation clinique systématique",
        "rm": ["RM-07", "RM-10"]},
}

RM_S = "03-analyse-risques-iso14971.md"
TD = "compliance/mdr/technical-documentation"


def perf_rows(task: str) -> str:
    """Table des métriques PRÉVUES par tâche — aucune valeur avant R6-R8."""
    crit = {
        "classification":
            "| AUC-ROC | patients (sujets indépendants) | 🔴 R6-R8 | ≥ 0.80 visé, critère SAP A5 finalisé R7 |\n"
            "| Sensibilité (classe positive) | idem | 🔴 R6-R8 | faux négatifs = RM-01, prioritaire |\n"
            "| Spécificité | idem | 🔴 R6-R8 | borne les sur-investigations (RM-02) |",
        "multiclass":
            "| Macro-AUC (OvR) | patients (sujets indépendants) | 🔴 R6-R8 | critère SAP A5 finalisé R7 |\n"
            "| F1 par classe | idem | 🔴 R6-R8 | classes déséquilibrées (poids du registre) |\n"
            "| Matrice de confusion | idem | 🔴 R6-R8 | adjugée SAP, publiée au CER TD-11 |",
        "multilabel":
            "| AUC micro/macro | patients (sujets indépendants) | 🔴 R6-R8 | critère SAP A5 finalisé R7 |\n"
            "| Précision/rappel par label | idem | 🔴 R6-R8 | chaque label = une action clinique distincte |",
        "regression":
            "| MAE / RMSE | patients (sujets indépendants) | 🔴 R6-R8 | critère SAP A5 finalisé R7 |\n"
            "| IC 95 % (bootstrap site) | idem | 🔴 R6-R8 | hétérogénéité multicentrique CHU |\n"
            "| Calibration (courbe + pente) | idem | 🔴 R6-R8 | indispensable avant usage pronostique |",
        "segmentation":
            "| Dice / IoU | patients (sujets indépendants) | 🔴 R6-R8 | critère SAP A5 finalisé R7 |\n"
            "| Erreur volumétrique absolue | idem | 🔴 R6-R8 | suivi lésionnel longitudinal |\n"
            "| Robustesse modalité manquante | idem | 🔴 R6-R8 | ADR-0018 : dégrade élégamment |",
    }
    return crit.get(task, "(tâche non reconnue)")


# ------------------------------------------------------------- rendu fiche ---

def _label_desc(label: dict) -> str:
    t = label["task"]
    if t == "classification":
        return f"binaire — `{label['label_nom']}` (prévalence synthétique {label['prevalence']})"
    if t == "multiclass":
        return ("multiclasse — " + ", ".join(f"`{c}`" for c in label["classes"])
                + f" (poids {label['poids']})")
    if t == "multilabel":
        return ("multilabel — " + ", ".join(f"`{c}`" for c in label["classes"])
                + f" (p(ind)≈{label['p']})")
    if t == "segmentation":
        return f"segmentation — `{label['target_nom']}` ∈ [{label['lo']}, {label['hi']}]"
    return f"régression — `{label['target_nom']}` ∈ [{label['lo']}, {label['hi']}]"


def render_card(no: int, slug: str, spec: dict, cfg: dict, audit: dict) -> str:
    meta = MODULE_META[slug]
    rm_extra = meta["rm"]
    rms = ["RM-01", "RM-02", "RM-03", "RM-05"] + rm_extra
    feats = ", ".join(f"`{f}`" for f in spec["features"])
    disc = ", ".join(f"`{f}`" for f in spec["discriminantes"])
    mods = ", ".join(f"`{m}`" for m in cfg["modalities"]["attendues"])
    heads = "oui (ADR-0019 multi-tâches, tronc partagé)" if cfg.get("heads", {}).get("shared_trunk") else "têtes spécialisées"
    expl = []
    e = cfg.get("explainability", {})
    if e.get("modality_importance"):
        expl.append("importance des modalités (`ai/multimodal/explainability/modality_importance.py`)")
    if e.get("attention_viz"):
        expl.append("visualisation d'attention de la fusion croisée (ADR-0017)")
    if e.get("shap_multimodal"):
        expl.append(f"SHAP multimodal (palier {e['shap_multimodal']})")
    expl_txt = " ; ".join(expl) if expl else "—"

    return f"""# MC-{no:02d} — {meta['nom']} ({slug})

> **Model card MDR** (cadre : Mitchell et al. 2019, adaptée MDR 2017/745 Annexe II/III).
> Fiche générée — outil `tools/generate_model_cards.py` {FICHE_VERSION}, sources
> versionnées du dépôt. Toute modification du modèle DOIT passer par une
> régénération + revue (PROC-03 revue conception/V&V).

| Identification | |
|---|---|
| Module | {no}/26 — `{slug}` |
| Version fiche | {FICHE_VERSION} |
| Version plateforme | {PLATFORM_VERSION} |
| Dispositif | MEDISUITE — logiciel CDS fusion multimodale, **MDR règle 11 → classe IIb** (`{TD}/01-identification-classification.md`) |
| Service | `{meta['service']}` (monorepo `services/`) |
| Config IA | `ai/multimodal/configs/{no:02d}_{slug}.yaml` |
| État | 🟢 structure · 🟠 données synthétiques · 🔴 métriques (R6-R8) · CER TD-11 à compléter R7 |

## 1. Usage prévu (intended purpose du module)

**Périmètre fonctionnel** : {meta['perimetre']}.

**Ce que la sortie IA influence** : {meta['decision']}.
Population visée : patients des CHU ivoiriens (COC, TRI, YOP, BOU — investigation
MEDISUITE-CI-01) ; utilisateurs : cliniciens formés (IFU-clinicien), dans un
cadre d'aide à la décision, jamais de décision autonome.

## 2. Hors champ et usages interdits

- **Interdit** : usage diagnostique autonome sans revue clinique ; usage
  pédiatrique/adulte hors populations entraînées ; usage hors établissement
  (site de soins rattaché) ; réutilisation des sorties pour un autre patient.
- **Non couvert** : toute population non représentée dans les données R6 ;
  imagerie hors modalités DICOM standard ; interprétation génomique
  réglementée autre que documentation.
- Toute variante de modèle (re-entraînement, seuils différents) constitue une
  **nouvelle configuration à qualifier** (libération de modèle, section 8 du
  dossier technique — ADR-0012 MLflow, PROC-07 libération).

## 3. Données

| Attribut | Valeur |
|---|---|
| État | 🟠 **SYNTHÉTIQUE** — `datasets/generate.py`, seed {cfg.get('seed', 42)} ; manifest : « AUCUNE donnée réelle… interdit pour l'entraînement clinique validé » |
| Tâche | `{spec['label']['task']}` — {_label_desc(spec['label'])} |
| Features cliniques nommées | {feats} |
| Variables discriminantes (signal artificiel) | {disc} |
| Volumes synthétiques | train {audit.get('n_train', 'n/a')} / val (cf. `datasets/manifest.json`, SHA-256 vérifiés par tests) |
| Données réelles | 🔴 **R6** — collection eCRF FHIR (F01-F06), investigateurs CI-01, verrou M+18 puis extraction SAF data manager (`docs/E-CRF.md`) |

La provenance des données R6 (critères d'inclusion/exclusion, pseudonymisation,
SDV 20 %/100 % SAE) est définie par le protocole d'investigation
`{TD}/10-protocole-investigation-multicentrique-R5.md` et le plan de
monitoring (`compliance/mdr/clinical/monitoring/`).

## 4. Architecture et entraînement

| Attribut | Valeur |
|---|---|
| Moteur de fusion | `ai/multimodal/core/` — backends **numpy / torch** (ADR-0022, équivalence testée), fusion entraînable torch (ADR-0023) |
| Fusion | gated (ADR-0016) + cross-attention (ADR-0017) |
| Modalités attendues | {mods} |
| Modalités manquantes | politique `{cfg['modalities']['politique_modalites_manquantes']}` (ADR-0018, testée) |
| Têtes | {heads} ; pondération des pertes : `{cfg.get('losses', {}).get('weighting', 'n/a')}` (incertitude) |
| Dimension modèle | d_model = {cfg.get('d_model', 'n/a')} |
| Backend courant | `{cfg.get('backend', 'n/a')}` |
| Seed | {cfg.get('seed', 42)} — reproductibilité exigée (MLflow run_id consigné à R6) |

**Preuves d'implémentation actuelles** (audit reproductible `docs/audit-26-modules.md`,
données `docs/_audit_data.json`) : {audit.get('loc', '?')} lignes de service, {audit.get('n_tests', '?')} tests,
{audit.get('n_scores', '?')} scores cliniques implémentés (référentiel cité par score).

## 5. Performances — 🔴 à renseigner R6-R8

> **AUCUN chiffre de performance n'est publié avant le verrou de base M+18.**
> L'analyse suit le SAP (annexe A5 du protocole) sur l'extraction SAF du data
> manager ; l'adjudication alimente le CER TD-11 (MEDDEV 2.7/1 rev 4, ADR-0026).
> Tout résultat antérieur au verrou est irrecevable pour le dossier.

Métriques prévues ({spec['label']['task']}) :

| Métrique | Population | Valeur | Critère |
|---|---|---|---|
{perf_rows(spec['label']['task'])}

Métriques d'ingénierie disponibles dès maintenant (non cliniques) : équivalence
NumPy↔torch, latence p95 banc CPU (`docs/BENCHMARK-GPU.md`), robustesse aux
modalités manquantes (47 tests IA).

## 6. Explicabilité

{expl_txt}.

Les probabilités sont affichées **non binaires** avec l'importance par modalité
(atténuation RM-01/RM-03) ; les seuils de confiance sont affichés à l'écran
(IFU-clinicien §aide à la décision).

## 7. Évaluation clinique et réglementaire

| Élément | Référence | État |
|---|---|---|
| Protocole d'investigation | CI-01, ISO 14155, `{TD}/10-protocole-investigation-multicentrique-R5.md` | 🟢 v1.0 prête à signer (kit `compliance/mdr/clinical/signatures/`) |
| Soumissions | ANOC-CI, PACTR, Ministère+DPIA (`compliance/mdr/submissions/`) | 🟢 checklists prêtes / 🔴 dépôt M+3 |
| Collection multicentrique | eCRF FHIR R6 + verrou M+18 + SAF | 🟢 outillé / 🔴 terrain R6 |
| Rapport clinique | CER MEDDEV 2.7/1 rev 4 (`{TD}/11-…meddev-271.md`, ADR-0026) | 🟢 squelette / 🔴 contenu R7 |
| Bénéfice-risque final | EGSP Annexe I §1, §8 | 🔴 R7 (post-adjudication) |

## 8. Risques et biais (FMEA ISO 14971 — `{TD}/{RM_S}`)

Risques communs à tout modèle IA du dispositif :

| Risque | Mitigation liée à cette fiche |
|---|---|
| RM-01 — faux négatif | probabilités non binaires + importance des modalités ; IFU : outil d'aide, pas de diagnostic autonome |
| RM-02 — faux positif | conduite standardisée par score de référence ; audit périodique des faux positifs (PMS) |
| RM-03 — biais d'automatisation | rappels à l'écran, formation obligatoire IFU, sorties jamais binaires |
| RM-05 — dérive (drift) | DAG Airflow `data-drift-check`, versionning MLflow, seuils calibrés sur données CHU 🔴 R6 |

Accentuations spécifiques du module : {", ".join(rm_extra) if rm_extra else "aucune au-delà du socle commun"}.

**Biais de population** (honnêteté, à instruire R6) : les distributions
anthropométriques, la prévalence des pathologies et les équipements ivoiriens
diffèrent des cohortes de littérature ; la population d'évaluation CI-01
(2-3 CHU) est le moyen de caractériser ce biais, pas de le nier. Sous-groupes
analysés au SAP : sexe, âge, site.

## 9. Limites

- Les données actuelles sont **synthétiques** : toute démonstration d'exactitude
  faite avec est une preuve d'ingénierie, jamais une preuve clinique.
- La fusion est sensible à la qualité d'appariement des modalités (RM-04) :
  un import désynchronisé doit être bloqué en amont (contrôles d'intégrité).
- Les seuils de décision sont des placeholders jusqu'au calibrage CHU (RM-05).
- Ce module hérite des limites d'interopérabilité HL7/FHIR (RM-08) et des
  indépendances d'horloge clinique (RM-10) quand il en dépend.

## 10. Supervision humaine

Le dispositif **n'est pas autonome** (règle 11, justification IIb — TD-01 §3) :
chaque sortie est une recommandation probabiliste sous responsabilité du
clinicien. Les parcours critiques (code AVC, SCA, triage) imposent une
contre-vérification clinique explicite à l'écran. L'usabilité formative (IEC
62366, protocole + grille de passation) puis sommative (🔴 R6) valident ces
parcours avec des praticiens CHU.

## 11. Surveillance post-commercialisation (PMS/PMCF)

- Détection de dérive : DAG Airflow, alertes Prometheus `ai-models` ;
- Incidents/vigilance : `{TD}/07-pms-vigilance.md` (liens PROC-04 incidents/CAPA) ;
- PMCF : continuité de l'évaluation clinique après marquage — les données PMS
  alimentent les mises à jour du CER (cycle MEDDEV 2.7/1 §8) ;
- Tout re-entraînement passe par la libération de modèle (PROC-07, MLflow,
  model registry) et une mise à jour de cette fiche.

## 12. Traçabilité

| Élément | Référence |
|---|---|
| ADR architecture IA | ADR-0016/0017/0018/0019, ADR-0022, ADR-0023 |
| Registre des modules | `datasets/registry.py`, `docs/MODULES.md`, `services/registry.py` |
| Tests verrouillants | {audit.get('n_tests', '?')} tests du service ; datasets (schéma/déterminisme/signal) ; IA 47 tests |
| Dossier technique | `{TD}/00-index-dossier-technique.md` (TD-01…TD-11) |
| Identification produit | EMDN V20199999, Basic UDI-DI famille plateforme (`{TD}/01-…`) |
| SBOM | `compliance/sbom/sbom.json` (CycloneDX) |
| Historique des fiches | cette fiche est régénérée par outil ; l'historique vit dans Git (revue PROC-03) |
"""


def render_index(cards: list[dict], modules: list[tuple[int, str]]) -> str:
    rows = []
    for c in cards:
        rows.append(f"| MC-{c['no']:02d} | [{c['slug']}]({c['file']}) | {c['nom']} | "
                    f"`{c['task']}` | {c['modalites']} | `{c['service']}` | 🟠 synthétique / 🔴 R6 |")
    return f"""# Index des model-cards MEDISUITE — 26 modules

> Générées par `tools/generate_model_cards.py` {FICHE_VERSION} depuis les
> sources de vérité du dépôt (registry + configs IA + audit 26 modules).
> **État global** : 🟢 structure livrée · 🟠 données synthétiques ·
> 🔴 métriques R6-R8 (verrou M+18 → SAP → CER TD-11, ADR-0026).

| Fiche | Module | Nom | Tâche | Modalités | Service | Données / métriques |
|---|---|---|---|---|---|---|
{chr(10).join(rows)}

**Liens** : audit reproductible `docs/audit-26-modules.md` · registry
`datasets/registry.py` · plan de validation `{TD}/08-plan-validation-v1.0.0.md`
(R6 = entraînement réel + model-cards finalisées) · CER `{TD}/11-rapport-evaluation-clinique-meddev-271.md`.
{len(cards)} fiches couvrent l'intégralité des {len(modules)} modules cliniques.
"""


# ------------------------------------------------------------------- main ---

def build_cards() -> tuple[list[dict], list[tuple[int, str]]]:
    modules, spec = _load_registry()
    audit_by_slug = {a["slug"]: a for a in _load_json(ROOT / "docs" / "_audit_data.json")}
    cards = []
    for no, slug in modules:
        cfg = _load_config(no, slug)
        audit = audit_by_slug.get(slug, {})
        text = render_card(no, slug, spec[slug], cfg, audit)
        cards.append({"no": no, "slug": slug, "text": text,
                      "file": f"MC-{no:02d}-{slug}.md",
                      "nom": MODULE_META[slug]["nom"], "task": spec[slug]["label"]["task"],
                      "modalites": ", ".join(cfg["modalities"]["attendues"]),
                      "service": MODULE_META[slug]["service"]})
    return cards, modules


def write_out(outdir: Path, cards: list[dict], modules: list[tuple[int, str]]) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    for c in cards:
        (outdir / c["file"]).write_text(c["text"], encoding="utf-8")
    (outdir / "00-index-model-cards.md").write_text(
        render_index(cards, modules), encoding="utf-8")


def check_out(outdir: Path, cards: list[dict], modules: list[tuple[int, str]]) -> int:
    problems = 0
    expected = {c["file"]: c["text"] for c in cards}
    expected["00-index-model-cards.md"] = render_index(cards, modules)
    for name, text in sorted(expected.items()):
        p = outdir / name
        if not p.exists():
            print(f"MANQUANT : {name}")
            problems += 1
            continue
        actual = p.read_text(encoding="utf-8")
        if actual != text:
            print(f"DÉRIVE : {name}")
            diff = difflib.unified_diff(actual.splitlines(), text.splitlines(),
                                        "fichier", "généré", lineterm="")
            for line in list(diff)[:20]:
                print("   " + line)
            problems += 1
    for p in sorted(outdir.glob("*.md")):
        if p.name not in expected:
            print(f"ORPHELIN : {p.name}")
            problems += 1
    return 1 if problems else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--outdir", type=Path, default=OUTDIR_DEFAULT)
    ap.add_argument("--check", action="store_true",
                    help="vérifie que les fiches sur disque == régénération (CI)")
    args = ap.parse_args()
    cards, modules = build_cards()
    assert len(cards) == 26, f"26 modules attendus, {len(cards)} générés"
    if args.check:
        return check_out(args.outdir, cards, modules)
    write_out(args.outdir, cards, modules)
    print(f"26 model-cards + index écrits dans {args.outdir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
