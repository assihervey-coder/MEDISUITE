# Serveur FHIR R4 — HAPI JPA (v0.4)

Le référentiel central d'interopérabilité de MEDISUITE est un **serveur HAPI
FHIR JPA réel** (`hapiproject/hapi`), hérité de la cible ADR-0005 : tous les
flux inter-établissements (CHU, centres de santé, laboratoires privés)
convergent vers ce référentiel conformément au standard **HL7 FHIR R4
(4.0.1)**. Ce document décrit l'architecture, le démarrage, les règles de
sécurité et les limites connues de l'implémentation v0.4.

## 1. Architecture

```
┌──────────────┐  REST interne   ┌─────────────────────┐
│ patient-…    │────────────────▶│ integration-service │
│ laboratory-… │  (HL7 v2/FHIR)  │  (hub FHIR R4)      │
└──────────────┘                 └──────────┬──────────┘
                                            │ POST/GET /Patient
                                            │ (application/fhir+json)
                                            ▼
                                ┌─────────────────────┐
                                │  hapi-fhir (HAPI    │
                                │  JPA, port 8090)    │
                                │  validation R4 ON   │
                                └──────────┬──────────┘
                                           │ JDBC
                                           ▼
                                ┌─────────────────────┐
                                │ postgres-hapi:5432  │
                                │  (volume persistant)│
                                └─────────────────────┘
```

- **mapping interne → FHIR** : `medisuite_core.fhir` (Patient, Observation,
  Condition, Encounter, AllergyIntolerance) — déjà éprouvé v0.1 ;
- **client REST** : `medisuite_core.hapi_client.HapiClient` — stdlib
  uniquement (`urllib`), injection d'opener pour les tests, dégradation
  gracieuse quand le référentiel est hors ligne (ping() → False, aucune
  exception remontée aux cliniciens) ;
- **relais** : le hub `integration-service` expose `/api/v1/fhir/server/*`
  et applique le RBAC fail-closed avant tout appel sortant.

## 2. Démarrage

```bash
docker compose -f local-deployment/docker-compose.minimal.yml up hapi-fhir
# UI FHIR embarquée (HAPI Testpage) : http://localhost:8090
# CapabilityStatement :               http://localhost:8090/fhir/metadata
```

Vérification de santé :

```bash
curl -s http://localhost:8090/fhir/metadata | jq -r '.fhirVersion'   # → 4.0.1
```

Endpoints du hub (jeton JWT requis — voir auth-service) :

| Endpoint | Méthode | RBAC | Effet |
|---|---|---|---|
| `/api/v1/fhir/server/status` | GET | `patient.read` | joignabilité + version R4 |
| `/api/v1/fhir/server/metadata` | GET | `patient.read` | CapabilityStatement relayé |
| `/api/v1/fhir/server/patients` | GET | `patient.read` | recherche `family`/`identifier` |
| `/api/v1/fhir/server/patients` | POST | `patient.write` | création Patient (201) + événement bus |

## 3. Sécurité et conformité

1. **RBAC fail-closed** : `rbac.can(role, permission)` avant chaque relais ;
   rôle inconnu → 403 (aucun accès par défaut) — prouvé par tests.
2. **Validation serveur** : HAPI tourne avec `validation.enabled: true` et
   `request_level: REQUIRE` — une ressource malformée est rejetée au portail
   du référentiel, pas seulement côté MEDISUITE (défense en profondeur).
3. **Aucune donnée dans le code** : la base et l'index Lucene vivent dans le
   volume `hapi-data` ; mots de passe par variables d'environnement compose
   (à remplacer par secrets Vault/Keycloak avant production — v1.0).
4. **Pseudonymisation** : le mapping interne conserve `numero_dossier` en
   identifiant (`urn:oid:2.16.840.1.113883.2.8.8.10.10`) ; le CNAM reste un
   identifiant secondaire, jamais une clé publique du référentiel.

## 4. Limites connues (honnêteté d'ingénieur)

- **Pas de profils nationaux IOP CI** : les `StructureDefinition` du MINISTÈRE
  de la Santé (à paraître) seront ajoutés en v1.0 ; la base utilise les
  profils HL7 de base.
- **Authentification HAPI non branchée** : le serveur tourne sans SMART
  on FHIR / OAuth2 ; l'ingress doit bloquer l'accès direct en production et
  laisser passer le hub uniquement (NetworkPolicy K8s prévue avec la v0.4 GPU).
- **Pas de souscription active dans la CI** : `resthook_enabled: true` est
  configuré mais aucun abonné n'est enregistré par défaut.
- **Volume** : PostgreSQL 16 conteneurisé sans réplication — pour un CHU,
  basculer sur la base managée K8s (StatefulSet + sauvegardes) avant validation
  clinique.

## 5. Tests

`services/integration-service/tests/test_integration.py` : 12 tests, dont 5
pour HAPI (statut hors ligne, metadata relayé, recherche bundle, création +
RBAC fail-closed auditeur → 403, mapping FHIR du payload envoyé) — opener
factice, aucun serveur requis en CI.
