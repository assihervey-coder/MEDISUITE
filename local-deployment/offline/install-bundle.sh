#!/usr/bin/env bash
# install-bundle — installe un paquet hors-ligne MEDISUITE sur le site cible.
#
# Usage : bash install-bundle.sh medisuite-offline-<version>.tar.gz [racine_cible]
#
# Étapes (toutes vérifiées par MANIFEST.sha256 AVANT toute installation) :
#   1. contrôle d'intégrité (sha256) du paquet et de son contenu
#   2. images docker (docker load)
#   3. dépendances Python (pip install --no-index --find-links wheels/)
#   4. portail (npm ci --offline --cache npm-cache)
#   5. rappel : exécuter la séquence setup 00-10 en mode OFFLINE=1
set -euo pipefail

PKG="${1:?usage : install-bundle.sh <paquet.tar.gz> [racine_cible]}"
TARGET_ROOT="${2:-$(pwd)/medisuite}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

[ -f "${PKG}" ] || { echo "paquet introuvable : ${PKG}" >&2; exit 1; }
command -v sha256sum >/dev/null || { echo "sha256sum requis" >&2; exit 1; }

WORK="$(mktemp -d)"
trap 'rm -rf "${WORK}"' EXIT

echo "[install] [1/5] contrôle d'intégrité"
[ -f "${PKG}.sha256" ] && (cd "$(dirname "${PKG}")" && sha256sum -c "$(basename "${PKG}").sha256") \
  || echo "[install] ⚠️ .sha256 du paquet absent — l'intégrité du contenu seul sera vérifiée"
tar -xzf "${PKG}" -C "${WORK}"
BUNDLE="$(find "${WORK}" -maxdepth 1 -type d -name 'medisuite-offline-*' | head -1)"
(cd "${BUNDLE}" && sha256sum -c MANIFEST.sha256 --quiet) \
  || { echo "[install] 🔴 intégrité du contenu ÉCHOUÉE — paquet corrompu, installation annulée" >&2; exit 1; }
echo "[install] 🟢 contenu conforme au manifeste"

echo "[install] [2/5] images docker"
if command -v docker >/dev/null 2>&1 && ls "${BUNDLE}"/images/*.tar >/dev/null 2>&1; then
  for img in "${BUNDLE}"/images/*.tar; do docker load -i "${img}"; done
else
  echo "[install] ⚠️ docker absent ou pas d'images dans le paquet — mode natif uniquement"
fi

echo "[install] [3/5] dépendances Python (hors-ligne, aucun index)"
python3 -m venv "${TARGET_ROOT}/.venv"
"${TARGET_ROOT}/.venv/bin/pip" install --no-index --find-links "${BUNDLE}/wheels" \
  -r "${TARGET_ROOT}/requirements.txt" 2>/dev/null \
  || "${TARGET_ROOT}/.venv/bin/pip" install --no-index --find-links "${BUNDLE}/wheels" \
       fastapi uvicorn sqlalchemy httpx pytest pyyaml numpy

echo "[install] [4/5] portail (npm offline)"
mkdir -p "${TARGET_ROOT}/apps/web-portal"
cp "${BUNDLE}/portal/package.json" "${BUNDLE}/portal/package-lock.json" "${TARGET_ROOT}/apps/web-portal/"
(cd "${TARGET_ROOT}/apps/web-portal" && npm ci --offline --cache "${BUNDLE}/portal/npm-cache" --no-audit --no-fund) \
  || echo "[install] ⚠️ npm ci --offline a échoué — vérifier le cache embarqué"

echo "[install] [5/5] prochaines étapes"
echo "  1. synchroniser le code source du dépôt vers ${TARGET_ROOT} (rsync du dépôt à la même version)"
echo "  2. cd ${TARGET_ROOT} && OFFLINE=1 bash local-deployment/setup/00-prereqs.sh && … jusqu'à 10-verify.sh"
echo "  3. OFFLINE=1 fait sauter par les scripts tout accès réseau restant"
echo "[install] 🟢 paquet installé — les scripts 00-10 prennent le relais"
