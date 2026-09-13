"""Tests du moteur de règles cliniques — cas réels et cas limites.

Chaque test référence le résultat attendu par la littérature (valeur témoin).
"""
import pytest

from medisuite_rules import triage, emergency, cardiology, pneumology, nephrology
from medisuite_rules import oncology, gyne_obstetrique, neurology, psy_geriatrie
from medisuite_rules import derma_ent_ophtalmo, gastro_rheuma_uro, lab_qc, scores


# ---------------------------------------------------------------- triage

def test_qsofa_sepsis_reconnu():
    # RR 28, PAS 85, GCS<15 → qSOFA 3 = sepsis probable
    r = triage.qsofa(freq_resp=28, pas_systolique=85, gcs_ou_avpu="V")
    assert r["score"] == 3 and "élevé" in r["risque"]


def test_qsofa_negatif():
    assert triage.qsofa(16, 120, "alerte")["score"] == 0


def test_esi_reanimation():
    r = triage.esi(niveau_ressources=0, voies_aeriennes_stables=False)
    assert r["niveau"] == 1


def test_news2_critique():
    r = triage.news2(freq_resp=25, spo2=90, o2_supplementaire=True, pas=85,
                     pouls=125, conscience="V", temperature=38.9)
    assert r["score"] >= 7  # niveau "émergent"


# ---------------------------------------------------------------- urgences

def test_gcs_coma_profond():
    assert emergency.gcs("aucun", "aucun", "aucun")["score"] == 3


def test_gcs_normal():
    assert emergency.gcs("spontane", "oriente", "obey")["score"] == 15


def test_gcs_invalide_leve_erreur():
    with pytest.raises(ValueError):
        emergency.gcs("xyz", "oriente", "obey")


def test_wells_pe_fort():
    r = emergency.wells_pe(True, True, True, False, True, False, True)
    assert r["score"] >= 6 and "fort" in r["probabilite_pretest"]


def test_parkland():
    # 70 kg, 30 % SBC → 4×70×30 = 8400 mL/24 h ; moitié (4200) en 8 h
    r = emergency.parkland(70, 30, heures_depuis_brule=0)
    assert r["total_24h_ml"] == 8400 and r["premiere_8h_ml"] == 4200


def test_parkland_retard_compense():
    r = emergency.parkland(70, 30, heures_depuis_brule=16)
    assert r["reste_16h_ml"] < 4200  # retard déduit


def test_iss_polytrauma():
    r = emergency.iss([4, 3, 2])  # régions distinctes
    assert r["score"] == 29 and r["majeur"]


def test_curbs65_ambulatoire_vs_reanimation():
    assert emergency.curbs65(False, 4, 18, 120, 30)["conduite"] == "ambulatoire"
    r = emergency.curbs65(True, 9, 32, 85, 70)
    assert r["score"] == 5


# ---------------------------------------------------------------- cardiologie

def test_chads2ds2vasc_haut_risque():
    r = cardiology.chads2ds2vasc(False, True, False, True, False, 78, True)
    assert r["score"] >= 3 and r["anticoagulation"] == "recommandée"


def test_heart_score_sortie():
    r = cardiology.heart_score("faiblement", "normal", 32, 0, "normale")
    assert r["score"] == 0 and "sortie" in r["conduite"]


def test_killip_choc():
    assert cardiology.killip(False, False, True)["classe"] == 4


# ---------------------------------------------------------------- pneumologie

def test_spirometrie_obstructive():
    r = pneumology.spirometry_interpretation(fev1_l=1.4, fvc_l=3.5, fev1_theo_pct=40)
    assert r["pattern"] == "obstructif" and "sévère" in r["gravite_obstruction"]


def test_gold_groupe_e():
    r = pneumology.gold_group(mmc_pct=70, dyspnee_mrc=2, exacerbations_12m=3,
                              hospitalisation_exacerbation=False)
    assert r["groupe"] == "E"


def test_stop_bang_eleve():
    r = pneumology.stop_bang(True, True, True, True, True, True, True, True)
    assert r["score"] == 8 and "élevé" in r["risque"]


# ---------------------------------------------------------------- néphrologie

def test_ckd_epi_2021_homme_50ans():
    # créat 1.0 mg/dL, homme 50 ans → ~90 mL/min/1.73
    v = nephrology.ckd_epi_2021(50, "M", 1.0)
    assert 80 < v < 100


def test_ckd_epi_decroissance_avec_age():
    assert nephrology.ckd_epi_2021(80, "F", 1.2) < nephrology.ckd_epi_2021(40, "F", 1.2)


def test_kdigo_ckd_stade_g4():
    r = nephrology.kdigo_ckd_stage(egfr=25, albuminurie_mg_g=150)
    assert r["stade_gfr"] == "G4" and r["nephrologue"]


def test_kdigo_aki_stade3():
    r = nephrology.kdigo_aki_stage(creatinine_baseline=1.0, creatinine_actuelle=3.5,
                                   diurese_ml_kg_h=0.2)
    assert r["stade"] == 3


def test_ktv_dialyse_adequate():
    r = nephrology.ktv_daugirdas(uree_pre_mmol_l=25, uree_post_mmol_l=7,
                                 uf_total_l=2, poids_post_kg=70, duree_h=4)
    assert r["adequate"] and r["ktv"] > 1.2


# ---------------------------------------------------------------- oncologie

def test_birads_masse_suspecte():
    r = oncology.birads(masse=True, microcalcifications="suspectes",
                        asymetrie=False, aire_axillaire=True)
    assert r["categorie"] == "BI-RADS 4" and "biopsie" in r["conduite"]


def test_fleischner_petit_nodule_pas_de_suivi():
    r = oncology.fleischner(nodule_mm=4, risque_eleve=False, nodule_solide=True)
    assert "aucun suivi" in r["conduite"]


def test_fleischner_gros_nodule():
    r = oncology.fleischner(nodule_mm=9, risque_eleve=False, nodule_solide=True)
    assert "3-6 mois" in r["conduite"]


def test_tnm_breast_metastatique():
    assert oncology.tnm_breast_stage(1.0, "cN0", True, 1)["stade"] == "IV"


def test_aspects_ischemie_limitee():
    regions = {r: 1 for r in ["caudate", "insula", "internal_capsule",
                              "M1", "M2", "M3", "M4", "M5", "M6", "lenticular"]}
    regions["insula"] = 0
    r = neurology.aspects(regions)
    assert r["score"] == 9 and r["thrombectomie_candidate"]


def test_aspects_regions_incompletes_leve_erreur():
    with pytest.raises(ValueError):
        neurology.aspects({"M1": 1})


# ---------------------------------------------------------------- gynéco-obstétrique

def test_iota_benigne():
    r = gyne_obstetrique.iota_simple_rules(M_regles=[], B_regles=["paroi fine <1mm"])
    assert "bénigne" in r["verdict"]


def test_iota_maligne():
    r = gyne_obstetrique.iota_simple_rules(
        M_regles=["irrégulier", "ascite", "solide"], B_regles=[])
    assert "maligne" in r["verdict"]


def test_rotterdam_sopk():
    r = gyne_obstetrique.rotterdam_pcos(True, True, False, 20, 12.5)
    assert r["sopk"] and r["criteres_positifs"] >= 2


def test_bishop_defavorable():
    r = gyne_obstetrique.bishop(1, 20, -3, "ferme", "postérieure")
    assert r["score"] <= 3 and "maturation" in r["conduite"]


# ---------------------------------------------------------------- psychiatrie/gériatrie

def test_phq9_severe():
    r = psy_geriatrie.phq9([3] * 9)
    assert r["score"] == 27 and "sévère" in r["severite"] and r["item9_positif"]


def test_phq9_invalide():
    with pytest.raises(ValueError):
        psy_geriatrie.phq9([9] * 9)


def test_cssrs_urgence():
    r = psy_geriatrie.cssrs_risk(False, True, True, True, False)
    assert "URGENCE" in r["conduite"]


def test_fried_fragile():
    r = psy_geriatrie.fried(True, True, True, False, False)
    assert r["phenotype"] == "fragile"


def test_braden_risque_eleve():
    r = psy_geriatrie.braden(2, 2, 1, 2, 2, 2)
    assert r["score"] <= 12 and "élevé" in r["risque"]


def test_barthel_invalide_leve_erreur():
    with pytest.raises(ValueError):
        psy_geriatrie.barthel({"alimentation": 5})


# ---------------------------------------------------------------- derma/ENT/ophtalmo

def test_abcde_biopsie():
    r = derma_ent_ophtalmo.abcde(True, True, True, 8, True)
    assert r["alertes"] >= 2 and "biopsie" in r["conduite"]


def test_pası_severe():
    r = derma_ent_ophtalmo.pasi(3, 3, 3, [50, 50, 50, 50])
    assert r["pasi"] > 30 and "sévère" in r["severite"] and r["traitement_systemique"]


def test_pta_oms():
    r = derma_ent_ophtalmo.pta_audiogramme({"500": 40, "1000": 45, "2000": 55,
                                            "4000": 60})
    assert r["pta_db"] == 50 and "modérée" in r["grade_oms"]


def test_bppv_epley():
    r = derma_ent_ophtalmo.bppv_interpretation(True, False, True, True)
    assert r["bppv"] and "Epley" in r["traitement"]


def test_dr_proliferative():
    r = derma_ent_ophtalmo.retinopathie_diabetique(True, True, False, True, True,
                                                   False, True)
    assert r["stade_icdr"] == "proliférative" and r["traitement_anti_vegf"]


# ---------------------------------------------------------------- gastro/rhumato/uro

def test_child_pugh_c():
    r = gastro_rheuma_uro.child_pugh(5.0, 2.0, 2.5, "réfractaire", "grade_3_4")
    assert r["classe"].startswith("C")


def test_meld_prioritaire():
    r = gastro_rheuma_uro.meld(6.0, 3.0, 2.5, 128, True)
    assert r["meld_na"] >= 20


def test_das28_activite_elevee():
    r = gastro_rheuma_uro.das28(15, 10, 60, 80)
    assert r["activite"] == "élevée" and r["biotherapie_indiquee"]


def test_gleason_grade_groups():
    assert gastro_rheuma_uro.gleason_grade_group(3, 3)["grade_group"] == 1
    assert gastro_rheuma_uro.gleason_grade_group(4, 3)["grade_group"] == 3
    assert gastro_rheuma_uro.gleason_grade_group(5, 4)["grade_group"] == 5


def test_ipss_severe():
    r = gastro_rheuma_uro.ipss(4, 5, 4, 4, 4, 5)
    assert r["gravite"] == "sévère"


def test_pirads_biopsie():
    r = gastro_rheuma_uro.pirads_lesions([{"zone": "périphérique", "t2": 1, "dw": 5}])
    assert r["pirads"] == 5 and r["biopsie_ciblee"]


# ---------------------------------------------------------------- laboratoire QC

def test_westgard_1_3s_rejet():
    r = lab_qc.westgard(values=[100, 118], mean=100, sd=5)  # z=[0, 3.6]
    assert r["violations"] == ["1_3s"] and not r["samples_released"]


def test_westgard_accepte():
    r = lab_qc.westgard(values=[99, 101, 100.5], mean=100, sd=5)
    assert r["decision"] == "accepté" and r["samples_released"]


def test_westgard_2_2s_biais():
    r = lab_qc.westgard(values=[111, 111.5], mean=100, sd=5)  # deux +2σ
    assert "2_2s" in r["violations"]


def test_delta_check_alerte():
    r = lab_qc.delta_check(value=9.0, previous=4.0, analyte="potassium")
    assert r["alerte"]  # +125 % > seuil 30 %


def test_resultat_critique_k():
    r = lab_qc.analyser_resultat("potassium", 7.2)
    assert r["critical"] and r["notification_urgente"] and r["statut_fhir"] == "critical"


def test_resultat_normal():
    r = lab_qc.analyser_resultat("hemoglobine", 13.5)
    assert r["flag"] == "normal" and not r["critical"]


def test_paludisme_severe():
    r = lab_qc.paludisme_tdr_positive(250000)
    assert "hospitalisation" in r["traitement"]


# ---------------------------------------------------------------- utilitaires

def test_imc_oms():
    assert scores.imc(70, 1.75) == 22.9
    assert scores.categorie_oms(31.5) == "obésité"


def test_grade_bandes():
    assert scores.grade(12, [(9, "A"), (18, "B")]) == "B"
