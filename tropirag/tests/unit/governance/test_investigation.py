"""Gouvernance — descripteur, mode fail-closed, calendrier M+18, garde 451."""
from __future__ import annotations

from datetime import date

import pytest

from tropirag.governance import investigation as gov

M0 = date(2025, 6, 1)  # jalon de déploiement — verrou M+18 : 2026-12-01


class TestDescripteur:
    def test_phrase_reglementaire_exacte(self):
        """Le libellé backend = bandeau portail (scr.ai_banner) — un seul
        libellé réglementaire, affiché ET appliqué."""
        assert gov.BANNER_TEXT == (
            "Sorties IA NON VALIDÉES cliniquement — investigation R6-R8 en cours, "
            "verrou M+18 ; toute décision clinique sur ces sorties est interdite."
        )

    def test_descripteur_complet(self):
        s = gov.stamp()
        assert s["statut"] == "investigation"
        assert s["protocole"] == "MEDISUITE-CI-01"
        assert s["phases_en_cours"] == ["R6", "R7", "R8"]
        assert s["verrou"] == "M+18"
        assert s["decision_clinique"] == "interdite"
        assert any("MDR" in r and "Annexe XV" in r for r in s["references"])
        assert any("ISO 14155" in r for r in s["references"])

    def test_decisions_paths_couvrent_les_sorties_cds(self):
        for p in ("/api/v1/cases", "/api/v1/evidence", "/api/v1/surveillance"):
            assert p in gov.DECISION_PATHS


class TestModeFailClosed:
    def test_defaut_verrouille(self, monkeypatch):
        monkeypatch.delenv("MEDISUITE_GOVERNANCE_MODE", raising=False)
        monkeypatch.delenv("MEDISUITE_GOVERNANCE_CE_ACK", raising=False)
        assert gov.governance_mode() == "locked"
        assert gov.is_decisional_use_allowed() is False

    def test_mode_inconnu_retombe_sur_verrouille(self, monkeypatch):
        monkeypatch.setenv("MEDISUITE_GOVERNANCE_MODE", "production")
        assert gov.governance_mode() == "locked"

    def test_certified_sans_ack_refuse(self, monkeypatch):
        """Opt-in à double clé : mode certified SANS l'accusé CE → verrou."""
        monkeypatch.setenv("MEDISUITE_GOVERNANCE_MODE", "certified")
        monkeypatch.delenv("MEDISUITE_GOVERNANCE_CE_ACK", raising=False)
        assert gov.governance_mode() == "locked"

    def test_certified_double_optin(self, monkeypatch):
        """Scénario post-R8 : marquage CE + accusé explicite → sorties
        décisionnelles autorisées, le tampon passe à `certified`."""
        monkeypatch.setenv("MEDISUITE_GOVERNANCE_MODE", "certified")
        monkeypatch.setenv("MEDISUITE_GOVERNANCE_CE_ACK", "ce")
        assert gov.is_decisional_use_allowed() is True
        s = gov.stamp()
        assert s["statut"] == "certified"
        assert s["decision_clinique"] == "autorisée"
        assert s["phases_en_cours"] == []


class TestCalendrierM18:
    def test_add_months_plafond_fin_de_mois(self):
        assert gov.add_months(date(2025, 1, 31), 1) == date(2025, 2, 28)
        assert gov.add_months(date(2024, 1, 31), 1) == date(2024, 2, 29)  # bissextile
        assert gov.add_months(date(2025, 6, 1), 18) == date(2026, 12, 1)

    def test_m18_date(self):
        assert gov.m18_date(M0) == date(2026, 12, 1)

    def test_status_avant_verrou_phase_r6(self):
        st = gov.m18_status(date(2026, 9, 15), M0)
        assert st["pose"] is False
        assert st["phase_active"] == "R6"
        assert st["jours_avant_verrou"] == 77
        assert st["mois_ecoules"] == 15
        assert st["decision_clinique"] == "interdite"

    def test_status_apres_verrou_phase_r7(self):
        """Le verrou de base M+18 posé → R7 (rapport clinique) mais l'usage
        décisionnel reste interdit jusqu'au CE (R8)."""
        st = gov.m18_status(date(2026, 12, 2), M0)
        assert st["pose"] is True
        assert st["phase_active"] == "R7"
        assert st["decision_clinique"] == "interdite"

    def test_status_jour_du_verrou(self):
        st = gov.m18_status(gov.m18_date(M0), M0)
        assert st["pose"] is True
        assert st["jours_avant_verrou"] == 0


class TestGarde451:
    def test_refus_structure(self):
        d = gov.finalize_denial(case_id="CASE-X")
        assert d["error"] == "clinical_decision_locked"
        assert d["status_code"] == 451
        assert d["case_id"] == "CASE-X"
        assert d["governance"]["decision_clinique"] == "interdite"
        assert "marquage CE" in d["reprise"]

    def test_refus_sans_case_id(self):
        assert "case_id" not in gov.finalize_denial()

    @pytest.mark.parametrize("m0,attendu", [
        (date(2025, 6, 1), "2026-12-01"),
        (date(2025, 3, 15), "2026-09-15"),
        (date(2026, 1, 31), "2027-07-31"),
    ])
    def test_verrous_m18_parametres(self, m0, attendu):
        assert gov.m18_date(m0).isoformat() == attendu
