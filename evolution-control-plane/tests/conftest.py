"""Bootstrap pytest du control plane — alias 'ecp' (répertoires à tirets)."""
import importlib
import os
import sys
from pathlib import Path

# rootdir = evolution-control-plane/ (pyproject) → le root du repo doit être
# sur sys.path pour importlib.import_module("evolution-control-plane._bridge")
REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# PROP-0012 — isolation : les tests ne doivent JAMAIS écrire dans la chaîne
# d'audit WORM du dépôt (preuves de gouvernance réelles). À poser AVANT tout
# import de l'app : _state lit ECP_AUDIT_PATH au moment de l'import.
os.environ.setdefault(
    "ECP_AUDIT_PATH",
    str(Path(__file__).resolve().parent / "_audit-tests.jsonl"))

_bridge = importlib.import_module("evolution-control-plane._bridge")
_bridge.register()
