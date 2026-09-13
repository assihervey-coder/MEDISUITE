# Visualiseur OHIF v3 branché sur `/dicom-web` (v0.3)

## Architecture

```
Navigateur (radiologue)
   │  http://localhost:3001
   ▼
┌─────────────────────────────────────────────┐
│  ohif-viewer  (ohif/app:v3.8.3 + nginx)     │
│  - SPA OHIF v3        → fichiers statiques  │
│  - /dicom-web/*  ─────┐ proxy injectant     │
│  - /wado/*  ──────────┤ "Authorization:     │
│                       │  Basic ****"        │
└───────────────────────┼─────────────────────┘
                        ▼
        ┌───────────────────────────────┐
        │  orthanc-pacs  :8042          │
        │  Orthanc OSS 24.9             │
        │  plugin DICOMweb (PS3.18)     │
        │  QIDO-RS / WADO-RS / STOW-RS  │
        └───────────────────────────────┘
```

La chaîne d'imagerie devient **réelle de bout en bout** :
`STOW (modalité / imaging-service)` → `Orthanc` → `DICOMweb` → `OHIF` → lecture diagnostique.

## Démarrage

```bash
docker compose -f local-deployment/docker-compose.minimal.yml build ohif-viewer
docker compose -f local-deployment/docker-compose.minimal.yml up -d orthanc-pacs ohif-viewer
# UI  : http://localhost:3001 (liste d'études OHIF)
```

Déposer une étude puis l'ouvrir :

```bash
# exemple : STOW via imaging-service, puis lien profond
curl -X POST http://localhost:8003/dicom-web/studies -H "Content-Type: application/json" -d '{...}'
# lien profond généré par imaging-service :
curl "http://localhost:8003/api/v1/pacs/viewer-url?study_uid=1.2.3..." -H "Authorization: Bearer <jwt>"
# → {"viewer":"ohif","url":"http://localhost:3001/viewer?StudyInstanceUIDs=1.2.3..."}
```

Le web-portal (page Imagerie) embarque un bouton **OHIF ↗** par étude qui
construit le même lien profond (base surchargeable par `VITE_OHIF_BASE`).

## Fichiers

| Fichier | Rôle |
|---|---|
| `local-deployment/ohif/app-config.js` | Source de données DICOMweb `orthanc` (chemins relatifs) |
| `local-deployment/ohif/nginx.conf` | Proxy `/dicom-web` + `/wado` → `orthanc-pacs:8042` |
| `local-deployment/ohif/Dockerfile` | Surcharge de l'image officielle `ohif/app:v3.8.3` |
| `services/imaging-service/src/main.py` | `GET /api/v1/pacs/viewer-url` (RBAC `imaging.read`, UID validé) |

## Sécurité

- **Le secret PACS ne quitte jamais le conteneur nginx** : le navigateur parle
  à OHIF sans identifiant ; nginx injecte l'en-tête `Authorization` vers
  Orthanc. Aucun CORS à ouvrir, aucune exposition du mot de passe PACS.
- **Validation d'UID stricte** côté imaging-service (`^\d+(\.\d+)+$`) avant
  composition du lien profond — anti-injection dans l'URL du viewer.
- **Production** : remplacer l'en-tête Basic statique par le plugin
  `keycloak` d'Orthanc (OIDC, déjà provisionné dans `infrastructure/keycloak/`)
  ou par un gateway authentifié (api-gateway + mTLS). L'image `ohif/app`
  supporte `AUTH` par plugin OHIF (extension `@ohif/extension-default`).
- Les comptes Orthanc (`RegisteredUsers`) restent actifs : l'accès direct
  :8042 doit être fermé côté réseau en production (docker network interne).

## Limites connues (honnêteté d'audit)

- L'image `ohif/app:v3.8.3` est un artefact compilé : la config est testée
  par validation JSON + pattern officiel OHIF, pas par un navigateur headless
  dans la CI (aucun Docker disponible dans l'environnement de build).
- Les identifiants Basic sont en clair dans `nginx.conf` (dev local). En prod :
  secrets Docker/K8s + plugin Keycloak (voir ci-dessus).
- OHIF nécessite des instances avec `PixelData` : les études STOW-RS au format
  JSON métadonnées seules listent mais ne rendent pas de pixels (comportement
  DICOM standard, pas un bug MEDISUITE).
