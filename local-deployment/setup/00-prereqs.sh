#!/usr/bin/env bash
# 00-prereqs — vérification des prérequis d'installation locale MEDISUITE.
# S'arrête sur le premier prérequis DUR manquant ; docker est DUR pour le
# mode conteneurs (07/08) mais toléré en mode natif (ALLOW_NO_DOCKER=1).
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

log "prérequis d'installation — dépôt : ${MEDISUITE_ROOT}"

need_cmd python3 node npm make git curl openssl sha256sum
ok "outils de base présents (python3, node, npm, make, git, curl, openssl)"

PY_MIN="3.10"
PY_VER="$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
python3 - "${PY_VER}" "${PY_MIN}" <<'EOF' || die "python3 >= ${PY_MIN} requis — installer une version récente puis relancer"
import sys
maj, mine = (int(x) for x in sys.argv[1].split("."))
pmin = tuple(int(x) for x in sys.argv[2].split("."))
sys.exit(0 if (maj, mine) >= pmin else 1)
EOF
ok "python3 ${PY_VER} >= ${PY_MIN}"

NODE_MAJ="$(node -p 'process.versions.node.split(".")[0]')"
[ "${NODE_MAJ}" -ge 18 ] || die "node >= 18 requis (trouvé : ${NODE_MAJ}) — voir https://nodejs.org"
ok "node ${NODE_MAJ} >= 18"

if docker_ready; then
  ok "démon docker joignable ($(docker --version))"
  if docker compose version >/dev/null 2>&1; then
    ok "plugin docker compose présent ($(docker compose version --short))"
  else
    die "plugin docker compose absent — installer docker-compose v2"
  fi
else
  if [ "${ALLOW_NO_DOCKER:-0}" = "1" ]; then
    warn "démon docker absent — mode NATIF uniquement (ALLOW_NO_DOCKER=1) : scripts 07/08/09 ignorés"
  else
    warn "démon docker absent — le mode conteneurs (07-images, 08-up, 09-smoke) sera indisponible ; relancer avec ALLOW_NO_DOCKER=1 pour un setup natif seul"
  fi
fi

ok "prérequis validés — poursuivre avec 01-python.sh"
