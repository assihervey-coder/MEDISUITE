# Déploiement local MEDISUITE

## Installation assistée (v0.13) — séquence 00-10

```bash
make setup-local            # mode natif : 00-prereqs → 04-certs, 06-db, 10-verify
make setup-local-docker     # mode conteneurs : 07-images, 08-up, 05-secrets, 09-smoke, 10-verify
```

Détail des 11 scripts idempotents, flags (`SKIP_AI`, `PLAYWRIGHT`,
`ALLOW_NO_DOCKER`, `OFFLINE=1`) et bilan final : **setup/README.md**.
Site sans Internet : **offline/README.md** (`make offline-bundle`).

## Lancement manuel (historique)

1. `make install-core && make test` — validation du socle
2. `make dev-up && make smoke` — 38 services sur SQLite (zéro dépendance externe)
3. `docker compose -f local-deployment/docker-compose.minimal.yml up` — mode conteneurs
   (Orthanc PACS + Prometheus + Grafana inclus)
4. Ports : gateway 8000 · auth 8001 · patients 8002 · imagerie 8003 · labo 8004 ·
   spécialités 8100-8123 · transverses 8200-8204 · passerelles 8300-8303 · OHIF/Grafana 3000
