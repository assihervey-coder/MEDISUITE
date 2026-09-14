"""Tests Safety Engine : red flags, escalade, verdicts."""
from tropirag.clinical_engine.orchestrator import ClinicalOrchestrator
from tropirag.domain.clinical_case.builders import build_case
from tropirag.core.enums import Severity, Urgency


class TestRedFlags:
    def test_coma_critique(self, days_ago):
        res = ClinicalOrchestrator().analyze(build_case({
            "patient": {"age_years": 40},
            "free_text": "fièvre et coma",
            "travel": {"segments": [{"country": "CI", "departure": days_ago(7)}]},
        }))
        assert res.safety.max_severity is Severity.CRITICAL
        assert res.safety.max_urgency is Urgency.IMMEDIATE

    def test_purpura_urgence(self):
        res = ClinicalOrchestrator().analyze(build_case({
            "free_text": "fièvre et pétéchies",
            "patient": {"age_years": 20},
        }))
        assert res.escalation.level.value == "emergency_transfer"
        assert any("ceftriaxone" in e.message.lower() for e in res.rules.escalations)

    def test_hypotension_directe(self):
        res = ClinicalOrchestrator().analyze(build_case({
            "free_text": "fièvre", "vitals": {"systolic_bp": 82},
            "patient": {"age_years": 45},
        }))
        assert res.safety.max_urgency in (Urgency.IMMEDIATE,)

    def test_double_filet_detecteur_direct(self):
        from tropirag.clinical_engine.safety.red_flag_detector import detect_red_flags

        hits = detect_red_flags(build_case({"free_text": "coma"}))
        assert any(h.code == "coma" for h in hits)


class TestEscalade:
    def test_nourrisson_reference(self, days_ago):
        res = ClinicalOrchestrator().analyze(build_case({
            "patient": {"age_years": 0, "age_months": 8},
            "free_text": "fièvre 39",
            "travel": {"segments": [{"country": "CI", "departure": days_ago(10)}]},
        }))
        assert res.escalation.level.value in ("refer_hospital", "emergency_transfer")

    def test_grossesse_fievre(self, days_ago):
        res = ClinicalOrchestrator().analyze(build_case({
            "patient": {"age_years": 26, "sex": "female", "pregnant": "pregnant"},
            "free_text": "fièvre 39",
            "travel": {"segments": [{"country": "CI", "departure": days_ago(10)}]},
        }))
        assert res.escalation.level.value in ("refer_hospital", "senior_clinician",
                                               "emergency_transfer")


class TestVerdict:
    def test_cas_benin_routine(self, days_ago):
        res = ClinicalOrchestrator().analyze(build_case({
            "patient": {"age_years": 30},
            "free_text": "rhinorrhée légère",
            "travel": {"segments": [{"country": "CI", "departure": days_ago(30)}]},
        }))
        assert res.safety.max_severity in (Severity.NONE, Severity.MILD, Severity.MODERATE)
