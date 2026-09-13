# Journal des changements — MEDISUITE

Format Keep a Changelog ; versionnement sémantique ; les numéros de release
correspondent aux tags Git.

## [v0.3.0] — 2026-09-13

### Visualiseur OHIF v3 branché sur /dicom-web
- **Chaîne d'imagerie réelle de bout en bout** : STOW → Orthanc → DICOMweb
  (PS3.18) → OHIF → lecture diagnostique. Conteneur `ohif-viewer`
  (`ohif/app:v3.8.3` surchargé) dans `docker-compose.minimal.yml`, UI port 3001.
- `local-deployment/ohif/app-config.js` : source de données DICOMweb
  `orthanc` (QIDO-RS/WADO-RS en chemins relatifs, lazy-load des études,
  transfert JPEG Lossless).
- `local-deployment/ohif/nginx.conf` : proxy `/dicom-web` + `/wado` →
  `orthanc-pacs:8042` avec **authentification injectée côté serveur** — le
  secret PACS ne quitte jamais le conteneur, aucun CORS, aucune exposition
  navigateur.
- imaging-service : `GET /api/v1/pacs/viewer-url?study_uid=…` — lien profond
  OHIF (`/viewer?StudyInstanceUIDs=…`) avec RBAC `imaging.read` et **validation
  stricte d'UID DICOM** (`^\d+(\.\d+)+$`, anti-injection) ; 4 tests nouveaux.
- web-portal (page Imagerie) : bouton **OHIF ↗** par étude (base surchargeable
  `VITE_OHIF_BASE`).
- Documentation : `docs/OHIF-VIEWER.md` (architecture, démarrage, sécurité,
  limites connues — plugin Keycloak recommandé en production).

### IA — fusion torch ENTRAÎNABLE de bout en bout (ADR 0023)
- `ai/multimodal/core/torch_fusion.py` : `TorchFusionModel` (nn.Module,
  float64) — projections `nn.Linear` par modalité, **cross-attention
  multi-têtes** (`TorchCrossAttention` : Wq/Wk/Wv/Wo, softmax √(d/h)),
  **portes sigmoid nn.Parameter** par modalité, **requête globale apprise**,
  **tête de tâche entraînable** (`TorchTaskHead` : binaire / multiclasse /
  régression).
- **Équivalence NumPy à l'initialisation** (pattern ADR 0022 étendu au tronc) :
  tous les poids copiés du socle déterministe v0.1 — Δ probabilité = 0 au
  premier predict, tenseur `fused` allclose rtol 1e-6 ; divergence uniquement
  par entraînement explicite.
- `fit()` déterministe : Adam, ordre fixe (aucun shuffle), tokenisation gelée
  pré-calculée, pertes BCE-with-logits / CE / MSE, historique retourné —
  démontré sur synthétique séparable : perte 2,01 → 0,16, **accuracy 100 %**,
  deux fits identiques → historiques identiques (zéro RNG).
- Checkpoints natifs `state_dict` + métadonnées (`medisuite-fusion-0.3`) :
  round-trip bit-à-bit testé, prêt pour MLflow.
- `predict()` aux clés identiques à `FusionEngine.infer` (drop-in) :
  importance des modalités APPRISE, recalibrage ADR-0018 conservé, gradient
  épars sur modalités absentes (comportement testé).
- Factory : `fusion_model_from_config()` / `fusion_model_for_module()` ;
  périmètre honnête : survival/segmentation rejetées `NotImplementedError`.
- Suite IA : **16 tests** nouveaux (`test_torch_fusion.py`), tous verts
  (torch 2.14+cpu).

### Divers
- Badge README → v0.3.0 ; 22 ADR → 23 (ADR 0023) ; roadmap mise à jour :
  FHIR R4 (HAPI), télémétrie OTel et K8s GPU reportés en v0.4.0.
- `docker-compose.minimal.yml` : 9 services (+ ohif-viewer).

## [v0.2.0] — 2026-09-13

### Écrans cliniques spécialisés (web-portal)
- **Lecteur BI-RADS** (`/birads`) : lecture mammographique structurée — densité
  ACR a-d, masse, microcalcifications, asymétrie, aire axillaire — catégorisation
  BI-RADS 1-6 avec échelle colorée et conduite à tenir (ACR BI-RADS 5e éd. 2013),
  calcul via oncology-service (moteur `packages/clinical-rules`).
- **Code AVC** (`/code-avc`) : horloge « dernier vu normal » avec bandeau des
  fenêtres thérapeutiques AHA/ASA (alteplase ≤ 4,5 h, thrombectomie ≤ 6 h,
  perfusion 6-24 h DAWN/DEFUSE-3), cotation NIHSS 11 items (0-38), ASPECTS
  10 régions cliquables, checklist des contre-indications à la thrombolyse et
  synthèse d'orientation double validation (neurologue + neuroradiologue).
- `api.postScore` désormais générique (typage strict des réponses) ;
  design system étendu (échelle BI-RADS, bandeau fenêtres, grille ASPECTS,
  bannière go/caution/stop). `tsc -b` strict + build Vite OK.

### IA — backends de calcul (ADR 0022)
- `BaseEncoder.project()` : point d'injection unique des projections
  entraînables ; le socle NumPy déterministe reste le défaut (v0.1 figée).
- Backend **PyTorch** : `TorchProjector` (nn.Linear float64) dont les poids
  sont copiés depuis la matrice stable P → sortie numériquement identique au
  socle NumPy à l'initialisation (tokens allclose rtol 1e-6 ; dict d'inférence
  complet inchangé après branchement — tests à l'appui).
- Backend **MONAI** : prétraitement image canonique (EnsureChannelFirst →
  ScaleIntensity → Resize 64×64 / 32³) inséré dans la tokenisation
  `imaging_2d` / `imaging_3d`.
- Clé YAML `backend: numpy|torch|monai` dans les 26 configurations de modules ;
  import paresseux + `ImportError` documentée ; suite IA : **31/31** avec
  torch 2.14+cpu et MONAI installés.

### PACS — Orthanc réel (ADR 0006 appliqué)
- `services/imaging-service/src/orthanc_client.py` : client REST stdlib
  (urllib/base64) — `system`, `ping`, `studies` (expansion), relais QIDO-RS ;
  configuration par variables `MEDISUITE_ORTHANC_*` ; dégradation gracieuse.
- Endpoints `/api/v1/pacs/status` (jamais 5xx), `/api/v1/pacs/studies`,
  `/api/v1/pacs/qido` ; `integrations` reflète l'état réel. 12/12 tests imaging.
- `docker-compose.minimal.yml` **réparé** (YAML invalide en v0.1 : argument de
  build non quoté, nom de volume incohérent) et Orthanc réel
  `orthancteam/orthanc:24.9` avec configuration complète
  (`local-deployment/orthanc/orthanc.json` : DICOMweb activé, AE `MEDISUITE`,
  modalités de simulation, authentification, volume persistant).
- Documentation : `docs/PACS-ORTHANC.md`.

### Divers
- Badge de version README → v0.2.0 ; 21 ADR → 22 (ajout ADR 0022).

## [v0.1.0] — 2026-09-13

### Fondations
- Monorepo complet : 38 services, 26 modules de spécialités (ports 8100-8123),
  4 passerelles, 5 transverses ; api-gateway avec proxy JWT + token bucket.
- `packages/medisuite-core` : JWT HS256, scrypt, TOTP RFC 6238, RBAC
  fail-closed, audit chaîné SHA-256, HL7 v2.5 (parser + MLLP), FHIR R4,
  bus d'événements, seed ivoirien.
- `packages/clinical-rules` : ~90 scores cliniques tracés vers leurs
  référentiels (ESI/CTMP, qSOFA/SOFA, GCS, Wells, Parkland, ISS, CURB-65,
  CHA2DS2-VASc, HEART, GOLD, CKD-EPI 2021, KDIGO, kt/V, BI-RADS, Fleischner,
  Lung-RADS, AJCC 8e, IOTA, ASPECTS, NIHSS, MMSE, PHQ-9, Westgard…).
- Moteur de fusion multimodale NumPy déterministe : cross-attention softmax
  + gated fusion + MissingModalityHandler, 7 encodeurs, 6 têtes, 26 configs
  YAML ; stack MLOps (MLflow, DVC, Feast, Airflow, Kubeflow, KServe).
- web-portal Vite/React/TS strict + patient-portal RGPD + CLI TypeScript ;
  infrastructure Docker/K8s/Helm/Terraform/ArgoCD/Flux, monitoring Prometheus
  avec alertes cliniques/IA, OPA Rego, realm Keycloak, GAP-ANALYSIS honnête.
- Validation : 373 tests verts (105 packages + 268 services, 38/38 suites).
