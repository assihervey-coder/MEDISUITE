# MC-01 — Imagerie — détection d'anomalies (imaging)

> **Model card MDR** (cadre : Mitchell et al. 2019, adaptée MDR 2017/745 Annexe II/III).
> Fiche générée — outil `tools/generate_model_cards.py` 1.0.0, sources
> versionnées du dépôt. Toute modification du modèle DOIT passer par une
> régénération + revue (PROC-03 revue conception/V&V).

| Identification | |
|---|---|
| Module | 1/26 — `imaging` |
| Version fiche | 1.0.0 |
| Version plateforme | v1.0.0 (cible) — jalons v0.1→v0.9 tagués |
| Dispositif | MEDISUITE — logiciel CDS fusion multimodale, **MDR règle 11 → classe IIb** (`compliance/mdr/technical-documentation/01-identification-classification.md`) |
| Service | `imaging-service` (monorepo `services/`) |
| Config IA | `ai/multimodal/configs/01_imaging.yaml` |
| État | 🟢 structure · 🟠 données synthétiques · 🔴 métriques (R6-R8) · CER TD-11 à compléter R7 |

## 1. Usage prévu (intended purpose du module)

**Périmètre fonctionnel** : Radiographie, scanner, IRM, échographie — DICOMweb complet.

**Ce que la sortie IA influence** : priorisation d'examens et orientation diagnostique ; le diagnostic final reste radiologique.
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
| État | 🟠 **SYNTHÉTIQUE** — `datasets/generate.py`, seed 42 ; manifest : « AUCUNE donnée réelle… interdit pour l'entraînement clinique validé » |
| Tâche | `classification` — binaire — `anomalie` (prévalence synthétique 0.35) |
| Features cliniques nommées | `qualite_image`, `score_anomalie`, `bruit_std`, `dose_ct_gy`, `contraste` |
| Variables discriminantes (signal artificiel) | `score_anomalie`, `contraste` |
| Volumes synthétiques | train 120 / val (cf. `datasets/manifest.json`, SHA-256 vérifiés par tests) |
| Données réelles | 🔴 **R6** — collection eCRF FHIR (F01-F06), investigateurs CI-01, verrou M+18 puis extraction SAF data manager (`docs/E-CRF.md`) |

La provenance des données R6 (critères d'inclusion/exclusion, pseudonymisation,
SDV 20 %/100 % SAE) est définie par le protocole d'investigation
`compliance/mdr/technical-documentation/10-protocole-investigation-multicentrique-R5.md` et le plan de
monitoring (`compliance/mdr/clinical/monitoring/`).

## 4. Architecture et entraînement

| Attribut | Valeur |
|---|---|
| Moteur de fusion | `ai/multimodal/core/` — backends **numpy / torch** (ADR-0022, équivalence testée), fusion entraînable torch (ADR-0023) |
| Fusion | gated (ADR-0016) + cross-attention (ADR-0017) |
| Modalités attendues | `imaging_2d`, `imaging_3d`, `tabulaire` |
| Modalités manquantes | politique `degrade_elegamment` (ADR-0018, testée) |
| Têtes | oui (ADR-0019 multi-tâches, tronc partagé) ; pondération des pertes : `uncertainty` (incertitude) |
| Dimension modèle | d_model = 32 |
| Backend courant | `numpy` |
| Seed | 42 — reproductibilité exigée (MLflow run_id consigné à R6) |

**Preuves d'implémentation actuelles** (audit reproductible `docs/audit-26-modules.md`,
données `docs/_audit_data.json`) : 371 lignes de service, 16 tests,
0 scores cliniques implémentés (référentiel cité par score).

## 5. Performances — 🔴 à renseigner R6-R8

> **AUCUN chiffre de performance n'est publié avant le verrou de base M+18.**
> L'analyse suit le SAP (annexe A5 du protocole) sur l'extraction SAF du data
> manager ; l'adjudication alimente le CER TD-11 (MEDDEV 2.7/1 rev 4, ADR-0026).
> Tout résultat antérieur au verrou est irrecevable pour le dossier.

Métriques prévues (classification) :

| Métrique | Population | Valeur | Critère |
|---|---|---|---|
| AUC-ROC | patients (sujets indépendants) | 🔴 R6-R8 | ≥ 0.80 visé, critère SAP A5 finalisé R7 |
| Sensibilité (classe positive) | idem | 🔴 R6-R8 | faux négatifs = RM-01, prioritaire |
| Spécificité | idem | 🔴 R6-R8 | borne les sur-investigations (RM-02) |

Métriques d'ingénierie disponibles dès maintenant (non cliniques) : équivalence
NumPy↔torch, latence p95 banc CPU (`docs/BENCHMARK-GPU.md`), robustesse aux
modalités manquantes (47 tests IA).

## 6. Explicabilité

importance des modalités (`ai/multimodal/explainability/modality_importance.py`) ; visualisation d'attention de la fusion croisée (ADR-0017) ; SHAP multimodal (palier v0.2).

Les probabilités sont affichées **non binaires** avec l'importance par modalité
(atténuation RM-01/RM-03) ; les seuils de confiance sont affichés à l'écran
(IFU-clinicien §aide à la décision).

## 7. Évaluation clinique et réglementaire

| Élément | Référence | État |
|---|---|---|
| Protocole d'investigation | CI-01, ISO 14155, `compliance/mdr/technical-documentation/10-protocole-investigation-multicentrique-R5.md` | 🟢 v1.0 prête à signer (kit `compliance/mdr/clinical/signatures/`) |
| Soumissions | ANOC-CI, PACTR, Ministère+DPIA (`compliance/mdr/submissions/`) | 🟢 checklists prêtes / 🔴 dépôt M+3 |
| Collection multicentrique | eCRF FHIR R6 + verrou M+18 + SAF | 🟢 outillé / 🔴 terrain R6 |
| Rapport clinique | CER MEDDEV 2.7/1 rev 4 (`compliance/mdr/technical-documentation/11-…meddev-271.md`, ADR-0026) | 🟢 squelette / 🔴 contenu R7 |
| Bénéfice-risque final | EGSP Annexe I §1, §8 | 🔴 R7 (post-adjudication) |

## 8. Risques et biais (FMEA ISO 14971 — `compliance/mdr/technical-documentation/03-analyse-risques-iso14971.md`)

Risques communs à tout modèle IA du dispositif :

| Risque | Mitigation liée à cette fiche |
|---|---|
| RM-01 — faux négatif | probabilités non binaires + importance des modalités ; IFU : outil d'aide, pas de diagnostic autonome |
| RM-02 — faux positif | conduite standardisée par score de référence ; audit périodique des faux positifs (PMS) |
| RM-03 — biais d'automatisation | rappels à l'écran, formation obligatoire IFU, sorties jamais binaires |
| RM-05 — dérive (drift) | DAG Airflow `data-drift-check`, versionning MLflow, seuils calibrés sur données CHU 🔴 R6 |

Accentuations spécifiques du module : RM-02, RM-04.

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
- Incidents/vigilance : `compliance/mdr/technical-documentation/07-pms-vigilance.md` (liens PROC-04 incidents/CAPA) ;
- PMCF : continuité de l'évaluation clinique après marquage — les données PMS
  alimentent les mises à jour du CER (cycle MEDDEV 2.7/1 §8) ;
- Tout re-entraînement passe par la libération de modèle (PROC-07, MLflow,
  model registry) et une mise à jour de cette fiche.

## 12. Traçabilité

| Élément | Référence |
|---|---|
| ADR architecture IA | ADR-0016/0017/0018/0019, ADR-0022, ADR-0023 |
| Registre des modules | `datasets/registry.py`, `docs/MODULES.md`, `services/registry.py` |
| Tests verrouillants | 16 tests du service ; datasets (schéma/déterminisme/signal) ; IA 47 tests |
| Dossier technique | `compliance/mdr/technical-documentation/00-index-dossier-technique.md` (TD-01…TD-11) |
| Identification produit | EMDN V20199999, Basic UDI-DI famille plateforme (`compliance/mdr/technical-documentation/01-…`) |
| SBOM | `compliance/sbom/sbom.json` (CycloneDX) |
| Historique des fiches | cette fiche est régénérée par outil ; l'historique vit dans Git (revue PROC-03) |
