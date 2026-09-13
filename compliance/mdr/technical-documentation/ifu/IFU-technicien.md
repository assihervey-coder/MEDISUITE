# Notice d'utilisation (IFU) — Profil TECHNICIEN (exploitation)

> MEDISUITE v0.5 — à valider par l'usabilité sommative. Formation 4 h +
> quiz ≥ 80 % (PROC-06). Support : support@medisuite.ci.

## 1. Périmètre

Installation, supervision, sauvegarde et dépannage de premier niveau de la
plateforme (compose local ou Kubernetes). Les opérations cliniques (comptes,
rôles, corrections) relèvent de l'IFU Administrateur.

## 2. Installation (référence détaillée : README, docs/)

1. Prérequis : Docker ≥ 24 (compose) ou K8s ≥ 1.29 (+ GPU pour l'inférence,
   cf. `docs/K8S-GPU.md`) ; 16 Go RAM minimum (32 Go recommandés) ;
   sauvegarde externe configurée AVANT mise en service.
2. Démarrage : `docker compose -f local-deployment/docker-compose.minimal.yml up -d`
   — 11 services (5 services cœur, Orthanc, OHIF, HAPI FHIR, PostgreSQL,
   OTel collector, Prometheus, Grafana).
3. Vérifications post-install : `/health` de chaque service ; capability
   FHIR `http://localhost:8090/fhir/metadata` → `fhirVersion: 4.0.1` ;
   Orthanc `/system` ; cibles Prometheus (jobs `medisuite-services`, `pacs`,
   `otel`) toutes UP ; Grafana dashboards.

## 3. Supervision quotidienne

| Contrôle | Où | Alarme |
|---|---|---|
| Disponibilité services | Grafana / `/health` | tout service DOWN > 2 min |
| Latence requêtes | spans OTel → Prometheus (job `otel`) | p95 > 2 s (critère EGSP) |
| Erreurs 5xx | OTel/Prometheus | > 1 % sur 5 min |
| Chaîne d'audit | `audit_chain.verify()` (cron) | vérification False = incident S2 |
| Dérive IA | DAG Airflow drift-check | seuil dépassé → information RQ |
| Sauvegardes | job de sauvegarde BDD + Orthanc | échec → PROC-04 |

## 4. Sauvegardes et restauration

- PostgreSQL (données applicatives + HAPI) : dump quotidien chiffré,
  rétention 30 jours + archive mensuelle ; test de restauration **mensuel**
  sur environnement de test (enregistrement qualité).
- Orthanc : volume `orthanc-data` sauvegardé hors ligne (PACS = données
  primaires).
- RTO cible : 4 h ; RPO : 24 h (à contractualiser avec le CHU — jalon R4).

## 5. Dépannage de premier niveau

1. Service DOWN : `docker compose logs <service>` / `kubectl logs` —
   rechercher l'exception racine ; restart ; si récidive < 24 h → incident
   (PROC-04) avec logs joints.
2. HAPI injoignable : vérifier `postgres-hapi` d'abord (JDBC), puis mémoire
   (`JAVA_TOOL_OPTIONS -Xmx1g`).
3. OHIF sans image : vérifier Orthanc (`/system`), puis le proxy nginx
   `/dicom-web` (secret côté serveur, cf. `docs/OHIF-VIEWER.md`).
4. Aucune donnée dans les dashboards : vérifier le collector OTel
   (ports 4317/4318) et la cible Prometheus `otel-collector:8889`.

## 6. Limites

Ne pas modifier les configurations de production sans PR revue sécurité ;
ne jamais extraire de données patients hors du périmètre CHU ; toute
opération invasive (migration manuelle, purge) est interdite sans accord
du fabricant.
