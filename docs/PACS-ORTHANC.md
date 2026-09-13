# PACS réel — intégration Orthanc (v0.2)

> ADR 0006 (Orthanc comme PACS) et ADR 0002 (DICOMweb PS3.18), désormais
> appliqués avec un Orthanc **réel** et non simulé : image `orthancteam/orthanc`
> + plugin DICOMweb + connecteur REST côté imaging-service.

## 1. Démarrage rapide

```bash
cd local-deployment
docker compose -f docker-compose.minimal.yml up -d orthanc-pacs
# UI Orthanc :        http://localhost:8042  (medisuite / medisuite-dev)
# DICOMweb (QIDO) :   http://localhost:8042/dicom-web/studies
# DICOM (C-STORE) :   localhost:4242, AE title MEDISUITE
```

Le service d'imagerie s'y connecte automatiquement via les variables :

| Variable | Défaut | Rôle |
|---|---|---|
| `MEDISUITE_ORTHANC_URL` | `http://localhost:8042` | API REST Orthanc |
| `MEDISUITE_ORTHANC_USER` | `medisuite` | utilisateur enregistré |
| `MEDISUITE_ORTHANC_PASSWORD` | `medisuite-dev` | **à changer en prod (Vault)** |
| `MEDISUITE_ORTHANC_TIMEOUT` | `3.0` s | délai d'expiration réseau |

## 2. Endpoints exposés par imaging-service

| Endpoint | Description | Comportement si PACS hors ligne |
|---|---|---|
| `GET /api/v1/pacs/status` | Version, AET, compteurs patients/études | `200 {"reachable": false}` — jamais de 5xx |
| `GET /api/v1/pacs/studies?limit=20` | Fiches d'études (expansion `/studies`) | `502` avec cause |
| `GET /api/v1/pacs/qido?query=limit=10&Modality=MG` | Relais QIDO-RS PS3.18 (DICOM JSON) | `502` avec cause |
| `GET /api/v1/integrations` | État des connecteurs (Orthanc actif ?) | `actif: false` |

Le client (`src/orthanc_client.py`) est **stdlib uniquement** (urllib + base64),
testé par injection d'opener factice — aucun conteneur requis pour la chaîne
de tests IEC 62304.

## 3. Configuration Orthanc (`local-deployment/orthanc/orthanc.json`)

- `DicomAet: MEDISUITE` — AE title du PACS ;
- `DicomModalities` — SIMULATEUR, MODALITE-CT, MODALITE-MG (C-ECHO/C-STORE) ;
- `DicomWeb.Enable: true` — QIDO-RS `/dicom-web/`, WADO-RS `/wado/` ;
- `AuthenticationEnabled` + `RegisteredUsers` — credentials requis, **le mot
  de passe du dépôt est un secret de développement** ; en production, injecter
  depuis Vault et activer TLS côté reverse-proxy ;
- `StorageDirectory`/`IndexDirectory` — volume Docker persistant `orthanc-data`.

## 4. Envoyer un examen vers le PACS (test bout en bout)

```bash
# Depuis une modalité (ou storescu de dcmtk) :
storescu -aet MODALITE-CT -aec MEDISUITE localhost 4242 examen.dcm
# Puis vérifier côté MEDISUITE :
curl -u medisuite:medisuite-dev http://localhost:8042/system | jq .Version
curl "http://localhost:8003/api/v1/pacs/studies?limit=5"
```

## 5. Limites v0.2 (assumées, traçées pour v0.3)

- Pas de TLS entre imaging-service et Orthanc (réseau Docker interne) ; en
  production : mTLS via reverse-proxy ou `Ssl: true` + certificats Vault.
- Les pixels passent par Orthanc (WADO-RS) ; le viewer OHIF se branche
  directement sur `/dicom-web` (extension prévue dans apps/dicom-viewer).
- Pas de routage MPPS/UPS vers Orthanc — le worklist UPS local du
  imaging-service reste la source d'ordonnancement en v0.2.
