# Implementation Guide CI-IOP (candidat) — résumé v0.5

> Candidat ADR-0024 : guide d'implémentation FHIR national Côte d'Ivoire
> en attente de publication officielle. Toute réutilisation exige la
> confirmation de l'autorité sanitaire (OIDs, régions).

## 1. Profils et artefacts

| Artefact | URL canonique | Fichier |
|---|---|---|
| Patient-CI-IOP | `http://medisuite.ci/fhir/StructureDefinition/Patient-CI-IOP` | `StructureDefinition-Patient-CI-IOP.json` |
| Observation-CI-IOP | `http://medisuite.ci/fhir/StructureDefinition/Observation-CI-IOP` | `StructureDefinition-Observation-CI-IOP.json` |
| CS identifiants | `http://medisuite.ci/fhir/CodeSystem/CI-identifiants` | `CodeSystem-CI-identifiants.json` |
| VS identifiants | `http://medisuite.ci/fhir/ValueSet/CI-identifiants` | `ValueSet-CI-identifiants.json` |
| Exemple patient | — | `example-patient-ci-iop.json` |

## 2. Contraintes clés (résumé différentiel)

**Patient-CI-IOP** : `identifier` au moins 1 (slice `national` exactement 1,
système OID national, valeur `^[A-Z0-9]{10,16}$`) ; slice `cnam` 0-1
(10 chiffres) ; `name.family` + `name.given` + `gender` + `birthDate`
obligatoires ; extension `region-sanitaire` (string, liste validée côté hub).

**Observation-CI-IOP** : `code.coding.system` obligatoire (LOINC préféré),
`subject` référence Patient-CI-IOP, `effectiveDateTime` obligatoire,
`valueQuantity.system` fixé à UCUM, `referenceRange` 0-1.

## 3. Validation en deux niveaux (défense en profondeur)

1. **Hub** (`integration-service`) : `medisuite_core.iop.patient_to_iop`
   rejette toute non-conformité AVANT l'appel réseau (422 avec détail) —
   tests unitaires sans serveur.
2. **Serveur HAPI** : `validation.enabled: true` (REQUIRE) revalide contre
   les profils de base HL7 — les profils CI-IOP peuvent être chargés dans
   HAPI via `hapi.fhir.initial_data` ou l'API `/StructureDefinition`.

## 4. Cycle de vie des profils

1. v0.5 : candidats draft dans le dépôt (ce répertoire), catalogue servi
   par `GET /api/v1/fhir/profiles`.
2. À la publication officielle du cadre national : substitution des `url`
   canoniques + registre HL7 des OIDs (ADR-0024 §conséquences).
3. Toute modification : revue de conception (PROC-03) + ADR successor.

## 5. Limites

- OIDs plausibles non enregistrés officiellement.
- Liste régionale partielle (17/31 + 2 districts) — fail-closed jusqu'à
  confirmation du découpage officiel.
- Extension `region-sanitaire` simple string : à remplacer par un
  `CodeSystem` régional complet quand disponible.
