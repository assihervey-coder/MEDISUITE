# eCRF FHIR opérationnel — investigation MEDISUITE-CI-01 (R5/R6)

> v0.7.0 · Jalon R6 « outillage eCRF » : 🟢 implémenté et testé
> (80 tests associés : noyau `ecrf.py` + service + intégration).
> L'EXÉCUTION (inclusions réelles, monitoring terrain) reste 🔴 jusqu'au
> feu vert R6 (soumissions ANOC-CI/PACTR/Ministère + accords sites).

## Ce que ce module couvre

Le §8 du protocole `10-protocole-investigation-multicentrique-R5.md`
exige un eCRF : formulaires basés sur les profils FHIR IOP (ADR-0024),
contrôles de cohérence à la saisie, audit chaîné SHA-256 natif,
saisie possible malgré les coupures réseau des sites CHU. C'est
implémenté de bout en bout :

```
web-portal (écran /ecrf, offline-first)
    │  POST /api/ecrf/... (Idempotency-Key)
    ▼
api-gateway :8000  ──proxy──▶  ecrf-service :8205
                                 │ validation medisuite_core/ecrf.py (§8)
                                 │ SQLite/PostgreSQL (sujets, entrées, requêtes)
                                 │ audit chaîné SHA-256 (ADR-0021, persisté)
                                 │ → (option) bundle FHIR R4 IOP → hub HAPI site
                                 ▼
                            export DSMB agrégé (sans PHI)
```

## Modèle de données

- **Sujet pseudonyme** : `CI01-<SITE>-NNNNN` (COC/TRI/YOP/BOU). Aucun nom
  ne transite — la correspondance reste sous scellé site (§6 protocole).
- **Formulaires** (source unique : `medisuite_core/ecrf.py FORMS`) :

| ID | Contenu | Rôle de saisie | Dérivations |
|---|---|---|---|
| F01-INCLUSION | consentement (écrit/différé urgence), âge, grossesse, perte modalités, doublon, panne | investigateur | éligibilité §4.2/§4.3 |
| F02-BASELINE | sexe, tranche d'âge, provenance, comorbidités | investigateur | — |
| F03-DECISION | décisions standard/finale, adhésion, sorties dispositif, horodatages | investigateur | délai P3 (minutes) |
| F04-SUIVI30J | statut 30 j, EI/SAE liés dispositif, hospitalisation | investigateur | sûreté P2 |
| F05-ADJUDICATION | verdicts, certitude 1-5, tierce arbitre, dossier complet | **adjudicateur uniquement** | référence §3.3 |
| F06-DEVIATION | type, description, impact évaluabilité | investigateur | registre déviations |

- **Séparation des rôles (fail-closed)** : le comité d'adjudication (aveugle)
  ne peut saisir QUE le F05 (`ecrf.adjudicate`) ; les investigateurs ne
  peuvent JAMAIS saisir le F05. Rôles ajoutés au RBAC v0.7 : `investigateur`,
  `moniteur`, `adjudicateur`, `data_manager`, `promoteur` (+ eCRF pour
  `medecin`).
- **Cycle de vie** : `brouillon` → signature investigateur (`ecrf.sign`,
  verrou ISO 14155 §4.8) → amendement = **nouvelle version** avec
  `parent_id` ; l'original signé reste intact et consultable.

## Idempotence et mode offline

Chaque saisie est dédoublonnée par **clé calculée serveur**
`SHA-256(étude|sujet|formulaire|payload canonique)` — un rejeu ne crée
jamais de doublon. Le portal empile les saisies hors-ligne dans IndexedDB
et les rejoue (endpoint `POST /api/v1/ecrf/sync`, lots ≤ 200) avec
`Idempotency-Key` client. Résultat **par item** : `created` / `duplicate` /
`error` (détails de validation) / `rejected` — un lot ne bloque jamais.
Voir `docs/OFFLINE-PORTAL.md`.

## Endpoints (ecrf-service :8205, RBAC fail-closed)

| Méthode | Chemin | Permission |
|---|---|---|
| GET | `/api/v1/ecrf/forms` | `ecrf.read` |
| POST | `/api/v1/ecrf/subjects` | `ecrf.write` |
| GET | `/api/v1/ecrf/subjects[?site=&scenario=&statut=]` | `ecrf.read` |
| GET | `/api/v1/ecrf/subjects/{code}` | `ecrf.read` |
| POST | `/api/v1/ecrf/subjects/{code}/forms/{form_id}` | `ecrf.write` (F05 : `ecrf.adjudicate`) |
| POST | `/api/v1/ecrf/entries/{id}/sign` | `ecrf.sign` |
| POST | `/api/v1/ecrf/entries/{id}/amend` | `ecrf.write` |
| GET/POST | `/api/v1/ecrf/queries` (+ `/{id}/close`) | `ecrf.monitor` (ouverture) / `ecrf.write` (clôture) |
| POST | `/api/v1/ecrf/sync` | `ecrf.write` |
| GET | `/api/v1/ecrf/exports/dsmb` | `ecrf.export` |
| GET | `/api/v1/ecrf/audit/verify` | `audit.read` |

## Poussée FHIR (ADR-0024)

`MEDISUITE_ECRF_FHIR_PUSH=1` active la poussée transaction d'un bundle
R4 par entrée vers le hub HAPI du site (`MEDISUITE_FHIR_BASE`) :
Patient pseudonyme (profil Patient-CI-IOP, identifiant = code étude) +
une Observation-CI-IOP par champ (CodeSystem étude) + observation
d'éligibilité dérivée. Statuts gracieux par entrée : `pousse`,
`erreur_hapi`, `hors_ligne` (saisie locale toujours préservée),
`desactive` (défaut).

## Export DSMB (trimestriel, §6)

Comptages dérivés sans aucune donnée libre ni PHI : sujets par
site/scénario/statut, entrées par formulaire, EI/SAE liés dispositif
(règle d'arrêt A5 rappelée), médiane du délai d'orientation (P3),
répartition d'adhésion. Aucune donnée nominative : les extractions de
niveau enregistrement passent par l'extraction data manager ci-dessous.

## Verrou de base M+18 et extraction data manager (v0.8, §7.4/SAP A5)

**Verrou** (`POST /api/v1/ecrf/study/lock`, permission `ecrf.lock` =
promoteur) : fige la base à la fin des suivis 30 j avec **≥ 2 témoins**
(protocole §8 : verrou + témoins) et **zéro requête de monitoring
ouverte** (plan-monitoring §5). Il calcule un **checksum SHA-256 de
l'état complet** — sujets + entrées, chaque payload haché à partir de
son **contenu canonique recalculé** (`canonical_payload`), pas d'un hash
stocké : toute altération directe de la base modifie le checksum.
Effets, irréversibles (aucun déverrouillage n'existe — EGSP) :
- toute écriture (inclusion, saisie, amendement, sync) → **409** ;
- l'**extraction d'analyse** est débloquée ;
- l'événement `ecrf.study.locked` est publié et l'action audité
  (chaîne SHA-256 persistée).

**Extraction** (`GET /api/v1/ecrf/extract`, permission `ecrf.extract` =
data manager uniquement ; promoteur, investigateur, moniteur → 403) :
- **409 avant le lock** — verrouillage prérequis (§7.4) ;
- après lock : SAF pseudonymisé — dernière entrée **SIGNÉE** par
  (sujet, formulaire), dérivations SAP recalculées (éligibilité F01,
  délai P3 F03, SAE F04), checksum re-vérifié à chaque appel ;
- si l'état courant diverge du checksum verrouillé → **500 alarme
  d'intégrité** + événement `ecrf.extract.integrity` audité (investigation
  requise avant toute analyse R7) ;
- `GET /api/v1/ecrf/study/status` (ecrf.read) : état du verrou, témoins,
  compteurs, checksum courant indicatif avant lock.

RBAC ajouté v0.8 : `ecrf.lock` (promoteur), `ecrf.extract` (data
manager) — séparation stricte : celui qui verrouille n'extrait pas.

## Ce qui reste 🔴 (terrain)

- R6 : feu vert ANOC-CI/Ministère, accords sites, formation PROC-06,
  inclusions réelles.
- Monitoring de terrain (visites annexe A4) : l'outil de requêtes SDV
  est opérationnel et les **instruments sont rédigés** (plan, rapport de
  visite A4, registre des déviations — `compliance/mdr/clinical/monitoring/`) ;
  la VISITE elle-même reste humaine.
- Pilotage des soumissions : checklists ANOC-CI / PACTR /
  Ministère-DPIA prêtes (`compliance/mdr/submissions/`) — dépôts réels
  🔴 (jalon R5, M+3).
- Le lock M+18 s'exécutera en fin d'étude (promoteur + témoins) —
  l'OUTILLAGE est 🟢, l'opération est 🔴 terrain.
