# Déploiement local MEDISUITE

1. `make install-core && make test` — validation du socle
2. `make dev-up && make smoke` — 38 services sur SQLite (zéro dépendance externe)
3. `docker compose -f local-deployment/docker-compose.minimal.yml up` — mode conteneurs
   (Orthanc PACS + Prometheus + Grafana inclus)
4. Ports : gateway 8000 · auth 8001 · patients 8002 · imagerie 8003 · labo 8004 ·
   spécialités 8100-8123 · transverses 8200-8204 · passerelles 8300-8303 · OHIF/Grafana 3000
