# §6 — Cycle de vie logiciel (IEC 62304:2006+A1 + IEC 81001-5-1) — classe de sécurité C

## 1. Classe de sécurité du logiciel (IEC 62304 §4.3)

**Classe C** : « une défaillance peut causer la mort ou une détérioration
grave de l'état de santé » — cohérent avec la classification IIb règle 11
(sécabilité AVC, BI-RADS 4-6). Argumentaire : les segments administratifs
seuls justifieraient la classe B, mais la plateforme est libérée comme un
système unique (décision ADR-0004 et §1 classification) → tout le socle est
développé au niveau d'exigence C. Ce choix prudent, plus coûteux en preuves,
élimine les frontières fragiles de segmentation.

## 2. Correspondance processus IEC 62304 ↔ implémentation MEDISUITE

| Processus IEC 62304 | Exigence classe C | Réalisation MEDISUITE | État |
|---|---|---|---|
| 5.1 Développement plan | plan logiciel documenté | ce document + ADRs + roadmap versionnée | 🟠 |
| 5.2 Exigences système | exigences tracées aux risques | EGSP `02-gspr-annexe-I.md` (matrice exigence↔preuve) | 🟠 |
| 5.3-5.4 Architecture | décomposition + interfaces | 38 services FastAPI, contrat unique `create_service_app`, ADR 0001-0023 | 🟢 |
| 5.5 Détail conception | unités critiques documentées | `clinical-rules` (90+ scores citant référentiels), `FusionEngine`, `audit_chain` | 🟠 |
| 5.6-5.7 Implémentation + intégration | unit tests, intégration | 373+ tests automatisés, CI GitHub Actions | 🟢 |
| 6 Validation processus | outils de développement validés | tsc strict, pytest, validation YAML de config ; environnement reproducible | 🟠 |
| 7 Gestion des risques | lien risques ↔ code | FMEA `03-analyse-risques-iso14971.md` avec IDs RM-* cités dans les ADRs | 🟠 |
| 8 Résolution de problèmes | revue des défaillances | issues Git + CHANGELOG ; registre des incidents à instaurer 🔴 | 🟠 |

## 3. Preuves de vérification & validation (V&V) existantes

| Niveau | Preuve | Résultat |
|---|---|---|
| Unitaire (packages noyau) | JWT HS256 contre vecteurs RFC, TOTP RFC 6238, RBAC fail-closed, HL7 parse/build, FHIR mapping, chaîne d'audit avec test d'altération | 81/81 |
| Unitaire (règles cliniques) | chaque score testé contre un cas de son référentiel (ESI, qSOFA, GCS, NIHSS, ASPECTS, BI-RADS, CURB-65, KDIGO…) | 90+ scores verts |
| Unitaire (IA) | FusionEngine numpy déterministe ; équivalence torch/numpy (allclose rtol 1e-6) ; gradients finis sur blocs actifs et None attendus sur inactifs ; checkpoint bit-à-bit | 47/47 |
| Intégration services | RBAC réel (vrais JWT), workflows complets (ORDERED→VALIDATED, STOW→QIDO), idempotence, valeurs critiques | 268/268 |
| Intégration interopérabilité | HAPI relais (opener factice + serveur réel en compose), OTel spans + payload OTLP conforme | 12/12 |
| UI | compilation TS strict sans `any`, build Vite | exit 0 |

## 4. IEC 81001-5-1 (cycle de vie des logiciels de santé incluant sécurité)

- **Traçabilité des données de santé** : registre d'audit chaîné SHA-256
  (`audit_chain.py`) avec vérification d'intégrité et démonstration de
  falsification (`tamper-demo`) — extension aux flux HL7/DICOM prévue 🔴.
- **Gestion de configuration** : Git monorepo, tags sémantiques v0.1→v0.4,
  ADRs numérotés immuables, DVC pour les jeux de données d'entraînement.
- **Chaîne d'approvisionnement logicielle** : dépendances stdlib d'abord,
  images versionnées épinglées (orthancteam:24.9, collector:0.109.0,
  ohif/app:v3.8.3) ; SBOM et scan CVE 🔴 (v1.0, EGSP §15).

## 5. Frontière entre développement et libération (release)

Processus de libération d'une version (ex. v0.4.0) :
1. CI verte sur les 4 niveaux ci-dessus (bloquant) ;
2. revue des nouveaux risques (FMEA mise à jour — liens RM-*) ;
3. migration de schéma SQL testée sur copie ;
4. tag Git + CHANGELOG (Keep a Changelog) ;
5. note de version aux utilisateurs pilotes (CHU) — feedback PMS.

Ce processus, aujourd'hui documenté et partiellement automatisé, sera
formalisé en procédure ISO 13485 (🔴 `09-smq-iso13485.md`).

## 6. Écarts honnêtes

Le dossier V&V de classe C exige aussi : revue formelle de conception
(documentée, signée), couverture de code cible (recommandé ≥80 % sur les
unités critiques — mesuré mais non archivé), et tests de robustesse
malveillante systématiques (partiellement : payloads DICOM/HL7 adverses).
Trois chantiers 🔴 tracés dans `08-plan-validation-v1.0.0.md`.
