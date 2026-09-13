# Checklists — Autorisation Ministère + DPIA (loi n° 2013-450)

> Deux volets complémentaires du jalon R5 : (I) l'autorisation d'exécution
> de l'investigation clinique auprès du Ministère de la Santé et de l'Hygiène
> publique ; (II) l'analyse d'impact relative à la protection des données à
> caractère personnel (DPIA) au titre de la loi ivoirienne n° 2013-450.
> Statuts : 🔴 à produire / 🟠 en cours / 🟢 prêt (preuve liée).

## I. Autorisation Ministère de la Santé

| # | Item | Artefact / source | Statut |
|---|---|---|---|
| M1 | Lettre de demande d'autorisation d'investigation clinique (promoteur) | à rédiger sur papier entête promoteur | 🔴 |
| M2 | Copie de l'avis ANOC-CI (dès obtention — prérequis usuel) | soumission ANOC d'abord | 🔴 dépendant |
| M3 | Protocole versionné + notice/consentement | TD-10 + annexe A2 | 🟢 |
| M4 | Brochure investigateur du dispositif | à assembler (TD 02 + IFU) | 🟠 |
| M5 | Liste des sites d'investigation (CHU-Cocody, Treichville, Bouaké) + lettres d'accord des directions | accords annexe A6 | 🔴 |
| M6 | Identité et qualifications de l'investigateur coordinateur | CV (A3 ANOC) | 🔴 |
| M7 | Dispositif : description, classe (MDR IIb, règle 11), Basic UDI-DI, statut de certification | `01-identification-classification.md` — cert CE 🔴 (investigation art. 62-80) | 🟢 identification prête |
| M8 | Procédure vigilance/incidents (24 h / ≤ 7 j ; MDR art. 87-90 si DM impliqué) | protocole §9 + `07-pms-vigilance.md` | 🟢 |
| M9 | Assurance des participants (attestation) | contrat assurance §9.2 | 🔴 |
| M10 | Dépôt + suivi (accusé, questions-réponses, autorisation signée) | à exécuter M+3 → M+4 | 🔴 |

## II. DPIA — loi n° 2013-450 relative à la protection des données

| # | Item | Artefact / source | Statut |
|---|---|---|---|
| D1 | Description du traitement : finalité (recherche clinique), bases, catégories de données | protocole §6 (pseudonymisation native eCRF) | 🟢 |
| D2 | Cartographie des flux : sites CHU → eCRF → HAPI FHIR site → export DSMB (sans PHI) → analyse | `docs/E-CRF.md` + `docs/FHIR-HAPI.md` | 🟢 |
| D3 | Minimisation : codes pseudonymes CI01-, jamais de nom ; modalités ≤ 1 (ADR-0018) ; DSMB agrégé | eCRF v0.7 (tests 18/18) | 🟢 |
| D4 | Durées de conservation : données investigation 25 ans (dossier d'investigation) | plan-monitoring §4 | 🟢 |
| D5 | Mesures de sécurité : JWT HS256, RBAC fail-closed par rôle étude, MFA, audit chaîné SHA-256, offline IndexedDB pseudonyme + dead-letter | `02-gspr-annexe-I.md` + `docs/OFFLINE-PORTAL.md` | 🟢 |
| D6 | Transferts : hébergement des hubs HAPI **dans les sites** ; pas de transfert international identifiant | architecture protocole §6 | 🟢 |
| D7 | Analyse de risque droits/libertés + mesures résiduelles (FMEA RM-01…RM-10 croisée) | `03-analyse-risques-iso14971.md` | 🟠 à formaliser en format DPIA |
| D8 | Information des participants (notice : données, droits, contact DPO/autorité) — baoulé/dioula | annexe A2 + C3 ANOC | 🔴 dépendant traduction |
| D9 | Consultation de l'autorité de protection si risque résiduel élevé | décision promoteur après D7 | 🔴 |
| D10 | Validation DPIA signée + intégration au dossier d'investigation | à exécuter M+4 | 🔴 |

## Ordre de dépendance (chaîne critique)

```
 Assurance (M9) ──┐
 Accords CHU (M5) ─┼─► ANOC-CI (avis) ──► Ministère (M1-M10) ──► PACTR (24 items) ──► FEU VERT INCLUSIONS (M+6)
 DPIA (D1-D10) ────┘
```

Toute modification ultérieure du traitement de données (ex. ajout d'un
service IA en cours d'étude) → révision DPIA + amendement protocole +
information ANOC/Ministère selon la matrice du §12 (amendements).
