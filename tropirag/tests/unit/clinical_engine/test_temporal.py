"""Tests du moteur temporel — incubations et chronologie."""
from datetime import timedelta

from tropirag.clinical_engine.temporal.incubation_engine import IncubationEngine
from tropirag.domain.clinical_case.builders import build_case
from tropirag.core.datetime import local_now


def case_with(return_days_ago: int, onset_days_ago: int | None):
    data = {
        "patient": {"age_years": 30},
        "free_text": "fièvre",
        "travel": {"segments": [{"country": "CI",
                                 "departure": (local_now().date() - timedelta(days=return_days_ago)).isoformat()}]},
        "consultation_date": local_now().date().isoformat(),
    }
    if onset_days_ago is not None:
        data["symptom_onset"] = (local_now().date() - timedelta(days=onset_days_ago)).isoformat()
    return build_case(data)


class TestIncubation:
    def test_dengue_compatible(self):
        c = case_with(return_days_ago=8, onset_days_ago=4)  # début 4 j après retour
        checks = IncubationEngine().check_all(c, ["dengue"])
        assert checks[0].compatible is True

    def test_dengue_trop_tardive(self):
        c = case_with(return_days_ago=90, onset_days_ago=3)
        checks = IncubationEngine().check_all(c, ["dengue"])
        assert checks[0].compatible is False
        assert "trop tardif" in checks[0].reason.lower() or "Trop tardif" in checks[0].reason

    def test_malaria_fenetre_large(self):
        c = case_with(return_days_ago=45, onset_days_ago=2)
        checks = IncubationEngine().check_all(c, ["malaria"])
        assert checks[0].compatible is True

    def test_sans_dates_never_excludes(self):
        c = build_case({"patient": {"age_years": 30}, "free_text": "fièvre",
                        "travel": {"segments": [{"country": "CI"}]}})
        checks = IncubationEngine().check_all(c, ["dengue"])
        assert checks[0].compatible is True  # prudence


class TestNarratif:
    def test_narration_chronologie(self):
        from tropirag.clinical_engine.temporal.incubation_engine import TemporalReasoner

        c = case_with(return_days_ago=9, onset_days_ago=4)
        lines = TemporalReasoner().narrate(c)
        assert any("Retour" in l for l in lines)
        assert any("APRÈS le retour" in l for l in lines)
