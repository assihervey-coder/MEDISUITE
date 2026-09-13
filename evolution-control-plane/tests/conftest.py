"""Bootstrap pytest du control plane — alias 'ecp' (répertoires à tirets)."""
import importlib
import sys
from pathlib import Path

# rootdir = evolution-control-plane/ (pyproject) → le root du repo doit être
# sur sys.path pour importlib.import_module("evolution-control-plane._bridge")
REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

_bridge = importlib.import_module("evolution-control-plane._bridge")
_bridge.register()
