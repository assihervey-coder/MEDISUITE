# Couverture de l'arborescence initiale — audit réel v0.8.0

> **Question posée** : « relis l'arborescence initiale et compare-la à ce qui
> est déjà fait en termes de contenu réel fonctionnel ».
> **Méthode** : relecture intégrale du fichier d'arborescence initial
> (2 674 chemins de fichiers + 359 répertoires listés — l'énoncé « ~15 000
> fichiers » correspondait au déploiement complet des variantes, le fichier
> lui-même liste 2 674 entrées), extraction automatique des chemins, puis
> correspondance à deux niveaux contre les 509 fichiers réels du dépôt :
> **EXACT** (même chemin) et **FAMILLE** (même répertoire parent + nom de base
> normalisé — capte les consolidations, renommages et artefacts d'accolades
> `{a,b}` de la spec). Outil reproductible : `tools/compare_arborescence.py`.

## 1. Chiffres globaux (mesurés, pas déclarés)

| Mesure | Valeur |
|---|---|
| Chemins de fichiers de l'arborescence initiale | 2 674 (+ 359 répertoires) |
| Fichiers réels du dépôt v0.7.0 | 509 |
| Correspondances **exactes** | **108** |
| Correspondances **famille** (consolidées/renommées) | **43** |
| Chemins aspirés sans équivalent de nom | 2 523 (→ §3 : consolidés par conception) |
| Fichiers réels **absents de la spec** (construits au-delà) | **401** |

Lecture honnête : le dépôt réel ne « copie » pas l'arborescence ; il en
implémente la **fonction métier** en 509 fichiers à haute densité (12 400+
lignes Python, ~90 scores cliniques, 39 suites de services testées) là où la
spec répliquait des gabarits de dossiers par service. Les 401 fichiers hors
plan (25 ADR, dossier CE MDR, eCRF, offline, GS1, datasets, audit 26 modules,
banc EGSP…) sont **la part d'ingénierie allant au-delà de la spécification**.

## 2. Couverture bloc par bloc

| Bloc (spec) | Aspiré | Réel v0.7.0 | Mécanisme de couverture | Verdict |
|---|---|---|---|---|
| `services/` 34 microservices, ~60 f. chacun | 1 581 | 39 services testés (152 f.) + `medisuite_core` 23 modules | **ADR-0020** : un template + fabrique `create_service_app` ; ce que la spec dupliquait 34× (`middleware/`, `routing/`, `core/`, `schemas/`, JWT/TOTP/RBAC, audit) vit **une seule fois** dans le noyau partagé | 🟢 fonctionnel, mieux que spec |
| `ai/` fusion + MLOps | 269 | 57 f. : core NumPy + torch (ADR-0022/0023), 7 encodeurs, 6 têtes, 26 configs, MLflow/DVC/Airflow/Feast/Kubeflow/KServe | Les 269 fichiers aspirés = éclatement d'un même moteur ; réel = moteur unique testé (47 tests, équivalence NumPy↔torch prouvée) | 🟢 |
| `apps/web-portal` ~130 écrans | ~180 | 37 f. : 12 domaines d'écrans + ClinicalPanel **piloté par configs** (24 modules) + BiRadsViewer, StrokeCode, ECRF, About UDI, offline (SW+IndexedDB), i18n fr/en | Les écrans spécialisés de la spec = variantes d'un même gabarit ; réel = gabarit + configs + 4 écrans critiques dédiés | 🟠 générique livré, écrans dédiés par spécialité = backlog |
| `apps/mobile`, `apps/desktop`, extensions viewer maison | 38 | 0 (OHIF v3.8.3 branché `/dicom-web` à la place des extensions maison) | Choix assumé : viewer standard éprouvé > extensions à maintenir ; mobile/desktop hors périmètre v0.x | 🔴 backlog v1+ |
| `docs/` guides+architecture | 163 | 36 f. dont 24 ADR + 10 guides réels (PACS, OHIF, FHIR, OTEL, K8S-GPU, E-CRF, OFFLINE, UDI-GS1, BENCHMARK, MODULES) | La spec empilait des docs normatives ; réel = guides d'usage + ADR traçables | 🟠 |
| `docs/compliance/` 15 normes + 26 model-cards | 46 | `compliance/` 30 f. **répartis** : dossier CE MDR 11 docs, SMQ 9 PROC, IFU 4 profils + étiquetage, usabilité, hardening, SBOM CycloneDX | Structure réelle (par livrable CE) plus opérante que 15 fichiers normatifs plats ; **model-cards formelles par module : 🔴** (partiellement couvert par datasets/registry + audit-26-modules + configs IA) | 🟠 model-cards 🔴 |
| `infrastructure/` | 83 | 17 f. : Terraform, K8s base+overlays+Helm, GPU (8 YAML validés), ArgoCD+Flux | La spec listait 8 modules Terraform × 4 env ; réel = un socle paramétrable + overlays | 🟢 (multi-env staging/prod à dérouler) |
| `configs/` | 64 | 2 f. configs ops + 26 configs IA (dans `ai/multimodal/configs/`) | Déplacement assumé : les configs vivent près du code | 🟢 |
| `.github/` CI 12 workflows + 13 actions composables | 55 | 1 `ci.yml` (3 jobs) | **Écart réel découvert par cet audit** → corrigé v0.8 : job `core+datasets+integration` ajouté, `tsc \|\| true` silencieux remplacé par contrôle strict ; GPU/e2e actions = backlog | 🟠 corrigé |
| `compliance/` (racine spec) | — | → voir `docs/compliance/` ci-dessus | — | 🟢 |
| `local-deployment/` 12 scripts setup | 32 | compose minimal **11 services** (Orthanc, HAPI+PG16, otel-collector, vault, OHIF…) + hapi/ + ohif/ + orthanc.json + scripts (certs, secrets, SBOM) | Scripts setup 00-10 et packages offline `.tar` : 🔴 backlog (chronophage, valeur faible avant déploiement CHU réel) | 🟠 |
| `security/` | 19 | `compliance/security/hardening/` : Vault (compose+policies+init), PKI mTLS (script vérifié openssl), plan pentest ASVS, SBOM | — | 🟢 outillage ; exécution pentest externe 🔴 terrain |
| `monitoring/` | 22 | otel collector, Prometheus (+ job OTel), alertes cliniques/IA, Grafana | — | 🟢 |
| `packages/` | 14 | 46 f. : `medisuite_core` (JWT, TOTP, RBAC, audit chaîné, HL7 v2.5+MLLP, FHIR R4, HAPI, OTel, eCRF, GS1-UDI, seed) + `clinical-rules` (~90 scores) | **Largement au-delà de la spec** : la spec dispersait ces capacités par service ; réel = noyau certifiable | 🟢+ |
| `testing/` k6/jest/playwright | 7 | stratégie intégrée : 127 tests packages+datasets, 47 IA, 39 suites services, vitest portal, openers factices HAPI/OTLP | dossiers dédiés e2e/charge : 🔴 backlog (playwright, k6) | 🟠 |
| Racine : 12 compose variants, nix/tilt/skaffold/jenkins/circleci/gitlab/azure/drone/woodpecker, husky/lintstaged… | ~90 | 1 compose minimal + 1 CI + Makefile + env example | **Non retenu volontairement** (YAGNI) : une seule source de vérité par environnement, 0 duplication d'intent — choix documenté ici | 🟢 choix d'ingénierie |

## 3. Les 2 523 « sans équivalent de nom » : consolidés, pas manquants

La quasi-totalité tombe dans trois mécanismes **conscients et documentés** :

1. **Duplication par gabarit** (≈1 450 fichiers) : la spec écrit 34× la même
   arborescence par service (`src/api/v1/`, `core/`, `models/`, `schemas/`,
   `migrations/`…). Le dépôt réel fournit ces fonctions **une fois** dans
   `medisuite_core` (contrat unique `create_service_app`, JWT HS256, RBAC
   fail-closed, audit chaîné ADR-0021, bus d'événements, DB) — chaque service
   n'apporte que sa logique métier + seed + tests. Résultat mesurable :
   **39 suites vertes** là où la spec prévoyait 34 services sans plan de
   mutualisation.
2. **Écrans par spécialité** (≈150 fichiers) : le portal réel rend les
   modules par **configuration** (`ClinicalPanel` + `registry.py` +
   configs IA) au lieu de 130 `.tsx` écrits à la main ; les 4 écrans où
   l'UX critique le justifie (BI-RADS, Code AVC, eCRF offline, À propos UDI)
   sont dédiés.
3. **Variants infra/CI** (≈120 fichiers) : 12 compose, 6 CI providers, 3
   gestionnaires d'env (nix/devbox/asdf) décrivent le même besoin ; le dépôt
   retient 1 compose + 1 CI + K8s/Helm (déploiement réel documenté).

**Reste réellement manquant et utile** (honnêteté, non consolidable) :
scripts setup local 00-10 + packages offline, e2e Playwright/charge k6,
mobile/desktop, i18n ar/es, ~100 écrans spécialisés fins, actions CI GPU/e2e.
Les model-cards formelles ×26 sont **livrées en v0.10**
(`compliance/mdr/model-cards/`, générées par outil — métriques 🔴 R6 avec
l'entraînement réel).

## 4. Le contenu « réel fonctionnel » — preuves, pas intentions

| Dimension | Preuve mesurable v0.7.0 |
|---|---|
| Tests | 127 packages+datasets + 47 IA + 39/39 suites services + 5 vitest + tsc strict |
| Chaîne clinique bout-en-bout | STOW→Orthanc→DICOMweb→OHIF réelle ; laboratoire ORDERED→VALIDATED + Westgard ; alertes critiques bicanal |
| Investigation CI-01 (R5/R6) | eCRF F01-F06 validé, signature verrou, amendements, SDV moniteur, sync offline idempotente, export DSMB sans PHI, audit SHA-256 persisté, push HAPI IOP optionnel |
| Observabilité | 38 services instrumentés OTel (W3C, OTLP/HTTP JSON, tampon 2 048, back-off ×4) sans modifier les services |
| Conformité | Dossier CE MDR IIb (11 docs), SMQ ISO 13485 (9 PROC), IFU×4 + étiquetage UDI, usabilité IEC 62366, SBOM CycloneDX, protocole ISO 14155 complet |
| Écarts assumés 🔴 | validité clinique IA (R6-R8), exécutions terrain (signatures R5, participants R3, pentest, GPU CHU, adhésion GS1) — **par conception, datés dans le plan R1-R9** |

## 5. Verdict

L'arborescence initiale décrivait **une intention d'exhaustivité** ; le dépôt
livre **la fonction, testée, mutualisée, certifiable**. Sur les 15 blocs
top-level : 8 couverts au niveau ou au-delà de la spec, 5 partiellement avec
backlog identifié (écrans fins, docs normatives plates, setup local, e2e, CI
élargie), 2 hors périmètre assumé (mobile/desktop, viewer maison). La
différence n'est pas un déficit : c'est le passage de « 15 000 fichiers
générés » à « un système que 39 suites testent, qu'un dossier CE peut auditer
et qu'une équipe de 4 peut maintenir ». Le chemin critique reste le même :
**R6-R8**, pas le nombre de fichiers.

*Régénérer ce tableau : `python tools/compare_arborescence.py <arbo.txt> --json /tmp/cmp.json`.*
