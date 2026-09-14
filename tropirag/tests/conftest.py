"""Configuration pytest — chemin src + fixtures globales."""
import sys
from datetime import timedelta
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import pytest  # noqa: E402

from tropirag.core.datetime import local_now  # noqa: E402


@pytest.fixture()
def days_ago():
    """Fabrique de dates ISO relatives (tests déterministes dans le temps)."""

    def _make(n: int) -> str:
        return (local_now().date() - timedelta(days=n)).isoformat()

    return _make


@pytest.fixture()
def fever_travel_ci_case(days_ago):
    """Cas de référence : fièvre + retour de Côte d'Ivoire (rural)."""

    def _make(**over):
        base = {
            "patient": {"age_years": 34, "sex": "male"},
            "free_text": "fièvre 39,6 depuis 4 jours, frissons, vomissements, céphalées",
            "travel": {"segments": [{
                "country": "CI", "region": "Abidjan", "rural_stay": True,
                "departure": days_ago(9),
            }]},
            "vitals": {"temperature_c": 39.6},
        }
        base.update(over)
        return base

    return _make
