# 🏥 MEDISUITE — Plateforme Clinique Multimodale Intelligente

> **Monorepo de santé publique ivoirienne** : 38 microservices, 26 modules de spécialités cliniques,
> moteur de fusion multimodale IA résilient aux modalités manquantes, MLOps de bout en bout.
>
> *De l'IMagerie DIgital à la fusion IA — conçu pour les CHU d'Abidjan, les hôpitaux régionaux et les centres de santé ruraux.*

![status](https://img.shields.io/badge/statut-v0.2.0_alpha-2d7ab3) ![python](https://img.shields.io/badge/Python-3.11%2B-3776AB) ![fastapi](https://img.shields.io/badge/FastAPI-0.110%2B-009688) ![license](https://img.shields.io/badge/Licence-MIT-green) ![ci](https://img.shields.io/badge/CI-GitHub_Actions-2088FF)

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
export PyTorch/ONNX prévu en v0.2.

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
- **20 ADR** (`docs/adr/`) documentant chaque décision d'architecture, y compris les choix **contre** la spec initiale (et pourquoi)

## 🗺️ Roadmap

| Version | Contenu | Statut |
|---|---|---|
| v0.1.0 | Socle fonctionnel : services, règles cliniques, fusion NumPy, web-portal, infra locale | ✅ cette release |
| v0.2.0 | PyTorch/MONAI + poids d'entraînement, DICOMweb STOW-RS réel (Orthanc), Kafka events | 🚧 |
| v0.3.0 | FHIR R4 server complet (HAPI), télémétrie OTel, déploiement K8s GPU | 📋 |
| v1.0.0 | Dossier de marquage CE (MDR IIb), validation clinique multicentrique CHU | 📋 |

## 🤝 Contribution

Voir `docs/onboarding/first-contribution.md`. Conventions : commits [Conventional Commits],
tests obligatoires sur tout score clinique nouveau, chaque fonction de règle **doit** citer son
référentiel (guideline + année) dans sa docstring.
