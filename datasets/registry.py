"""Registre des 26 modules : features cliniques et schémas de labels.

Source unique pour le générateur de datasets synthétiques. Les features sont
des variables cliniquement NOMMÉES (unités cohérentes avec docs/MODULES.md) ;
les labels suivent la tâche déclarée dans ai/multimodal/configs/*.yaml
(binaire, multiclasse, multilabel, régression, segmentation).

⚠️ AUCUNE donnée réelle : tout est tiré de distributions uniformes seedées,
   avec un signal apprenant injecté sur les features discriminantes.
"""
from __future__ import annotations

# (no_module, slug) — aligné sur services/registry.py SPECIALTIES + cœur 01-02
MODULES: list[tuple[int, str]] = [
    (1, "imaging"), (2, "laboratory"), (3, "oncology"), (4, "tumor"),
    (5, "ophthalmology"), (6, "diabetes"), (7, "traumatology"),
    (8, "cardiology"), (9, "pneumology"), (10, "obstetrics"),
    (11, "gynecology"), (12, "fertility"), (13, "neurology"),
    (14, "psychiatry"), (15, "pediatrics"), (16, "nephrology"),
    (17, "gastroenterology"), (18, "dermatology"), (19, "ent"),
    (20, "rheumatology"), (21, "urology"), (22, "nuclear_medicine"),
    (23, "radiotherapy"), (24, "anesthesia"), (25, "geriatrics"),
    (26, "emergency"),
]

# Une entrée = features {nom: (lo, hi)} + discriminantes (signal apprenant)
# + spec de label. `task` est relu des configs IA au moment de la génération.
SPEC: dict[str, dict] = {
    "imaging": {
        "features": {"qualite_image": (0.2, 1.0), "score_anomalie": (0.0, 1.0),
                     "bruit_std": (0.0, 0.3), "dose_ct_gy": (1.0, 20.0),
                     "contraste": (0.1, 1.0)},
        "discriminantes": ["score_anomalie", "contraste"],
        "label": {"task": "classification", "label_nom": "anomalie",
                  "prevalence": 0.35},
    },
    "laboratory": {
        "features": {"hgb_g_dl": (6.0, 18.0), "wbc_g_l": (1.0, 25.0),
                     "plt_g_l": (30.0, 500.0), "creatinine_mg_l": (3.0, 80.0),
                     "glycemie_g_l": (0.4, 4.5), "crp_mg_l": (0.0, 300.0)},
        "discriminantes": ["crp_mg_l", "wbc_g_l"],
        "label": {"task": "regression", "target_nom": "score_severite_0_10",
                  "lo": 0.0, "hi": 10.0},
    },
    "oncology": {
        "features": {"ca_125_u_ml": (5.0, 800.0), "psa_ng_ml": (0.1, 60.0),
                     "taille_tumeur_mm": (2.0, 120.0), "ecog": (0.0, 4.0),
                     "age": (20.0, 95.0)},
        "discriminantes": ["ca_125_u_ml", "taille_tumeur_mm"],
        "label": {"task": "multiclass",
                  "classes": ["sain", "benin", "invasif_precoce",
                              "invasif_avance"],
                  "poids": [0.4, 0.3, 0.2, 0.1]},
    },
    "tumor": {
        "features": {"volume_tumeur_mm3": (500.0, 90000.0),
                     "oedema_mm": (0.0, 15.0), "grade_oms": (1.0, 4.0),
                     "karnofsky": (40.0, 100.0)},
        "discriminantes": ["volume_tumeur_mm3", "oedema_mm"],
        "label": {"task": "segmentation", "target_nom": "fraction_lesionnelle",
                  "lo": 0.0, "hi": 0.6},
    },
    "ophthalmology": {
        "features": {"cd_ratio": (0.1, 0.95), "rnfl_um": (45.0, 120.0),
                     "acuite_logmar": (-0.1, 1.8), "hba1c_pct": (5.0, 12.0),
                     "pio_mmhg": (8.0, 42.0)},
        "discriminantes": ["cd_ratio", "rnfl_um"],
        "label": {"task": "multiclass",
                  "classes": ["rd_absente", "rd_non_proliferante",
                              "rd_proliferante"],
                  "poids": [0.5, 0.3, 0.2]},
    },
    "diabetes": {
        "features": {"hba1c_pct": (5.0, 14.0), "tir_pct": (20.0, 95.0),
                     "age_dx": (10.0, 70.0), "imc": (16.0, 45.0),
                     "fbg_g_l": (0.6, 4.0)},
        "discriminantes": ["hba1c_pct", "tir_pct"],
        "label": {"task": "regression", "target_nom": "risque_complication",
                  "lo": 0.0, "hi": 1.0},
    },
    "traumatology": {
        "features": {"iss": (4.0, 50.0), "gcs": (3.0, 15.0), "age": (18.0, 95.0),
                     "fractures_n": (1.0, 6.0), "cobb_deg": (5.0, 70.0)},
        "discriminantes": ["iss", "fractures_n"],
        "label": {"task": "multilabel",
                  "classes": ["fracture_ouverte", "atteinte_viscerale",
                              "chirurgie_requise"],
                  "p": [0.2, 0.3, 0.4]},
    },
    "cardiology": {
        "features": {"fevg_pct": (15.0, 70.0), "troponine_ng_ml": (0.01, 10.0),
                     "bpm": (40.0, 180.0), "qt_ms": (320.0, 560.0),
                     "cha2ds2_vasc": (0.0, 9.0)},
        "discriminantes": ["troponine_ng_ml", "fevg_pct"],
        "label": {"task": "multiclass",
                  "classes": ["stable", "angor_instable", "sca"],
                  "poids": [0.55, 0.25, 0.2]},
    },
    "pneumology": {
        "features": {"spo2_pct": (70.0, 100.0), "fev1_pct": (25.0, 110.0),
                     "wells": (0.0, 12.0), "crp_mg_l": (1.0, 300.0),
                     "paquets_annees": (0.0, 80.0)},
        "discriminantes": ["spo2_pct", "fev1_pct"],
        "label": {"task": "multilabel",
                  "classes": ["tb_active", "bpco", "embolie"],
                  "p": [0.15, 0.35, 0.2]},
    },
    "obstetrics": {
        "features": {"tas_mmhg": (80.0, 180.0), "proteinurie_g_j": (0.0, 5.0),
                     "clarte_nucale_mm": (0.8, 6.0), "bishop": (0.0, 13.0),
                     "age_gestation_sem": (24.0, 42.0)},
        "discriminantes": ["tas_mmhg", "proteinurie_g_j"],
        "label": {"task": "classification", "label_nom": "pre_eclampsie",
                  "prevalence": 0.2},
    },
    "gynecology": {
        "features": {"pap_bethesda": (0.0, 5.0), "hpv_vl_log": (0.0, 9.0),
                     "iota_score": (0.0, 10.0), "orads": (1.0, 5.0),
                     "saignement_j": (0.0, 30.0)},
        "discriminantes": ["iota_score", "orads"],
        "label": {"task": "classification", "label_nom": "malignite_suspectee",
                  "prevalence": 0.25},
    },
    "fertility": {
        "features": {"amh_ng_ml": (0.1, 8.0), "cfa_n": (1.0, 30.0),
                     "spermato_millions": (0.0, 120.0), "fsh_ui_l": (2.0, 25.0),
                     "age_femme": (20.0, 42.0)},
        "discriminantes": ["amh_ng_ml", "spermato_millions"],
        "label": {"task": "regression", "target_nom": "proba_conception",
                  "lo": 0.0, "hi": 1.0},
    },
    "neurology": {
        "features": {"nihss": (0.0, 30.0), "aspects": (0.0, 10.0),
                     "mmse": (0.0, 30.0), "age": (40.0, 95.0),
                     "delai_onset_h": (0.5, 24.0)},
        "discriminantes": ["nihss", "aspects"],
        "label": {"task": "classification", "label_nom": "avc_ischemique",
                  "prevalence": 0.4},
    },
    "psychiatry": {
        "features": {"phq9": (0.0, 27.0), "gad7": (0.0, 21.0),
                     "audit": (0.0, 40.0), "sommeil_h": (2.0, 11.0),
                     "cssrs": (0.0, 5.0)},
        "discriminantes": ["phq9", "gad7"],
        "label": {"task": "regression", "target_nom": "severite_globale",
                  "lo": 0.0, "hi": 30.0},
    },
    "pediatrics": {
        "features": {"poids_z": (-3.0, 2.5), "taille_z": (-3.0, 2.5),
                     "apgar": (1.0, 10.0), "bilirubine_mg_dl": (1.0, 18.0),
                     "age_mois": (0.0, 60.0)},
        "discriminantes": ["poids_z", "taille_z"],
        "label": {"task": "regression", "target_nom": "indice_croissance",
                  "lo": 0.0, "hi": 1.0},
    },
    "nephrology": {
        "features": {"creatinine_mg_l": (4.0, 120.0), "dfao_ckdepi": (3.0, 120.0),
                     "kaliemia_mmol_l": (2.5, 6.8), "proteinurie_g_j": (0.0, 6.0),
                     "ktv": (0.6, 2.2)},
        "discriminantes": ["dfao_ckdepi", "creatinine_mg_l"],
        "label": {"task": "regression", "target_nom": "stade_ckd_1_5",
                  "lo": 1.0, "hi": 5.0},
    },
    "gastroenterology": {
        "features": {"forrest": (1.0, 3.0), "li_rads": (1.0, 5.0),
                     "hb_g_dl": (4.0, 16.0), "alcool_u_sem": (0.0, 60.0),
                     "nodule_mm": (2.0, 60.0)},
        "discriminantes": ["forrest", "hb_g_dl"],
        "label": {"task": "classification",
                  "label_nom": "hemorragie_active", "prevalence": 0.3},
    },
    "dermatology": {
        "features": {"diametre_mm": (2.0, 60.0), "asymetrie": (0.0, 3.0),
                     "couleurs_n": (1.0, 6.0), "breslow_mm": (0.1, 8.0),
                     "evolutivite": (0.0, 3.0)},
        "discriminantes": ["breslow_mm", "asymetrie"],
        "label": {"task": "multiclass",
                  "classes": ["nevus", "douteux", "melanome"],
                  "poids": [0.5, 0.3, 0.2]},
    },
    "ent": {
        "features": {"perte_db": (10.0, 90.0), "lund_mackay": (0.0, 24.0),
                     "pta_db": (10.0, 85.0), "tinnitus": (0.0, 3.0),
                     "hpv_pos": (0.0, 1.0)},
        "discriminantes": ["perte_db", "lund_mackay"],
        "label": {"task": "classification",
                  "label_nom": "tumeur_orl_suspectee", "prevalence": 0.2},
    },
    "rheumatology": {
        "features": {"das28": (1.0, 9.0), "crp_mg_l": (1.0, 120.0),
                     "facteur_rhumato_ui": (0.0, 300.0), "sledai": (0.0, 24.0),
                     "kl_grade": (0.0, 4.0)},
        "discriminantes": ["das28", "crp_mg_l"],
        "label": {"task": "regression", "target_nom": "activite_0_10",
                  "lo": 0.0, "hi": 10.0},
    },
    "urology": {
        "features": {"pirads": (1.0, 5.0), "ips": (0.0, 35.0),
                     "psa_ng_ml": (0.1, 80.0), "gleason": (6.0, 10.0),
                     "renal_score": (4.0, 12.0)},
        "discriminantes": ["pirads", "gleason"],
        "label": {"task": "classification",
                  "label_nom": "ca_prostate_significatif", "prevalence": 0.28},
    },
    "nuclear_medicine": {
        "features": {"suv_max": (1.0, 40.0), "mtv_cm3": (1.0, 400.0),
                     "tlg": (1.0, 1200.0), "dose_mbq": (100.0, 7400.0),
                     "dlco_pct": (30.0, 110.0)},
        "discriminantes": ["suv_max", "mtv_cm3"],
        "label": {"task": "regression", "target_nom": "reponse_pct",
                  "lo": -40.0, "hi": 100.0},
    },
    "radiotherapy": {
        "features": {"dose_gy": (30.0, 74.0), "fractions": (5.0, 35.0),
                     "v20_pct": (5.0, 45.0), "gamma_pct": (85.0, 100.0),
                     "eqd2_gy": (40.0, 90.0)},
        "discriminantes": ["v20_pct", "eqd2_gy"],
        "label": {"task": "regression", "target_nom": "toxicite_0_1",
                  "lo": 0.0, "hi": 1.0},
    },
    "anesthesia": {
        "features": {"asa": (1.0, 5.0), "lee_rcri": (0.0, 4.0),
                     "stopbang": (0.0, 8.0), "sofa": (0.0, 24.0),
                     "duree_chir_h": (0.5, 10.0)},
        "discriminantes": ["asa", "sofa"],
        "label": {"task": "classification",
                  "label_nom": "evenement_perop", "prevalence": 0.18},
    },
    "geriatrics": {
        "features": {"fried": (0.0, 5.0), "rockwood": (1.0, 9.0),
                     "tug_s": (7.0, 45.0), "mna": (7.0, 30.0),
                     "beers_n": (0.0, 12.0), "braden": (6.0, 23.0)},
        "discriminantes": ["fried", "tug_s"],
        "label": {"task": "classification", "label_nom": "chute_12_mois",
                  "prevalence": 0.3},
    },
    "emergency": {
        "features": {"esi": (1.0, 5.0), "qsofa": (0.0, 3.0), "iss": (1.0, 50.0),
                     "nihss": (0.0, 30.0), "shock_index": (0.4, 1.8)},
        "discriminantes": ["qsofa", "shock_index"],
        "label": {"task": "multiclass",
                  "classes": ["hors_danger", "urgent", "tres_urgent", "vital"],
                  "poids": [0.35, 0.3, 0.2, 0.15]},
    },
}

# Vecteurs synthétiques par type de modalité (le générateur s'en sert)
VECTOR_MODALITIES = ("imaging_2d", "imaging_3d", "signal_1d", "waveform")
STRING_MODALITIES = ("texte", "genomique")
VECTOR_DIM = 16
GENOME_LEN = 60


def validate_spec() -> None:
    """Fail-fast : tout slug du registre doit porter ses métadonnées clés."""
    for no, slug in MODULES:
        spec = SPEC[slug]
        assert spec["features"] and spec["discriminantes"], slug
        for f in spec["discriminantes"]:
            assert f in spec["features"], f"{slug}: discriminante inconnue {f}"
        lab = spec["label"]
        task = lab["task"]
        if task == "classification":
            assert "label_nom" in lab and "prevalence" in lab, slug
        elif task in ("multiclass", "multilabel"):
            assert "classes" in lab and len(lab["classes"]) >= 2, slug
        elif task in ("regression", "segmentation"):
            assert "target_nom" in lab and "lo" in lab and "hi" in lab, slug
        else:
            raise AssertionError(f"{slug}: tâche inconnue {task}")
