#!/usr/bin/env python3
"""Correctif RBAC : jeton expiré → 401 (pas 403) dans tous les services.

Remplace le corps de ``current_user`` (39 copies générées à l'identique)
par l'appel à la dépendance partagée ``medisuite_core.auth_deps.bearer_identity`` :
  - pas d'en-tête → anon (endpoints publics, RBAC fail-closed inchangé) ;
  - jeton invalide/expiré → HTTP 401 (le portail déconnecte proprement) ;
  - jeton valide → claims.
Le script est idempotent (re-exécution = 0 remplacement).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path("/home/z/my-project/MEDISUITE")

# Corps identique dans les 39 services (deux styles de signature, docstring optionnelle).
RX = re.compile(
    r'def current_user\(\s*authorization: Annotated\[str \| None, Header\(\)\] = None,?\s*\) -> dict:\s*'
    r'(?:"""[^"]*"""\s*)?'
    r'if not authorization or not authorization\.lower\(\)\.startswith\("bearer "\):\s*'
    r'return \{"sub": "anon", "role": ""\}\s*'
    r'try:\s*'
    r'return security\.jwt_decode\(authorization\.split\(" ", 1\)\[1\], JWT_SECRET\)\s*'
    r'except security\.JWTError:\s*'
    r'return \{"sub": "anon", "role": ""\}'
)

NEW_BODY = (
    'def current_user(authorization: Annotated[str | None, Header()] = None) -> dict:\n'
    '    """Identité : absent → anon ; jeton invalide/expiré → 401 (le portail\n'
    '    déconnecte au lieu d\'afficher un faux 403) ; valide → claims (RBAC)."""\n'
    '    return auth_deps.bearer_identity(authorization, JWT_SECRET)'
)

IMPORT_LINE = "from medisuite_core import auth_deps"


def patch(path: Path) -> int:
    src = path.read_text(encoding="utf-8")
    if "auth_deps.bearer_identity" in src:
        return 0  # déjà corrigé (idempotent)
    out, n = RX.subn(NEW_BODY, src)
    if n == 0:
        return 0
    # import : après la dernière ligne 'from medisuite_core import security'
    if IMPORT_LINE not in out:
        anchor = "from medisuite_core import security"
        if anchor in out:
            out = out.replace(anchor, anchor + "\n" + IMPORT_LINE, 1)
        else:  # repli : juste avant la fonction
            out = RX.sub(IMPORT_LINE + "\n\n\n" + NEW_BODY, out, count=1)
            n = 0  # déjà substitué ci-dessus — recompte pour honnêteté
    path.write_text(out, encoding="utf-8")
    return n if n else 1


def main() -> int:
    total_files = total_repl = 0
    for path in sorted((ROOT / "services").glob("*/src/main.py")):
        src = path.read_text(encoding="utf-8")
        if "def current_user" not in src:
            continue
        if "auth_deps.bearer_identity" in src:
            continue
        n = patch(path)
        if n:
            total_files += 1
            total_repl += n
            print(f"  ✓ {path.relative_to(ROOT)} ({n})")
        else:
            print(f"  ⚠ pattern non reconnu : {path.relative_to(ROOT)} "
                  f"(à corriger à la main)")
    print(f"\n{total_repl} remplacement(s) dans {total_files} service(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
