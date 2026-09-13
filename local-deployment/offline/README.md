# Paquet d'installation hors-ligne MEDISUITE (air-gapped)

Concerne les sites sans accès Internet (politique CHU, salle imaging isolée,
zone de soin fermée). Le paquet rend la séquence `setup/00-10` exécutable
**sans un seul octet réseau**, à l'exception de la synchronisation du code
source du dépôt lui-même (même version que le paquet, cf. `MANIFEST.sha256`).

## Contenu du paquet `medisuite-offline-<version>.tar.gz`

| Entrée | Contenu | Producteur |
|---|---|---|
| `wheels/` | toutes les dépendances Python du socle (+ IA si `--with-ai`) | `pip download` |
| `portal/` | `package.json`, `package-lock.json`, cache npm complet | `npm ci --cache` |
| `images/` | images tierces (`docker save`) + images MEDISUUTE construites | 07-images.sh |
| `docs/` | README d'installation, README offline, SBOM CycloneDX | dépôt |
| `MANIFEST.sha256` | empreinte de **tous** les fichiers du paquet | build-bundle.sh |

## Côté site émetteur (avec Internet)

```bash
make offline-bundle                          # = build-bundle.sh (complet)
bash local-deployment/offline/build-bundle.sh --no-images   # paquet léger
DRY_RUN=1 bash local-deployment/offline/build-bundle.sh     # plan sans effet
```

Transport : copier `medisuite-offline-<version>.tar.gz` **et** `.sha256` sur un
support chiffré (la clé USB seule n'est pas un contrôle suffisant — cf. plan
de gestion des risques RM-07 supports amovibles).

## Côté site cible (sans Internet)

```bash
sha256sum -c medisuite-offline-<version>.tar.gz.sha256       # transport OK ?
bash local-deployment/offline/install-bundle.sh \
      medisuite-offline-<version>.tar.gz /opt/medisuite      # vérifie MANIFEST
# puis : synchroniser le dépôt à la MÊME version dans /opt/medisuite, et :
cd /opt/medisuite
OFFLINE=1 bash local-deployment/setup/00-prereqs.sh && …    # séquence 00-10
```

`install-bundle.sh` refuse toute installation si le contrôle du manifeste
échoue (paquet corrompu ou altéré). Il installe ensuite hors réseau :
`pip install --no-index --find-links wheels/`, `npm ci --offline --cache
npm-cache`, `docker load` des images — puis les flags `OFFLINE=1` des scripts
00-10 interdisent tout accès réseau résiduel.

## Traçabilité conformité

- SBOM CycloneDX embarqué (`docs/sbom.json`) : base de la preuve de provenance
  des composants exigée par le dossier technique MDR (TD-01) et le plan pentest.
- La version du paquet (`git describe`) relie paquet ↔ commit ↔ datasets ↔
  model-cards : un site installé est auditable jusqu'au commit exact.
- Les images docker tierces sont versionnées exactement (orthanc 24.9,
  otel-collector 0.109.0, vault 1.17, prometheus v2.54.0, grafana 11.2.0) :
  aucun `latest` en production excepté HAPI (à figer avant R6 — suivi GAP).
