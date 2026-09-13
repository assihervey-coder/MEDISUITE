# ADR-0024 — Profils FHIR nationaux IOP-CI (StructureDefinitions candidats)

**Statut** : accepté (v0.5) · **Date** : 2026-09-14 · **Décideurs** : ingénierie + direction
**Supersede** : extension de ADR-0005 (FHIR R4)

## Contexte

Le référentiel central FHIR (v0.4, HAPI JPA) utilise les profils HL7 de
base. Or l'interopérabilité nationale ivoirienne (cadre IOP du Ministère de
la Santé, articulation DHIS2/CNAM/CHU) exige des identifiants et sémantique
locaux : identifiant national de santé (OID déjà posé dans le code :
`urn:oid:2.16.840.1.113883.2.8.8.10.10`), CNAM (couverture maladie
universelle), régions sanitaires. La publication officielle des
`StructureDefinition` nationales est **en cours côté autorité** — attendre
serait un risque projet (audit R1-R10), avancer sans cadre serait un risque
d'interopérabilité.

## Décision

1. Créer des **profils candidats** `CI-IOP-*` dans
   `services/integration-service/fhir/profiles/` :
   - `StructureDefinition-Patient-CI-IOP.json` — Patient avec identifiant
     national obligatoire, CNAM secondaire, nom ivoirien (family/prenoms),
     région sanitaire (extension), sexe et date de naissance contraints ;
   - `StructureDefinition-Observation-CI-IOP.json` — Observation labo
     (LOINC + UCUM obligatoires, sujet Patient-CI-IOP) ;
   - `CodeSystem-CI-identifiants.json` + `ValueSet-CI-identifiants.json`
     (systèmes d'identifiants nationaux) ;
   - exemples + `implementation-guide.md`.
2. Contraintes exposées **côté hub** (`integration-service`) : validation
   d'identifiant national avant tout POST vers HAPI (`validate_national_id`),
   endpoint `/api/v1/fhir/profiles` documentant les profils servis.
3. **Base canonique des identifiants** : un seul système par patient,
   OID national en premier, CNAM en secondaire — tout doublon est refusé.

## Justification

- Profils candidats = antériorité et influence sur le cadre national tout
  en restant conformes R4 (dérive zéro : extensions dans des slices
  documentées) ;
- Migration triviale quand les StructureDefinition officielles publient :
  `url` canoniques à substituer, mappings inchangés ;
- Cohérent avec « stdlib d'abord » : profils JSON déclaratifs + fonctions
  de validation simples, testables sans serveur.

## Alternatives écartées

- **Attendre la publication officielle** : bloque l'investigation clinique
  (jalon R5) et le pilote CHU.
- **Imposer HL7 international pur** : les identifiants nationaux sont
  indispensables à la facturation CNAM et au DHIS2 — non viables à l'échelle.
- **Fork du serveur HAPI avec profils en dur** : complexité d'exploitation
  incompatible avec le contexte CHU ; les profils restent des artefacts
  versionnés du dépôt.

## Conséquences

- Les services écrivent via les mappings `medisuite_core.fhir` enrichis
  (`national_id` obligatoire) — tests mis à jour.
- Toute évolution des profils passe par revue (PROC-03) + ADR successor.
- Limites déclarées : OID nationaux plausibles mais **non enregistrés
  officiellement** (registre HL7 en attente) ; régions sanitaires : liste
  13 régions (donnée ouverte MoH) à confirmer.
