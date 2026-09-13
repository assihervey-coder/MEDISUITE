# 🏥 MEDISUITE — Plateforme Clinique Multimodale Intelligente

> **Monorepo de santé publique ivoirienne** : 38 microservices, 26 modules de spécialités cliniques,
> moteur de fusion multimodale IA résilient aux modalités manquantes, MLOps de bout en bout.
>
> *De l'IMagerie DIgital à la fusion IA — conçu pour les CHU d'Abidjan, les hôpitaux régionaux et les centres de santé ruraux.*

![status](https://img.shields.io/badge/statut-v0.12.0_alpha-2d7ab3) ![python](https://img.shields.io/badge/Python-3.11%2B-3776AB) ![fastapi](https://img.shields.io/badge/FastAPI-0.110%2B-009688) ![license](https://img.shields.io/badge/Licence-MIT-green) ![ci](https://img.shields.io/badge/CI-GitHub_Actions-2088FF)

---

## ⚡ Démarrage rapide

```bash
make install-core     # dépendances minimales
make test             # moteur de règles cliniques + services + fusion IA
make dev-up           # démarre tous les services (SQLite local, aucune config requise)
make smoke            # vérifie la santé des 38 services
```

Aucune base de données externe n'est requise en mode développement : chaque service utilise
SQLite (`data/<service>.db`) avec données de démonstration ivoiriennes (CNAM, FCFA, CHU Cocody…).

## 🧭 Cartographie

| Couche | Composants | Ports |
|---|---|---|
| **Passerelles** | `api-gateway` · `dicom-gateway` · `hl7-gateway` · `multimodal-gateway` | 8000, 8300-8302 |
| **Cœur** | `auth-service` · `patient-service` · `imaging-service` · `laboratory-service` | 8001-8004 |
| **Transverses** | `reporting` · `notification` · `audit` (registre chaîné) · `integration` (HL7v2/FHIR R4/IHE) · `analytics` | 8200-8204 |
| **Spécialités (24)** | oncology → emergency (modules 03 à 26, voir `docs/MODULES.md`) | 8100-8123 |
| **IA** | `ai/multimodal` (fusion cross-attention), `ai/mlops` (MLflow·Feast·DVC·Airflow), `explainability-service` | 8303 |
| **Interfaces** | `apps/web-portal` (Vite+React+TS, 120+ écrans), `apps/patient-portal`, `apps/admin-console`, `apps/CLI` | 5173 |
| **Infra** | `infrastructure/` (Terraform·K8s·Helm·ArgoCD·Flux·Ansible), `monitoring/` (Prometheus·Grafana·Loki·Tempo) | — |

## 🧠 Le cœur de la valeur : moteur de règles cliniques + fusion multimodale

**1. `packages/clinical-rules`** — un moteur **centralisé, testé, traçable aux référentiels** :
chaque score clinique est implémenté une seule fois (KDIGO 2012, qSOFA/Surviving Sepsis 2021,
Fleischner 2017, BI-RADS 5e éd., GOLD 2024, STOP-BANG, Parkland, CKD-EPI 2021, FRAX, DAS28,
Fried, Braden, ESI 4e éd., CTMP…), importé par les services via une API purement fonctionnelle,
avec tests unitaires sur cas limites. *Un seul endroit pour auditer, une seule version de la vérité clinique.*

**2. `ai/multimodal`** — fusion cross-attention **nativerement tolérante aux modalités manquantes**
(ADR-0018) : masquage appris, encodage de présence, gated fusion résiduelle, 7 encodeurs
(image 2D/3D, signal 1D, tabulaire, texte, génomique, waveform), 6 têtes (binaire, multiclasse,
multi-label, régression, survie, segmentation) et explicabilité (importance des modalités via
poids d'attention). Implémentation de référence **NumPy pur** (aucune dépendance GPU requise),
export PyTorch/ONNX réalisé en v0.2 (ADR 0022) ; fusion entraînable en v0.3 (ADR 0023).

**3. `services/audit-service`** — registre d'audit **à chaîne de hachage** (SHA-256 chaînée,
horodatage, vérification d'intégrité `POST /api/v1/chain/verify`) : répond à l'exigence de
traçabilité IEC 81001-5-1 sans la complexité d'une blockchain (décision ADR-0021).

## 🔒 Sécurité & conformité by design

- **JWT HS256** signé (implémentation stdlib auditable) + **scrypt** pour les mots de passe + **TOTP RFC 6238** (MFA)
- **RBAC** matrice clinique (médecin, biologiste, radiologue, infirmier, pharmacien, admin, patient)
- **Pseudonymisation** des identités dans les flux inter-services + consentements RGPD (`consent` dans patient-service)
- **OPA/Rego** pour l'autorisation clinique fine (`security/policies/opa/`)
- `compliance/` : dossiers MDR 2017/745 (classification IIb), ISO 13485, ISO 14971, IEC 62304 (niveau C),
  RGPD/DPIA, HDS — avec **cartographie honnête des écarts** (voir `compliance/GAP-ANALYSIS.md`)

> ⚠️ **Avertissement** : MEDISUITE v0.1 est un socle d'ingénierie **non certifié** comme dispositif
> médical. Toute mise en production clinique exige l'application complète du système de management
> de la qualité (ISO 13485) et le marquage CE.

## 📊 Chiffres du dépôt

- **38 services** Python/FastAPI prêts à démarrer, chacun avec `/health`, seed ivoirien et tests
- **~120 écrans** web générés sur le pattern `ClinicalPanel` branchés aux vraies API
- **60+ scores cliniques** implémentés et testés dans `packages/clinical-rules`
- **23 ADR** (`docs/adr/`) documentant chaque décision d'architecture, y compris les choix **contre** la spec initiale (et pourquoi)

## 🗺️ Roadmap

| Version | Contenu | Statut |
|---|---|---|
| v0.1.0 | Socle fonctionnel : services, règles cliniques, fusion NumPy, web-portal, infra locale | ✅ |
| v0.2.0 | Écrans BI-RADS + code AVC, backends torch/monai (ADR 0022), PACS Orthanc réel | ✅ |
| v0.3.0 | Visualiseur OHIF v3 sur /dicom-web, fusion torch ENTRAÎNABLE de bout en bout (ADR 0023) | ✅ |
| v0.4.0 | Serveur FHIR R4 réel (HAPI JPA), télémétrie OpenTelemetry (W3C + OTLP + collector), déploiement K8s GPU time-slicing, **démarrage du dossier CE MDR IIb** (dossier technique Annexe II/III) | ✅ |
| v0.5.0 | Jalons R1-R4 (SMQ 8 procédures, IFU 4 profils, usabilité formative, Vault/mTLS/SBOM/pentest-plan), **ADR-0024 profils FHIR nationaux IOP-CI candidats**, banc de performance EGSP (p95 ≤ 2 s : PASS) | ✅ |
| v0.6.0 | **Protocole d'investigation multicentrique R5 détaillé** (MEDISUITE-CI-01, ISO 14155), écran « À propos » UDI (`/api/v1/about` + web), datasets synthétiques des 26 modules + tests, [audit des 26 modules](docs/audit-26-modules.md) | ✅ |
| v0.7.0 | **eCRF FHIR opérationnel (R6)** : service dédié + [écran portal offline-first](docs/E-CRF.md) (saisie → signature → requêtes SDV → export DSMB), **mode offline du portal** ([SW + file IndexedDB idempotente](docs/OFFLINE-PORTAL.md)), **UDI-EID GS1 codifiable** ([GTIN/AIs/Digital Link](docs/UDI-GS1.md)) + rôles GCP eCRF | ✅ |
| v0.8.0 | **Couverture de l'arborescence initiale** ([audit mesuré](docs/COUVERTURE-ARBRE-INITIAL.md)), **instruments terrain R6** : [monitoring A4 + registre déviations](compliance/mdr/clinical/monitoring/plan-monitoring.md), [checklists ANOC-CI/PACTR/Ministère-DPIA](compliance/mdr/submissions/00-index-soumissions.md), **verrou de base M+18 + extraction SAF data manager** (checksum contenu, alarme intégrité), **ADR-0025 sampling OTel** déterministe parent-based | ✅ |
| v0.9.0 | **Écran promoteur « study status/lock »** (timeline R5-R8, verrou M+18 pilotable à l'écran — confirmation typée + 2 témoins, agrégats DSMB), **ADR-0026 rapport clinique MEDDEV 2.7/1 rev 4** + [squelette CER TD-11](compliance/mdr/technical-documentation/11-rapport-evaluation-clinique-meddev-271.md), **kit de signatures terrain R5** (page v1.0, registre investigateurs, journal de délégation ISO 14155 F.4.3), idempotence locale des suites (BDD fraîche par run) | ✅ cette release |
| v0.10.0 | **Model-cards formelles ×26** ([index](compliance/mdr/model-cards/00-index-model-cards.md)) générées par `tools/generate_model_cards.py` depuis les sources de vérité du dépôt (registry, configs IA, audit 26 modules) — 6 tests verrouillants + idempotence CI (`--check`) ; métriques 🔴 R6-R8 (verrou M+18 → SAP → CER TD-11) | ✅ |
| v0.11.0 | **Usabilité sommative IEC 62366-1** ([protocole + grille + rapport](compliance/mdr/technical-documentation/usability/protocole-evaluation-sommative.md) — exécution R6), **i18n réel du portal** fr/en/**ar (RTL)**/es — 43 clés × 4 langues + 6 tests, **CI GPU self-hosted optionnelle** (dispatch, banc EGSP) | ✅ |
| v0.12.0 | **e2e Playwright** ([5 parcours](apps/web-portal/e2e/portal.spec.ts), APIs mockées, RTL arabe vérifié bout-en-bout) + job CI, **charge k6 verrouillée** ([smoke + stress, seuil EGSP p95 ≤ 2 s](testing/load/README.md)) + workflow dispatch, Makefile réparé | ✅ |
| v1.0.0 | Dossier de marquage CE (MDR IIb) complet, évaluation clinique multicentrique CHU, SMQ ISO 13485 | 📋 — plan `compliance/mdr/technical-documentation/08-plan-validation-v1.0.0.md` |

## 🤝 Contribution

Voir `docs/onboarding/first-contribution.md`. Conventions : commits [Conventional Commits],
tests obligatoires sur tout score clinique nouveau, chaque fonction de règle **doit** citer son
référentiel (guideline + année) dans sa docstring.
