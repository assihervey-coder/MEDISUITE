# §3-4 — EGSP : Exigences générales de sécurité et de performance (MDR Annexe I)

> Tableau EGSP réduit aux lignes applicables à un logiciel SaaS médical IIb.
> Chaque exigence cite la **preuve existante** dans le dépôt (fichier/test) ou
> le livrable à produire (🔴). Principe directeur MDR art. 5 : réduction du
> risque *autant que possible*, pas seulement « raisonnable ».

## 1. Exigences générales (§1-§8 Annexe I)

| EGSP | Exigence | Preuve MEDISUITE | État |
|---|---|---|---|
| 1 | Éliminer/réduire les risques par conception intrinsèque | architecture fail-closed RBAC, validation stricte entrées (UID DICOM regex, pydantic), tests adverses (payloads malveillants → 422) | 🟠 |
| 3 | Réduction du risque par mesures de protection | chaîne d'audit SHA-256 vérifiable (`audit_chain.py` + tamper-demo), alertes critiques bicanale | 🟠 |
| 4 | Information d'utilisation (IFU) | `intended-purpose.md`, docs modules ; IFU formelle à rédiger | 🔴 |
| 5 | Performance conforme à la finalité | 373+ tests automatisés ; seuils de performance à fixer (latence inférence) | 🟠 |
| 7 | Pas d'interaction indésirable (interférence) | isolation par service, timeouts clients (3 s), dégradation gracieuse PACS/FHIR | 🟢 |
| 8 | Matériaux/corps étrangers | n/a — logiciel | n/a |
| 10 | Seuils et limites de sécurité | fenêtres thérapeutiques codées dans `clinical-rules` (rtPA 4,5 h, ASPECTS), garde-fous affichés | 🟠 |
| 14.2 | Interface utilisateur ergonomique | écrans React/TS typés, i18n fr/en ; évaluation formelle usabilité IEC 62366 à mener | 🔴 |
| 15 | Dépendances logicielles | dépendances stdlib d'abord ; SBOM à générer | 🔴 SBOM |
| 17 | Protection contre usage non autorisé | JWT HS256 + MFA TOTP RFC 6238, RBAC 10 rôles fail-closed prouvé par tests | 🟢 |
| 17.2 | Protection données personnelles | RGPD art. 7 consentements révocables, pseudonymisation, scrypt, chaîne d'audit IEC 81001-5-1 | 🟠 |
| 18 | Fiabilité/continuité | dégradation gracieuse documentée (PACS, FHIR), HPA K8s, restart policies | 🟠 |
| 20.4 | Statut : sémantique versionnel + tags Git v0.1→v0.4 | 🟢 |
| 23 | Instructions d'utilisation | README + docs/ (12 documents) ; IFU patient-CLINICIEN formalisé | 🔴 |

## 2. Exigences de performance (§1, 5, 8.1, 9, 23)

| Domaine | Exigence mesurable | Méthode de V&V | État |
|---|---|---|---|
| Aide décision (scores) | exactitude vs référentiels cliniques cités (qSOFA, GCS, Wells, NIHSS…) | 90+ scores unitaires dans `clinical-rules` avec cas de test par référentiel | 🟢 |
| Fusion multimodale | équivalence numpy/torch prouvée (rtol 1e-6), convergence d'apprentissage (accuracy 100 % cas synthétique) | `test_torch_fusion.py` 16/16 | 🟢 |
| Imagerie | conformité DICOMweb PS3.18 (STOW/QIDO/WADO) | suite imaging 12/12 + Orthanc réel | 🟢 |
| Interopérabilité | HL7 v2.5 roundtrip + ACK, FHIR R4 validate | tests HL7 100 %, validation HAPI REQUIRE | 🟢 |
| Latence inférence | ≤2 s p95 par requête de fusion (GPU time-sliced) | à mesurer sur banc CHU | 🔴 |
| Traçabilité | 100 % des accès patient journalisés, chaîne vérifiable | `audit_chain` + test d'altération | 🟢 |

## 3. Preuves de test automatisées (panorama v0.4)

| Suite | Couverture | Résultat |
|---|---|---|
| packages core+rules+fusion | JWT/TOTP/RBAC/HL7/FHIR/audit/fusion numpy | 81/81 |
| fusion torch (ADR 0022-0023) | équivalence, gradients, checkpoints | 47/47 |
| 38 services FastAPI | RBAC fail-closed, workflows, seeds | 268/268 |
| integration-service v0.4 | HAPI relais + OTel spans/OTLP | 12/12 |
| web-portal | tsc strict + build Vite | exit 0 |

## 4. Écarts à combler avant v1.0.0 (extraits de GAP-ANALYSIS)

1. 🔴 IFU par profil d'utilisateur (clinicien, technicien, admin, patient).
2. 🔴 SBOM + gestion des vulnérabilités des dépendances (Tor, MONAI, HAPI).
3. 🔴 Benchmarks de latence/charge sur matériel cible (banc d'essai CHU).
4. 🟠 Vault + TLS mTLS + tests d'intrusion (RGPD art. 32).
5. 🟠 DPIA complets pour les 5 modules à données sensibles maximales.

Chaque écart est relié à un jalon du plan `08-plan-validation-v1.0.0.md` —
aucune exigence EGSP n'est orpheline : soit prouvée, soit planifiée avec
responsable et date.
