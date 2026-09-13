# Setup local MEDISUITE — séquence 00-10 (v0.13)

Installation locale idempotente, en 11 scripts numérotés et ré-exécutables
(régression sans dommage). Deux modes : **natif** (venv + SQLite, aucun docker
requis) et **conteneurs** (compose minimale : Orthanc PACS, HAPI FHIR, OTel,
Vault, Prometheus, Grafana, OHIF).

| Script | Rôle | Durée indicative |
|---|---|---|
| `00-prereqs.sh` | outils + versions (python ≥ 3.10, node ≥ 18, docker, compose v2) | < 1 min |
| `01-python.sh` | venv `.venv` + dépendances socle (SKIP_AI=1 pour sauter torch) | 2-10 min |
| `02-portal.sh` | dépendances Node du portail (PLAYWRIGHT=1 pour les e2e) | 1-3 min |
| `03-env.sh` | `.env` local + secrets aléatoires (permissions 600, jamais écrasé) | < 1 min |
| `04-certs.sh` | certificat autosigné DEV (30 j) — jamais en production | < 1 min |
| `05-secrets.sh` | injection des secrets dans Vault dev (sauté sans docker) | < 1 min |
| `06-db.sh` | bases SQLite + seeds (démarre les 38 services, smoke, arrêt) | 2-5 min |
| `07-images.sh` | pull + build des images de la compose minimale | 5-15 min |
| `08-up.sh` | `docker compose up -d` + attente des santés (6 sondes) | 1-4 min |
| `09-smoke.sh` | smoke natif + sondes conteneurs | 1-2 min |
| `10-verify.sh` | bilan final 🟢/🟠/🔴 + prochaines étapes | < 1 min |

## Utilisation

```bash
# Mode complet (docker disponible)
bash local-deployment/setup/00-prereqs.sh          # ou : make setup-local
bash local-deployment/setup/05-secrets.sh          # après 08-up seulement
bash local-deployment/setup/07-images.sh && bash local-deployment/setup/08-up.sh
bash local-deployment/setup/09-smoke.sh && bash local-deployment/setup/10-verify.sh

# Mode natif sans docker
ALLOW_NO_DOCKER=1 bash local-deployment/setup/00-prereqs.sh
bash local-deployment/setup/01-python.sh && bash local-deployment/setup/02-portal.sh
bash local-deployment/setup/03-env.sh && bash local-deployment/setup/06-db.sh
bash local-deployment/setup/10-verify.sh
```

Raccourcis Makefile : `make setup-local` (natif : 00→04, 06, 10) et
`make setup-local-docker` (07→10).

## Règles communes (`_lib.sh`)

- `set -euo pipefail` : échec = arrêt immédiat, jamais d'état à moitié écrit.
- Idempotence : chaque script détecte ce qui est déjà fait (venv, node_modules,
  `.env`, certificats) et ne refait que le nécessaire.
- Honnêteté des sorties : 🟢 fait · 🟠 sauté proprement (avec la raison) ·
  🔴 bloquant (exit ≠ 0).
- Flags : `ALLOW_NO_DOCKER=1`, `SKIP_AI=1`, `SKIP_SEED=1`, `PLAYWRIGHT=1`.

## Site sans Internet

Voir `../offline/README.md` : le paquet `.tar.gz` embarque wheels, cache npm,
images docker et SBOM ; `install-bundle.sh` vérifie `MANIFEST.sha256` puis
relaie vers la séquence 00-10 en `OFFLINE=1`.
