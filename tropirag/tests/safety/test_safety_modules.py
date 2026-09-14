"""Tests safety étendus (clinical/medication/llm/evidence) + response_engine."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from tropirag.core.enums import SourceAuthority  # noqa: E402
from tropirag.domain.evidence.entities import EvidencePack, EvidenceUnit, SourceRef  # noqa: E402
from tropirag.safety.clinical_safety import (  # noqa: E402
    clinical_safety_report,
    disclaimer,
    urgency_conveyed,
)
from tropirag.safety.evidence_safety import (  # noqa: E402
    most_authoritative,
    resolve_conflict,
    verify_pack,
)
from tropirag.safety.llm_safety import LlmSafetyChecker  # noqa: E402
from tropirag.safety.medication_safety import (  # noqa: E402
    MedicationSafetyEngine,
    screen_prescription,
)

WHO = SourceRef(source_id="who-x", authority=SourceAuthority.WHO, title="Guide",
                publisher="OMS", edition_date="2023-06-01")
MSF = SourceRef(source_id="msf-x", authority=SourceAuthority.MSF, title="Protocole",
                publisher="MSF", edition_date="2022-01-01")


def _pack(*units: EvidenceUnit) -> EvidencePack:
    pack = EvidencePack(query="test")
    pack.units = list(units)
    for i, u in enumerate(units):
        pack.scores[u.unit_id] = 1.0 - 0.1 * i
    return pack


class TestClinicalSafety:

    def test_disclaimer_present(self):
        text = f"{disclaimer('fr')} Voici la synthèse..."
        assert clinical_safety_report(text, "urgent")["disclaimer"] is True

    def test_urgence_immediate_conveyed(self):
        ok = "Transfert de référence immédiate requis — urgence vitale."
        ko = "Vous pouvez consulter dans les prochains jours."
        assert urgency_conveyed(ok, "immediate")
        assert not urgency_conveyed(ko, "immediate")

    def test_rapport_complet(self):
        r = clinical_safety_report(
            f"{disclaimer('fr')} Cas urgent : transfert immédiat. Purpura évoqué.",
            urgency="immediate", red_flags=["purpura"])
        assert r["red_flags"]["passed"]
        assert r["urgency_conveyed"]


class TestMedicationSafety:

    def test_primaquine_grossesse_bloquee(self):
        v = MedicationSafetyEngine().check(
            "primaquine", {"pregnant": True, "gestational_age_weeks": 12})
        assert not v.allowed and v.severity == "absolute"
        assert any("grossesse" in r for r in v.reasons)

    def test_paracetamol_autorise(self):
        v = MedicationSafetyEngine().check(
            "paracetamol", {"diseases": ["dengue"], "pregnant": False})
        assert v.allowed

    def test_screen_trie_par_gravite(self):
        verdicts = screen_prescription(
            ["paracetamol", "primaquine"],
            {"pregnant": True, "diseases": ["dengue"]})
        # primaquine (bloqué) doit venir avant paracétamol
        assert verdicts[0].drug_code == "primaquine"
        assert not verdicts[0].allowed

    def test_medicament_inconnu(self):
        v = MedicationSafetyEngine().check("inconnu-xyz", {})
        assert v.severity == "caution" and "inconnu" in v.reasons[0]


class TestLlmSafety:

    def test_limites_ok(self):
        pack = _pack(EvidenceUnit(unit_id="eu-1",
                                   text="L'artésunate IV est indiqué dans le paludisme sévère.",
                                   source=WHO))
        checker = LlmSafetyChecker()
        ok = ("Le paludisme sévère est suspecté ; l'artésunate IV est indiqué "
              "selon les preuves [eu-1].")
        assert checker.passed(ok, pack)

    def test_posologie_llm_rejetee(self):
        checker = LlmSafetyChecker()
        bad = "Prendre 500 mg trois fois par jour pendant 7 jours."
        assert not checker.passed(bad)

    def test_diagnostic_autonome_rejete(self):
        checker = LlmSafetyChecker()
        bad = "Le diagnostic certain est le paludisme."
        assert not checker.passed(bad)


class TestEvidenceSafety:

    def test_pack_expire_detecte(self):
        expired = EvidenceUnit(unit_id="eu-old", text="périmé",
                               source=MSF, valid_until="2020-01-01")
        current = EvidenceUnit(unit_id="eu-new", text="valide", source=WHO)
        report = verify_pack(_pack(expired, current))
        assert not report["passed"]
        assert report["expired_unit_ids"] == ["eu-old"]

    def test_hiérarchie_autorite(self):
        who_u = EvidenceUnit(unit_id="eu-who", text="OMS", source=WHO)
        msf_u = EvidenceUnit(unit_id="eu-msf", text="MSF", source=MSF)
        assert most_authoritative(_pack(msf_u, who_u))[0] == "eu-who"

    def test_conflit_resolu(self):
        who_u = EvidenceUnit(unit_id="eu-who", text="OMS", source=WHO)
        msf_u = EvidenceUnit(unit_id="eu-msf", text="MSF", source=MSF)
        out = resolve_conflict([msf_u, who_u])
        assert out["winner"] == "eu-who" and out["losers"] == ["eu-msf"]


class TestResponseEngineExtended:

    def test_uncertainty_niveaux(self):
        from tropirag.response_engine.uncertainty_formatter import (
            level_from_score,
            level_statement,
        )
        assert level_from_score(0.8) == "high"
        assert level_from_score(0.5) == "medium"
        assert level_from_score(0.1) == "low"
        assert "Incertitude" in level_statement("high")

    def test_citation_integrite(self):
        from tropirag.response_engine.citation_builder import (
            format_bibliography,
            verify_citations,
        )
        from tropirag.response_engine.clinical_response_builder import ClinicalResponse

        unit = EvidenceUnit(unit_id="eu-1", source=WHO, section="Traitement",
                            text="L'artésunate IV est le traitement de référence du paludisme sévère.")
        pack = _pack(unit)
        resp = ClinicalResponse(case_id="c1", urgency="urgent", severity="moderate",
                                narrative="synthèse")
        resp.citations = [
            {"marker": "[1]", "unit_id": "eu-1",
             "quote": "L'artésunate IV est le traitement de référence",
             "full": "OMS. Guide, section « Traitement » (2023) [eu-1]"},
            {"marker": "[1]", "unit_id": "eu-fantome",
             "quote": "inventé", "full": "Fantôme [eu-fantome]"},
        ]
        r = verify_citations(resp, pack)
        assert not r["passed"]
        assert any("absente du pack" in p for p in r["problems"])
        assert any("dupliqués" in p for p in r["problems"])
        biblio = format_bibliography(pack)
        assert "OMS" in biblio and "[eu-1]" in biblio
