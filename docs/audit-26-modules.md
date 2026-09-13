# Audit des 26 modules cliniques — v0.6.0 (septembre 2026)

> Question : *« les 26 modules (Module / Service / AI Module / Datasets /
> Configs) sont-ils implémentés de façon optimale ? »*
> Méthode : **vérification par les artefacts**, pas par déclaration —
> chaque case de la matrice ci-dessous est dérivée des fichiers du dépôt par
> `tools/audit_26_modules.py` (données brutes : `docs/_audit_data.json`).

## 1. Verdict par dimension

| Dimension | Couverture | État | Preuve |
|---|---|---|---|
| **Module** (écran web) | 26/26 | 🟢 | 24 modules de spécialité via `ClinicalPanel` (ADR-0020, `modules-nav.ts`) + écrans dédiés 01 Imaging (`StudyList` DICOMweb, `BiRadsViewer`), 02 Laboratory (`Results`), + écrans transverses (TriageBoard, StrokeCode, FusionViewer, AuditLog, **About UDI v0.6.0**) |
| **Service** (FastAPI) | 26/26 | 🟢 | contrat unique `create_service_app` (version+commit UDI, OTel, RBAC), seed ivoirien, **174 tests** sur les suites spécialités, 38/38 suites vertes |
| **AI Module** (config fusion) | 26/26 | 🟢 | `ai/multimodal/configs/01…26.yaml` — tâche, modalités, d_model, heads, expliquabilité ; backends numpy/torch/monai (ADR 0022-0023) ; factory `engine_for_module(no)` |
| **Datasets** | 26/26 | 🟢 (v0.6.0) | `datasets/<slug>/train+val.jsonl` + `manifest.json` SHA-256 + 6 tests (était 🟠 : un seul générateur patients partagé) |
| **Configs** | 26/26 | 🟢 | configs IA par module + `configs/common/feature-flags.yaml` + `configs/clinical/westgard-rules.yaml` + env compose/K8s (registry déclarative) |

**Réponse courte : oui sur les cinq dimensions du tableau, aujourd'hui —
mais « optimal » a deux sens qu'il ne faut pas confondre.** L'implémentation
d'ingénierie (architecture, tests, traçabilité) est complète et vérifiable ;
la **validité clinique des sorties IA** ne l'est pas et ne le sera pas avant
l'investigation multicentrique R5-R8 — c'est l'objet des documents 🔴 du
dossier CE, pas un défaut d'implémentation.

## 2. Matrice détaillée (données extraites du dépôt)

| # | Module | Écran(s) web | Service (tests) | Scores cliniques embarqués | Config IA (tâche) | Dataset (train/val) |
|---|---|---|---|---|---|---|
| 1 | 🩻 Imaging | StudyList + BiRadsViewer | imaging-service (16) | — (DICOMweb STOW/QIDO/WADO + PACS) | 01 (classification) | 120/30 |
| 2 | 🧪 Laboratory | Results | laboratory-service (8) | — (workflow + Westgard + delta check) | 02 (régression) | 120/30 |
| 3 | 🎗️ Oncology | ClinicalPanel | oncology-service (9) | birads, fleischner, lung-rads, tnm-breast, roma, ecog (6) | 03 (multiclasse) | 120/30 |
| 4 | 🧠 Tumor | ClinicalPanel | tumor-service (5) | segmentation volumétrie (2) | 04 (segmentation) | 120/30 |
| 5 | 👁️ Ophthalmology | ClinicalPanel | ophthalmology-service (5) | rétinopathie, glaucome (2) | 05 (multiclasse) | 120/30 |
| 6 | 🩸 Diabetes | ClinicalPanel | diabetes-service (5) | risque ADA, HbA1c/TIR (2) | 06 (régression) | 120/30 |
| 7 | 🦴 Traumatology | ClinicalPanel | traumatology-service (5) | ISS, Cobb/FRAX (2) | 07 (multilabel) | 120/30 |
| 8 | ❤️ Cardiology | ClinicalPanel | cardiology-service (7) | cha2ds2-vasc, heart, fevg, cad-rads (4) | 08 (multiclasse) | 120/30 |
| 9 | 🫁 Pneumology | ClinicalPanel | pneumology-service (7) | wells, curb-65, gold, lung-rads (4) | 09 (multilabel) | 120/30 |
| 10 | 🤰 Obstetrics | ClinicalPanel | obstetrics-service (5) | bishop, pré-éclampsie (2) | 10 (binary→classif.) | 120/30 |
| 11 | 🌸 Gynecology | ClinicalPanel | gynecology-service (6) | iota, rotterdam, orads (3) | 11 (binary→classif.) | 120/30 |
| 12 | 🧬 Fertility | ClinicalPanel | fertility-service (4) | réserve ovarienne AMH/CFA (1) | 12 (régression) | 120/30 |
| 13 | 🧠 Neurology | StrokeCode + Panel | neurology-service (7) | nihss, aspects, mmse, mcdonald (4) | 13 (binary→classif.) | 120/30 |
| 14 | 🧬 Psychiatry | ClinicalPanel | psychiatry-service (7) | phq-9, gad-7, cssrs, audit (4) | 14 (régression) | 120/30 |
| 15 | 👶 Pediatrics | ClinicalPanel | pediatrics-service (5) | apgar, ictère, courbes OMS (2) | 15 (régression) | 120/30 |
| 16 | 🫘 Nephrology | ClinicalPanel | nephrology-service (7) | ckd-epi, kdigo, kt/v, renal (4) | 16 (régression) | 120/30 |
| 17 | 🫄 Gastroenterology | ClinicalPanel | gastroenterology-service (7) | forrest, li-rads, mayo, la (4) | 17 (binary→classif.) | 120/30 |
| 18 | 🩹 Dermatology | ClinicalPanel | dermatology-service (6) | abcde/breslow, pasi, scorad (3) | 18 (multiclasse) | 120/30 |
| 19 | 👂 ENT | ClinicalPanel | ent-service (6) | audiogramme, lund-mackay, hpv (3) | 19 (binary→classif.) | 120/30 |
| 20 | 🦴 Rheumatology | ClinicalPanel | rheumatology-service (7) | das28, basdai/asdas, sledai, kl (4) | 20 (régression) | 120/30 |
| 21 | 🚹 Urology | ClinicalPanel | urology-service (7) | pirads, gleason, ips, renal (4) | 21 (binary→classif.) | 120/30 |
| 22 | ☢️ Nuclear Med | ClinicalPanel | nuclear-medicine-service (5) | suv/percist, mird (2) | 22 (régression) | 120/30 |
| 23 | 🎯 Radiotherapy | ClinicalPanel | radiotherapy-service (5) | dvh/gamma, eqd2 (2) | 23 (régression) | 120/30 |
| 24 | 💉 Anesthesia | ClinicalPanel | anesthesia-service (6) | asa, lee/rcri, stopbang, sofa (3) | 24 (binary→classif.) | 120/30 |
| 25 | 👴 Geriatrics | ClinicalPanel | geriatrics-service (8) | fried, rockwood, tug, mna, braden (5) | 25 (binary→classif.) | 120/30 |
| 26 | 🚨 Emergency | TriageBoard + Panel | emergency-service (9) | esi/ctmp, qsofa, iss, nihss, steomi, parkland (6) | 26 (multiclasse) | 120/30 |

> La logique des scores vit dans **un seul moteur** `packages/clinical-rules`
> (~90 scores référencés, testés) — les services n'en sont que les
> exposants REST (`POST /api/v1/scores/{nom}`) : une implémentation par
> référence, jamais copiée.

## 3. Ce que v0.6.0 a corrigé pour rendre ce tableau vrai

1. **Datasets par module (l'écart 🟠 historique)** : un seul générateur
   patients existait ; les 26 jeux train/val + manifest SHA-256 + tests
   (déterminisme, schéma, signal apprenant, ADR-0018) sont livrés.
2. **`/health` version + commit** : l'étiquetage le promettait (§2 règle 1),
   la fabrique ne l'exposait pas — corrigé au niveau du noyau (38 services
   héritent) + 3 tests.
3. **Écran « À propos » UDI** (écart 🔴 déclaré R2) : étiquette réglementaire
   publique (`/api/v1/about` + page web), écart clôturé.
4. **Audit reproductible** : `tools/audit_26_modules.py` régénère ce tableau
   — un audit qui ne peut pas être rejoué n'est pas un audit.

## 4. Ce qui reste non optimal (honnêteté d'ingénieur)

| Écart | Nature | Jalon |
|---|---|---|
| Entraînement sur données réelles | les modèles fusion sont entraînables mais pas encore entraînés sur corpus clinique (datasets synthétiques exclus par conception) | R6 (investigation) |
| Exécution usabilité formative/summative | protocoles + grilles prêts, participants CHU 🔴 | R3 |
| Connecteurs SIH externes réels | HAPI/Orthanc/OHIF réels dans le dépôt ; LIS/PACS hospitaliers spécifiques à brancher par site | R4-R6 |
| Campagne GPU CHU | banc CPU PASS (p95 0,79 ms) ; mesures matériel cible à refaire sur site | R4 |
| Datasets pédiatriques dédiés | la limite « non destiné à un usage pédiatrique sans protocole dédié » (étiquetage) s'applique : module 15 a un dataset mais pas de protocole pédiatrique distinct | R5 amende |
| i18n des écrans modules | ClinicalPanel en français uniquement ; i18n fr/en partiel | backlog UI |
| Offline / connectivité faible | pas de mode dégradé hors ligne documenté — réel en contexte ivoirien | backlog v1.1 |

## 5. Rejouer cet audit

```bash
python tools/audit_26_modules.py   # régénère docs/_audit_data.json
python -m pytest datasets/tests/ -q
python services/run_tests.py       # 38/38 suites
```
