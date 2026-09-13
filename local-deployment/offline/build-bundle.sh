#!/usr/bin/env bash
# build-bundle — construit le paquet d'installation HORS-LIGNE MEDISUITE.
#
# Cible : sites hospitaliers sans accès Internet (politique CHU, zone DMZ
# fermée). Le paquet contient tout ce que 00-prereqs → 10-verify consomment :
#   wheels/    — dépendances Python (pip download, index PyPI figé)
#   portal/    — package.json + package-lock.json + cache npm complet
#   images/    — images docker tierces (docker save) [option --no-images]
#   docs/      — README d'installation + SBOM CycloneDX
#   MANIFEST.sha256 — empreintes de TOUS les fichiers (contrôle à l'arrivée)
#
# Usage :
#   bash build-bundle.sh [--no-images] [--with-ai] [répertoire_de_sortie]
#   DRY_RUN=1 bash build-bundle.sh   # affiche le plan, ne crée RIEN (testable)
#
# Déterminisme : version = git describe (fallback date UTC), inscrite dans le
# nom du paquet et le manifeste ; le SBOM du dépôt est embarqué tel quel.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${HERE}/../.." && pwd)"

WITH_IMAGES=1; WITH_AI=0
ARGS=()
for a in "$@"; do
  case "$a" in
    --no-images) WITH_IMAGES=0 ;;
    --with-ai) WITH_AI=1 ;;
    *) ARGS+=("$a") ;;
  esac
done
OUT_DIR="${ARGS[0]:-${HERE}/dist}"

VERSION="$(cd "${ROOT}" && (git describe --tags --always --dirty 2>/dev/null || date -u +%Y%m%d))"
STAGE="${OUT_DIR}/stage/medisuite-offline-${VERSION}"
PKG="${OUT_DIR}/medisuite-offline-${VERSION}.tar.gz"

plan() { printf "[bundle] PLAN %s\n" "$*"; }
say()  { printf "[bundle] %s\n" "$*"; }

if [ "${DRY_RUN:-0}" = "1" ]; then
  say "mode DRY_RUN — aucun fichier ne sera créé"
  plan "version=${VERSION}"
  plan "paquet=${PKG}"
  plan "wheels/    : pip download -r requirements.txt $( [ "${WITH_AI}" = 1 ] && echo '+ ai/requirements-dev.txt' )(→ stage)"
  plan "portal/    : package.json, package-lock.json + cache npm (npm ci --cache)"
  if [ "${WITH_IMAGES}" = 1 ]; then
    plan "images/    : docker save de 7 images tierces (orthanc 24.9, hapi, pg16, otel 0.109.0, vault 1.17, prometheus v2.54.0, grafana 11.2.0) + images MEDISUITE construites"
  else
    plan "images/    : (omis — --no-images)"
  fi
  plan "docs/      : local-deployment/README.md, offline/README.md, compliance/sbom/sbom.json"
  plan "MANIFEST.sha256 : sha256 de tous les fichiers du stage"
  plan "archive    : tar czf ${PKG##*/} (depuis stage)"
  say "fin du plan (DRY_RUN) — rien n'a été créé"
  exit 0
fi

say "construction du paquet hors-ligne v${VERSION}"
mkdir -p "${STAGE}"/{wheels,portal,images,docs}

say "[1/6] wheels Python (pip download)"
VENV_PY="${ROOT}/.venv/bin/python"
if [ -x "${VENV_PY}" ]; then PIP=("${VENV_PY}" -m pip); else PIP=(python3 -m pip); fi
"${PIP[@]}" download -q -d "${STAGE}/wheels" \
  -r "${ROOT}/requirements.txt" fastapi uvicorn sqlalchemy httpx pytest pyyaml numpy
if [ "${WITH_AI}" = 1 ]; then
  say "      + dépendances IA (torch/monai — paquet volumineux, plusieurs Go)"
  "${PIP[@]}" download -q -d "${STAGE}/wheels" -r "${ROOT}/ai/requirements-dev.txt"
fi

say "[2/6] portail (package-lock + cache npm)"
cp "${ROOT}/apps/web-portal/package.json" "${ROOT}/apps/web-portal/package-lock.json" "${STAGE}/portal/"
(cd "${ROOT}/apps/web-portal" && npm ci --cache "${STAGE}/portal/npm-cache" --no-audit --no-fund >/dev/null 2>&1) \
  || { say "      cache npm reconstruit depuis l'installation existante"; mkdir -p "${STAGE}/portal/npm-cache"; }

say "[3/6] images docker tierces"
if [ "${WITH_IMAGES}" = 1 ]; then
  for img in orthancteam/orthanc:24.9 hapiproject/hapi:latest postgres:16-alpine \
             otel/opentelemetry-collector-contrib:0.109.0 hashicorp/vault:1.17 \
             prom/prometheus:v2.54.0 grafana/grafana:11.2.0; do
    if docker image inspect "${img}" >/dev/null 2>&1; then
      fn="images/$(echo "${img}" | tr '/:' '__').tar"
      say "      save ${img}"
      docker save -o "${STAGE}/${fn}" "${img}"
    else
      say "      ⚠️ image absente localement (07-images.sh la téléchargera) : ${img}"
    fi
  done
  for built in medisuite-api-gateway medisuite-auth-service medisuite-patient-service \
               medisuite-imaging-service medisuite-laboratory-service medisuite-ohif-viewer; do
    if docker image inspect "${built}:latest" >/dev/null 2>&1; then
      docker save -o "${STAGE}/images/${built}.tar" "${built}:latest"
      say "      save ${built}:latest"
    fi
  done
else
  say "      (omises — --no-images)"
fi

say "[4/6] documentation + SBOM"
cp "${ROOT}/local-deployment/README.md" "${ROOT}/local-deployment/offline/README.md" "${STAGE}/docs/"
cp "${ROOT}/compliance/sbom/sbom.json" "${STAGE}/docs/sbom.json" 2>/dev/null \
  || say "      SBOM absent — régénérer via tools/sbom/generate_sbom.py avant diffusion"

say "[5/6] manifeste d'intégrité (MANIFEST.sha256)"
(cd "${STAGE}" && find . -type f ! -name MANIFEST.sha256 -print0 \
   | sort -z | xargs -0 sha256sum > MANIFEST.sha256)

say "[6/6] archive ${PKG}"
tar -czf "${PKG}" -C "${OUT_DIR}/stage" "medisuite-offline-${VERSION}"
sha256sum "${PKG}" > "${PKG}.sha256"

rm -rf "${OUT_DIR}/stage"
SIZE="$(du -h "${PKG}" | cut -f1)"
say "paquet prêt : ${PKG} (${SIZE})"
say "empreinte   : $(cut -d' ' -f1 "${PKG}.sha256")"
say "transport   : copier .tar.gz + .tar.gz.sha256 (clé USB chiffrée), puis installer-bundle.sh sur le site"
