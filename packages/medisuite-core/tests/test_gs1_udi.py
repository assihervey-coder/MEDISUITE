"""Tests UDI-EID GS1 (v0.7) : GTIN, Application Identifiers, Digital Link."""
from medisuite_core import gs1_udi

# GTIN de test : construits par le module lui-même (jamais inventés à la main)
GTIN14 = gs1_udi.build_gtin14("0376022176001")   # → 03760221760012
GTIN13 = "3760221760011"                          # EAN-13 (clé calculée)


# ── GTIN (AI 01) ─────────────────────────────────────────────────────────────

def test_check_digit_gtin13():
    # calcul vérifié à la main : 376022176001 → somme pondérée 69 → clé 1
    assert gs1_udi.gtin_check_digit("376022176001") == "1"
    assert gs1_udi.validate_gtin(GTIN13) == GTIN13


def test_build_gtin14_avec_indicateur():
    assert gs1_udi.build_gtin14("0376022176001") == GTIN14


def test_validate_gtin_invalide():
    for bad in ("03760221760021",      # clé fausse
                "037602217600",        # trop court
                "03760221760X28",      # non numérique
                ""):
        try:
            gs1_udi.validate_gtin(bad)
            raised = False
        except gs1_udi.Gs1UdiError:
            raised = True
        assert raised


def test_basic_udi_di_modele():
    budi = gs1_udi.basic_udi_di()
    assert len(budi) == 14 and budi.startswith("0")
    assert budi == gs1_udi.build_gtin14("0" + gs1_udi.DEMO_GTN_BASE_12)
    try:
        gs1_udi.basic_udi_di("260")  # base trop courte
        raised = False
    except gs1_udi.Gs1UdiError:
        raised = True
    assert raised


# ── Dates GS1 (AI 11 / 17) ───────────────────────────────────────────────────

def test_dates_roundtrip():
    assert gs1_udi.fmt_gs1_date("2027-12-31") == "271231"
    assert gs1_udi.parse_gs1_date("271231").isoformat() == "2027-12-31"


def test_date_jour_inconnu_convention_gs1():
    # '00' = jour inconnu → dernier jour du mois
    assert gs1_udi.parse_gs1_date("270200").isoformat() == "2027-02-28"
    assert gs1_udi.parse_gs1_date("271200").isoformat() == "2027-12-31"


def test_dates_invalides():
    for bad in ("2027-13-01", "271332", "2712", "abc123"):
        try:
            (gs1_udi.parse_gs1_date if len(bad) == 6 else gs1_udi.fmt_gs1_date)(bad)
            raised = False
        except gs1_udi.Gs1UdiError:
            raised = True
        assert raised


# ── Élément-string (contenu DataMatrix) ──────────────────────────────────────

def test_element_string_ordre_et_fnc1():
    es = gs1_udi.build_element_string(GTIN14, lot="LOT42",
                                      expiry="2027-12-31",
                                      prod="2026-09-14", serial="SN001")
    # (01) fixe, (17) fixe, (11) fixe, (10) variable suivi de FNC1, (21) final
    assert es == f"01{GTIN14}172712311126091410LOT42\x1d21SN001"


def test_element_string_lot_dernier_sans_fnc1():
    es = gs1_udi.build_element_string(GTIN14, lot="LOT42")
    assert es == f"01{GTIN14}10LOT42"           # pas de FNC1 final
    es = gs1_udi.build_element_string(GTIN14, lot="L", serial="S1")
    assert es == f"01{GTIN14}10L\x1d21S1"       # FNC1 entre (10) et (21)


def test_roundtrip_build_parse():
    # NB : l'espace n'appartient pas au jeu GS1 des AIs variables (fail-closed)
    es = gs1_udi.build_element_string(GTIN14, lot="LOT-A1", expiry="2027-12-31",
                                      prod="2026-09-14", serial="SN/9+1")
    parsed = gs1_udi.parse_element_string(es)
    assert parsed == {"01": GTIN14, "17": "271231", "11": "260914",
                      "10": "LOT-A1", "21": "SN/9+1"}


def test_parse_rejets():
    for bad in ("", "1000012345",                 # pas de (01) en tête
                f"01{GTIN14}99XYZ",               # AI inconnu
                f"0103760221760021",              # GTIN clé fausse dans (01)
                f"01{GTIN14}10LOT??",):           # caractère interdit AI (10)
        try:
            gs1_udi.parse_element_string(bad)
            raised = False
        except gs1_udi.Gs1UdiError:
            raised = True
        assert raised


# ── GS1 Digital Link (EID) ───────────────────────────────────────────────────

def test_digital_link():
    url = gs1_udi.gs1_digital_link(GTIN14, lot="LOT42", serial="SN001")
    assert url == f"https://id.gs1.org/01/{GTIN14}/10/LOT42/21/SN001"
    assert gs1_udi.gs1_digital_link(GTIN14).endswith(f"/01/{GTIN14}")


# ── Étiquette complète (MDR Annexe I §23.2) ──────────────────────────────────

def test_label_payload_complet_et_verifie():
    label = gs1_udi.label_payload(GTIN14, lot="LOT42", expiry="2027-12-31",
                                  prod="2026-09-14", serial="SN001",
                                  version_logiciel="v0.7.0")
    assert label["basic_udi_di"] == gs1_udi.basic_udi_di()
    assert label["udi_di"] == GTIN14
    assert label["emetteur"]["agence"] == "GS1 Côte d'Ivoire"
    ok, err = gs1_udi.verify_label_payload(label)
    assert ok and err is None


def test_verify_label_payload_detecte_les_ecarts():
    label = gs1_udi.label_payload(GTIN14, lot="LOT42", serial="SN001")
    label["lot"] = "AUTRE-LOT"
    ok, err = gs1_udi.verify_label_payload(label)
    assert not ok and err and "lot" in err
    label2 = gs1_udi.label_payload(GTIN14)
    label2["element_string"] = "99BREAK"
    ok, err = gs1_udi.verify_label_payload(label2)
    assert not ok
