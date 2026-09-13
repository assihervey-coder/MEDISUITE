"""Bootstrap pytest racine : rend les packages et services importables partout."""
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
for p in ["packages/medisuite-core", "packages/clinical-rules"]:
    sys.path.insert(0, str(ROOT / p))

# --- Evolution Control Plane : alias 'ecp' — chargé aussi quand rootdir = repo
# (le rootdir effectif peut être evolution-control-plane/ à cause de son pyproject,
#  auquel cas evolution-control-plane/tests/conftest.py fait le bootstrap.)
import importlib  # noqa: E402

try:
    _bridge = importlib.import_module("evolution-control-plane._bridge")
    _bridge.register()
except ModuleNotFoundError:
    pass  # rootdir différent : le conftest local du control plane s'en charge
