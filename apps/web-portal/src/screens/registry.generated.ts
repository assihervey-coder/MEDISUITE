/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — NE PAS ÉDITER À LA MAIN.
 *  Régénérer : `make screens` · vérifier : `python tools/generate_screens.py --check`.
 */
import type { ScreenDef } from "./types";

export const SCREENS: ScreenDef[] = [
    {
      "id": "oncology:overview",
      "slug": "oncology",
      "urlSlug": "oncology",
      "moduleNo": 3,
      "icon": "🎗️",
      "label": "Oncologie",
      "service": "oncology-service",
      "kind": "overview",
      "route": "/module/oncology",
      "servicePath": "module/oncology",
      "scores": [
        "birads",
        "fleischner",
        "lung-rads",
        "tnm-breast",
        "roma",
        "ecog"
      ],
      "sigs": [
        {
          "endpoint": "birads",
          "fn": "birads",
          "params": [
            {
              "name": "masse",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "microcalcifications",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "asymetrie",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "aire_axillaire",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "densite_acr",
              "kind": "text",
              "hasDefault": true
            }
          ]
        },
        {
          "endpoint": "fleischner",
          "fn": "fleischner",
          "params": [
            {
              "name": "nodule_mm",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "risque_eleve",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "nodule_solide",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "lobes_superieurs_multiple",
              "kind": "text",
              "hasDefault": true
            }
          ]
        },
        {
          "endpoint": "lung-rads",
          "fn": "lung_rads",
          "params": [
            {
              "name": "nodule_mm",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "croissance",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "nodules_solid_mass",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "ganglions_suspects",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "tnm-breast",
          "fn": "tnm_breast_stage",
          "params": [
            {
              "name": "t_taille_cm",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "n_ganglionnaire",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "m_metastase",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "grade_histologique",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "roma",
          "fn": "roma_score",
          "params": [
            {
              "name": "ca125",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "he4",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "menopausee",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "ecog",
          "fn": "ecog",
          "params": [
            {
              "name": "karnofsky",
              "kind": "text",
              "hasDefault": true
            },
            {
              "name": "description",
              "kind": "text",
              "hasDefault": true
            }
          ]
        }
      ],
      "ai": {
        "task": "multiclass",
        "modalities": [
          "imaging_2d",
          "imaging_3d",
          "tabulaire",
          "texte",
          "genomique"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "multiclass",
        "labelNom": "",
        "classes": [
          "sain",
          "benin",
          "invasif_precoce",
          "invasif_avance"
        ],
        "features": [
          {
            "name": "ca_125_u_ml",
            "lo": 5.0,
            "hi": 800.0
          },
          {
            "name": "psa_ng_ml",
            "lo": 0.1,
            "hi": 60.0
          },
          {
            "name": "taille_tumeur_mm",
            "lo": 2.0,
            "hi": 120.0
          },
          {
            "name": "ecog",
            "lo": 0.0,
            "hi": 4.0
          },
          {
            "name": "age",
            "lo": 20.0,
            "hi": 95.0
          }
        ]
      }
    },
    {
      "id": "oncology:cas",
      "slug": "oncology",
      "urlSlug": "oncology",
      "moduleNo": 3,
      "icon": "🎗️",
      "label": "Oncologie",
      "service": "oncology-service",
      "kind": "cas",
      "route": "/module/oncology/cas",
      "servicePath": "module/oncology",
      "scores": [
        "birads",
        "fleischner",
        "lung-rads",
        "tnm-breast",
        "roma",
        "ecog"
      ],
      "sigs": [
        {
          "endpoint": "birads",
          "fn": "birads",
          "params": [
            {
              "name": "masse",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "microcalcifications",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "asymetrie",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "aire_axillaire",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "densite_acr",
              "kind": "text",
              "hasDefault": true
            }
          ]
        },
        {
          "endpoint": "fleischner",
          "fn": "fleischner",
          "params": [
            {
              "name": "nodule_mm",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "risque_eleve",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "nodule_solide",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "lobes_superieurs_multiple",
              "kind": "text",
              "hasDefault": true
            }
          ]
        },
        {
          "endpoint": "lung-rads",
          "fn": "lung_rads",
          "params": [
            {
              "name": "nodule_mm",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "croissance",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "nodules_solid_mass",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "ganglions_suspects",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "tnm-breast",
          "fn": "tnm_breast_stage",
          "params": [
            {
              "name": "t_taille_cm",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "n_ganglionnaire",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "m_metastase",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "grade_histologique",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "roma",
          "fn": "roma_score",
          "params": [
            {
              "name": "ca125",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "he4",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "menopausee",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "ecog",
          "fn": "ecog",
          "params": [
            {
              "name": "karnofsky",
              "kind": "text",
              "hasDefault": true
            },
            {
              "name": "description",
              "kind": "text",
              "hasDefault": true
            }
          ]
        }
      ],
      "ai": {
        "task": "multiclass",
        "modalities": [
          "imaging_2d",
          "imaging_3d",
          "tabulaire",
          "texte",
          "genomique"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "multiclass",
        "labelNom": "",
        "classes": [
          "sain",
          "benin",
          "invasif_precoce",
          "invasif_avance"
        ],
        "features": [
          {
            "name": "ca_125_u_ml",
            "lo": 5.0,
            "hi": 800.0
          },
          {
            "name": "psa_ng_ml",
            "lo": 0.1,
            "hi": 60.0
          },
          {
            "name": "taille_tumeur_mm",
            "lo": 2.0,
            "hi": 120.0
          },
          {
            "name": "ecog",
            "lo": 0.0,
            "hi": 4.0
          },
          {
            "name": "age",
            "lo": 20.0,
            "hi": 95.0
          }
        ]
      }
    },
    {
      "id": "oncology:detail",
      "slug": "oncology",
      "urlSlug": "oncology",
      "moduleNo": 3,
      "icon": "🎗️",
      "label": "Oncologie",
      "service": "oncology-service",
      "kind": "detail",
      "route": "/module/oncology/cas/:caseId",
      "servicePath": "module/oncology",
      "scores": [
        "birads",
        "fleischner",
        "lung-rads",
        "tnm-breast",
        "roma",
        "ecog"
      ],
      "sigs": [
        {
          "endpoint": "birads",
          "fn": "birads",
          "params": [
            {
              "name": "masse",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "microcalcifications",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "asymetrie",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "aire_axillaire",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "densite_acr",
              "kind": "text",
              "hasDefault": true
            }
          ]
        },
        {
          "endpoint": "fleischner",
          "fn": "fleischner",
          "params": [
            {
              "name": "nodule_mm",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "risque_eleve",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "nodule_solide",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "lobes_superieurs_multiple",
              "kind": "text",
              "hasDefault": true
            }
          ]
        },
        {
          "endpoint": "lung-rads",
          "fn": "lung_rads",
          "params": [
            {
              "name": "nodule_mm",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "croissance",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "nodules_solid_mass",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "ganglions_suspects",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "tnm-breast",
          "fn": "tnm_breast_stage",
          "params": [
            {
              "name": "t_taille_cm",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "n_ganglionnaire",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "m_metastase",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "grade_histologique",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "roma",
          "fn": "roma_score",
          "params": [
            {
              "name": "ca125",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "he4",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "menopausee",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "ecog",
          "fn": "ecog",
          "params": [
            {
              "name": "karnofsky",
              "kind": "text",
              "hasDefault": true
            },
            {
              "name": "description",
              "kind": "text",
              "hasDefault": true
            }
          ]
        }
      ],
      "ai": {
        "task": "multiclass",
        "modalities": [
          "imaging_2d",
          "imaging_3d",
          "tabulaire",
          "texte",
          "genomique"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "multiclass",
        "labelNom": "",
        "classes": [
          "sain",
          "benin",
          "invasif_precoce",
          "invasif_avance"
        ],
        "features": [
          {
            "name": "ca_125_u_ml",
            "lo": 5.0,
            "hi": 800.0
          },
          {
            "name": "psa_ng_ml",
            "lo": 0.1,
            "hi": 60.0
          },
          {
            "name": "taille_tumeur_mm",
            "lo": 2.0,
            "hi": 120.0
          },
          {
            "name": "ecog",
            "lo": 0.0,
            "hi": 4.0
          },
          {
            "name": "age",
            "lo": 20.0,
            "hi": 95.0
          }
        ]
      }
    },
    {
      "id": "oncology:ia",
      "slug": "oncology",
      "urlSlug": "oncology",
      "moduleNo": 3,
      "icon": "🎗️",
      "label": "Oncologie",
      "service": "oncology-service",
      "kind": "ia",
      "route": "/module/oncology/ia",
      "servicePath": "module/oncology",
      "scores": [
        "birads",
        "fleischner",
        "lung-rads",
        "tnm-breast",
        "roma",
        "ecog"
      ],
      "sigs": [
        {
          "endpoint": "birads",
          "fn": "birads",
          "params": [
            {
              "name": "masse",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "microcalcifications",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "asymetrie",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "aire_axillaire",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "densite_acr",
              "kind": "text",
              "hasDefault": true
            }
          ]
        },
        {
          "endpoint": "fleischner",
          "fn": "fleischner",
          "params": [
            {
              "name": "nodule_mm",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "risque_eleve",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "nodule_solide",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "lobes_superieurs_multiple",
              "kind": "text",
              "hasDefault": true
            }
          ]
        },
        {
          "endpoint": "lung-rads",
          "fn": "lung_rads",
          "params": [
            {
              "name": "nodule_mm",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "croissance",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "nodules_solid_mass",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "ganglions_suspects",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "tnm-breast",
          "fn": "tnm_breast_stage",
          "params": [
            {
              "name": "t_taille_cm",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "n_ganglionnaire",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "m_metastase",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "grade_histologique",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "roma",
          "fn": "roma_score",
          "params": [
            {
              "name": "ca125",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "he4",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "menopausee",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "ecog",
          "fn": "ecog",
          "params": [
            {
              "name": "karnofsky",
              "kind": "text",
              "hasDefault": true
            },
            {
              "name": "description",
              "kind": "text",
              "hasDefault": true
            }
          ]
        }
      ],
      "ai": {
        "task": "multiclass",
        "modalities": [
          "imaging_2d",
          "imaging_3d",
          "tabulaire",
          "texte",
          "genomique"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "multiclass",
        "labelNom": "",
        "classes": [
          "sain",
          "benin",
          "invasif_precoce",
          "invasif_avance"
        ],
        "features": [
          {
            "name": "ca_125_u_ml",
            "lo": 5.0,
            "hi": 800.0
          },
          {
            "name": "psa_ng_ml",
            "lo": 0.1,
            "hi": 60.0
          },
          {
            "name": "taille_tumeur_mm",
            "lo": 2.0,
            "hi": 120.0
          },
          {
            "name": "ecog",
            "lo": 0.0,
            "hi": 4.0
          },
          {
            "name": "age",
            "lo": 20.0,
            "hi": 95.0
          }
        ]
      }
    },
    {
      "id": "tumor:overview",
      "slug": "tumor",
      "urlSlug": "tumor",
      "moduleNo": 4,
      "icon": "🧠",
      "label": "Tumeurs",
      "service": "tumor-service",
      "kind": "overview",
      "route": "/module/tumor",
      "servicePath": "module/tumor",
      "scores": [
        "ecog"
      ],
      "sigs": [
        {
          "endpoint": "ecog",
          "fn": "ecog",
          "params": [
            {
              "name": "karnofsky",
              "kind": "text",
              "hasDefault": true
            },
            {
              "name": "description",
              "kind": "text",
              "hasDefault": true
            }
          ]
        }
      ],
      "ai": {
        "task": "segmentation",
        "modalities": [
          "imaging_3d",
          "tabulaire"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "segmentation",
        "labelNom": "fraction_lesionnelle",
        "classes": [],
        "features": [
          {
            "name": "volume_tumeur_mm3",
            "lo": 500.0,
            "hi": 90000.0
          },
          {
            "name": "oedema_mm",
            "lo": 0.0,
            "hi": 15.0
          },
          {
            "name": "grade_oms",
            "lo": 1.0,
            "hi": 4.0
          },
          {
            "name": "karnofsky",
            "lo": 40.0,
            "hi": 100.0
          }
        ]
      }
    },
    {
      "id": "tumor:cas",
      "slug": "tumor",
      "urlSlug": "tumor",
      "moduleNo": 4,
      "icon": "🧠",
      "label": "Tumeurs",
      "service": "tumor-service",
      "kind": "cas",
      "route": "/module/tumor/cas",
      "servicePath": "module/tumor",
      "scores": [
        "ecog"
      ],
      "sigs": [
        {
          "endpoint": "ecog",
          "fn": "ecog",
          "params": [
            {
              "name": "karnofsky",
              "kind": "text",
              "hasDefault": true
            },
            {
              "name": "description",
              "kind": "text",
              "hasDefault": true
            }
          ]
        }
      ],
      "ai": {
        "task": "segmentation",
        "modalities": [
          "imaging_3d",
          "tabulaire"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "segmentation",
        "labelNom": "fraction_lesionnelle",
        "classes": [],
        "features": [
          {
            "name": "volume_tumeur_mm3",
            "lo": 500.0,
            "hi": 90000.0
          },
          {
            "name": "oedema_mm",
            "lo": 0.0,
            "hi": 15.0
          },
          {
            "name": "grade_oms",
            "lo": 1.0,
            "hi": 4.0
          },
          {
            "name": "karnofsky",
            "lo": 40.0,
            "hi": 100.0
          }
        ]
      }
    },
    {
      "id": "tumor:detail",
      "slug": "tumor",
      "urlSlug": "tumor",
      "moduleNo": 4,
      "icon": "🧠",
      "label": "Tumeurs",
      "service": "tumor-service",
      "kind": "detail",
      "route": "/module/tumor/cas/:caseId",
      "servicePath": "module/tumor",
      "scores": [
        "ecog"
      ],
      "sigs": [
        {
          "endpoint": "ecog",
          "fn": "ecog",
          "params": [
            {
              "name": "karnofsky",
              "kind": "text",
              "hasDefault": true
            },
            {
              "name": "description",
              "kind": "text",
              "hasDefault": true
            }
          ]
        }
      ],
      "ai": {
        "task": "segmentation",
        "modalities": [
          "imaging_3d",
          "tabulaire"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "segmentation",
        "labelNom": "fraction_lesionnelle",
        "classes": [],
        "features": [
          {
            "name": "volume_tumeur_mm3",
            "lo": 500.0,
            "hi": 90000.0
          },
          {
            "name": "oedema_mm",
            "lo": 0.0,
            "hi": 15.0
          },
          {
            "name": "grade_oms",
            "lo": 1.0,
            "hi": 4.0
          },
          {
            "name": "karnofsky",
            "lo": 40.0,
            "hi": 100.0
          }
        ]
      }
    },
    {
      "id": "tumor:ia",
      "slug": "tumor",
      "urlSlug": "tumor",
      "moduleNo": 4,
      "icon": "🧠",
      "label": "Tumeurs",
      "service": "tumor-service",
      "kind": "ia",
      "route": "/module/tumor/ia",
      "servicePath": "module/tumor",
      "scores": [
        "ecog"
      ],
      "sigs": [
        {
          "endpoint": "ecog",
          "fn": "ecog",
          "params": [
            {
              "name": "karnofsky",
              "kind": "text",
              "hasDefault": true
            },
            {
              "name": "description",
              "kind": "text",
              "hasDefault": true
            }
          ]
        }
      ],
      "ai": {
        "task": "segmentation",
        "modalities": [
          "imaging_3d",
          "tabulaire"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "segmentation",
        "labelNom": "fraction_lesionnelle",
        "classes": [],
        "features": [
          {
            "name": "volume_tumeur_mm3",
            "lo": 500.0,
            "hi": 90000.0
          },
          {
            "name": "oedema_mm",
            "lo": 0.0,
            "hi": 15.0
          },
          {
            "name": "grade_oms",
            "lo": 1.0,
            "hi": 4.0
          },
          {
            "name": "karnofsky",
            "lo": 40.0,
            "hi": 100.0
          }
        ]
      }
    },
    {
      "id": "ophthalmology:overview",
      "slug": "ophthalmology",
      "urlSlug": "ophthalmology",
      "moduleNo": 5,
      "icon": "👁️",
      "label": "Ophtalmologie",
      "service": "ophthalmology-service",
      "kind": "overview",
      "route": "/module/ophthalmology",
      "servicePath": "module/ophthalmology",
      "scores": [
        "glaucome-cdr",
        "retinopathie-diabetique"
      ],
      "sigs": [
        {
          "endpoint": "glaucome-cdr",
          "fn": "glaucome_cdr",
          "params": [
            {
              "name": "ratio_c_d",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "pio_mmhg",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "retinopathie-diabetique",
          "fn": "retinopathie_diabetique",
          "params": [
            {
              "name": "microanévrismes",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "hémorragies_veineuses",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "exsudats_mous",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "hémorragies_intrarétiniennes",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "neovaisseaux",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "hemorragie_vitree",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "oedeme_maculaire",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "multiclass",
        "modalities": [
          "imaging_2d",
          "tabulaire"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "multiclass",
        "labelNom": "",
        "classes": [
          "rd_absente",
          "rd_non_proliferante",
          "rd_proliferante"
        ],
        "features": [
          {
            "name": "cd_ratio",
            "lo": 0.1,
            "hi": 0.95
          },
          {
            "name": "rnfl_um",
            "lo": 45.0,
            "hi": 120.0
          },
          {
            "name": "acuite_logmar",
            "lo": -0.1,
            "hi": 1.8
          },
          {
            "name": "hba1c_pct",
            "lo": 5.0,
            "hi": 12.0
          },
          {
            "name": "pio_mmhg",
            "lo": 8.0,
            "hi": 42.0
          }
        ]
      }
    },
    {
      "id": "ophthalmology:cas",
      "slug": "ophthalmology",
      "urlSlug": "ophthalmology",
      "moduleNo": 5,
      "icon": "👁️",
      "label": "Ophtalmologie",
      "service": "ophthalmology-service",
      "kind": "cas",
      "route": "/module/ophthalmology/cas",
      "servicePath": "module/ophthalmology",
      "scores": [
        "glaucome-cdr",
        "retinopathie-diabetique"
      ],
      "sigs": [
        {
          "endpoint": "glaucome-cdr",
          "fn": "glaucome_cdr",
          "params": [
            {
              "name": "ratio_c_d",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "pio_mmhg",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "retinopathie-diabetique",
          "fn": "retinopathie_diabetique",
          "params": [
            {
              "name": "microanévrismes",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "hémorragies_veineuses",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "exsudats_mous",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "hémorragies_intrarétiniennes",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "neovaisseaux",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "hemorragie_vitree",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "oedeme_maculaire",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "multiclass",
        "modalities": [
          "imaging_2d",
          "tabulaire"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "multiclass",
        "labelNom": "",
        "classes": [
          "rd_absente",
          "rd_non_proliferante",
          "rd_proliferante"
        ],
        "features": [
          {
            "name": "cd_ratio",
            "lo": 0.1,
            "hi": 0.95
          },
          {
            "name": "rnfl_um",
            "lo": 45.0,
            "hi": 120.0
          },
          {
            "name": "acuite_logmar",
            "lo": -0.1,
            "hi": 1.8
          },
          {
            "name": "hba1c_pct",
            "lo": 5.0,
            "hi": 12.0
          },
          {
            "name": "pio_mmhg",
            "lo": 8.0,
            "hi": 42.0
          }
        ]
      }
    },
    {
      "id": "ophthalmology:detail",
      "slug": "ophthalmology",
      "urlSlug": "ophthalmology",
      "moduleNo": 5,
      "icon": "👁️",
      "label": "Ophtalmologie",
      "service": "ophthalmology-service",
      "kind": "detail",
      "route": "/module/ophthalmology/cas/:caseId",
      "servicePath": "module/ophthalmology",
      "scores": [
        "glaucome-cdr",
        "retinopathie-diabetique"
      ],
      "sigs": [
        {
          "endpoint": "glaucome-cdr",
          "fn": "glaucome_cdr",
          "params": [
            {
              "name": "ratio_c_d",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "pio_mmhg",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "retinopathie-diabetique",
          "fn": "retinopathie_diabetique",
          "params": [
            {
              "name": "microanévrismes",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "hémorragies_veineuses",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "exsudats_mous",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "hémorragies_intrarétiniennes",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "neovaisseaux",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "hemorragie_vitree",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "oedeme_maculaire",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "multiclass",
        "modalities": [
          "imaging_2d",
          "tabulaire"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "multiclass",
        "labelNom": "",
        "classes": [
          "rd_absente",
          "rd_non_proliferante",
          "rd_proliferante"
        ],
        "features": [
          {
            "name": "cd_ratio",
            "lo": 0.1,
            "hi": 0.95
          },
          {
            "name": "rnfl_um",
            "lo": 45.0,
            "hi": 120.0
          },
          {
            "name": "acuite_logmar",
            "lo": -0.1,
            "hi": 1.8
          },
          {
            "name": "hba1c_pct",
            "lo": 5.0,
            "hi": 12.0
          },
          {
            "name": "pio_mmhg",
            "lo": 8.0,
            "hi": 42.0
          }
        ]
      }
    },
    {
      "id": "ophthalmology:ia",
      "slug": "ophthalmology",
      "urlSlug": "ophthalmology",
      "moduleNo": 5,
      "icon": "👁️",
      "label": "Ophtalmologie",
      "service": "ophthalmology-service",
      "kind": "ia",
      "route": "/module/ophthalmology/ia",
      "servicePath": "module/ophthalmology",
      "scores": [
        "glaucome-cdr",
        "retinopathie-diabetique"
      ],
      "sigs": [
        {
          "endpoint": "glaucome-cdr",
          "fn": "glaucome_cdr",
          "params": [
            {
              "name": "ratio_c_d",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "pio_mmhg",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "retinopathie-diabetique",
          "fn": "retinopathie_diabetique",
          "params": [
            {
              "name": "microanévrismes",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "hémorragies_veineuses",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "exsudats_mous",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "hémorragies_intrarétiniennes",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "neovaisseaux",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "hemorragie_vitree",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "oedeme_maculaire",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "multiclass",
        "modalities": [
          "imaging_2d",
          "tabulaire"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "multiclass",
        "labelNom": "",
        "classes": [
          "rd_absente",
          "rd_non_proliferante",
          "rd_proliferante"
        ],
        "features": [
          {
            "name": "cd_ratio",
            "lo": 0.1,
            "hi": 0.95
          },
          {
            "name": "rnfl_um",
            "lo": 45.0,
            "hi": 120.0
          },
          {
            "name": "acuite_logmar",
            "lo": -0.1,
            "hi": 1.8
          },
          {
            "name": "hba1c_pct",
            "lo": 5.0,
            "hi": 12.0
          },
          {
            "name": "pio_mmhg",
            "lo": 8.0,
            "hi": 42.0
          }
        ]
      }
    },
    {
      "id": "diabetes:overview",
      "slug": "diabetes",
      "urlSlug": "diabetes",
      "moduleNo": 6,
      "icon": "🩸",
      "label": "Diabétologie",
      "service": "diabetes-service",
      "kind": "overview",
      "route": "/module/diabetes",
      "servicePath": "module/diabetes",
      "scores": [
        "dfg-ckd-epi",
        "imc-oms"
      ],
      "sigs": [
        {
          "endpoint": "dfg-ckd-epi",
          "fn": "ckd_epi_2021",
          "params": [
            {
              "name": "age",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "sexe",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "creatinine_mgdl",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "imc-oms",
          "fn": "categorie_oms",
          "params": [
            {
              "name": "imc_value",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "regression",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "regression",
        "labelNom": "risque_complication",
        "classes": [],
        "features": [
          {
            "name": "hba1c_pct",
            "lo": 5.0,
            "hi": 14.0
          },
          {
            "name": "tir_pct",
            "lo": 20.0,
            "hi": 95.0
          },
          {
            "name": "age_dx",
            "lo": 10.0,
            "hi": 70.0
          },
          {
            "name": "imc",
            "lo": 16.0,
            "hi": 45.0
          },
          {
            "name": "fbg_g_l",
            "lo": 0.6,
            "hi": 4.0
          }
        ]
      }
    },
    {
      "id": "diabetes:cas",
      "slug": "diabetes",
      "urlSlug": "diabetes",
      "moduleNo": 6,
      "icon": "🩸",
      "label": "Diabétologie",
      "service": "diabetes-service",
      "kind": "cas",
      "route": "/module/diabetes/cas",
      "servicePath": "module/diabetes",
      "scores": [
        "dfg-ckd-epi",
        "imc-oms"
      ],
      "sigs": [
        {
          "endpoint": "dfg-ckd-epi",
          "fn": "ckd_epi_2021",
          "params": [
            {
              "name": "age",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "sexe",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "creatinine_mgdl",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "imc-oms",
          "fn": "categorie_oms",
          "params": [
            {
              "name": "imc_value",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "regression",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "regression",
        "labelNom": "risque_complication",
        "classes": [],
        "features": [
          {
            "name": "hba1c_pct",
            "lo": 5.0,
            "hi": 14.0
          },
          {
            "name": "tir_pct",
            "lo": 20.0,
            "hi": 95.0
          },
          {
            "name": "age_dx",
            "lo": 10.0,
            "hi": 70.0
          },
          {
            "name": "imc",
            "lo": 16.0,
            "hi": 45.0
          },
          {
            "name": "fbg_g_l",
            "lo": 0.6,
            "hi": 4.0
          }
        ]
      }
    },
    {
      "id": "diabetes:detail",
      "slug": "diabetes",
      "urlSlug": "diabetes",
      "moduleNo": 6,
      "icon": "🩸",
      "label": "Diabétologie",
      "service": "diabetes-service",
      "kind": "detail",
      "route": "/module/diabetes/cas/:caseId",
      "servicePath": "module/diabetes",
      "scores": [
        "dfg-ckd-epi",
        "imc-oms"
      ],
      "sigs": [
        {
          "endpoint": "dfg-ckd-epi",
          "fn": "ckd_epi_2021",
          "params": [
            {
              "name": "age",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "sexe",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "creatinine_mgdl",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "imc-oms",
          "fn": "categorie_oms",
          "params": [
            {
              "name": "imc_value",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "regression",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "regression",
        "labelNom": "risque_complication",
        "classes": [],
        "features": [
          {
            "name": "hba1c_pct",
            "lo": 5.0,
            "hi": 14.0
          },
          {
            "name": "tir_pct",
            "lo": 20.0,
            "hi": 95.0
          },
          {
            "name": "age_dx",
            "lo": 10.0,
            "hi": 70.0
          },
          {
            "name": "imc",
            "lo": 16.0,
            "hi": 45.0
          },
          {
            "name": "fbg_g_l",
            "lo": 0.6,
            "hi": 4.0
          }
        ]
      }
    },
    {
      "id": "diabetes:ia",
      "slug": "diabetes",
      "urlSlug": "diabetes",
      "moduleNo": 6,
      "icon": "🩸",
      "label": "Diabétologie",
      "service": "diabetes-service",
      "kind": "ia",
      "route": "/module/diabetes/ia",
      "servicePath": "module/diabetes",
      "scores": [
        "dfg-ckd-epi",
        "imc-oms"
      ],
      "sigs": [
        {
          "endpoint": "dfg-ckd-epi",
          "fn": "ckd_epi_2021",
          "params": [
            {
              "name": "age",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "sexe",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "creatinine_mgdl",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "imc-oms",
          "fn": "categorie_oms",
          "params": [
            {
              "name": "imc_value",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "regression",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "regression",
        "labelNom": "risque_complication",
        "classes": [],
        "features": [
          {
            "name": "hba1c_pct",
            "lo": 5.0,
            "hi": 14.0
          },
          {
            "name": "tir_pct",
            "lo": 20.0,
            "hi": 95.0
          },
          {
            "name": "age_dx",
            "lo": 10.0,
            "hi": 70.0
          },
          {
            "name": "imc",
            "lo": 16.0,
            "hi": 45.0
          },
          {
            "name": "fbg_g_l",
            "lo": 0.6,
            "hi": 4.0
          }
        ]
      }
    },
    {
      "id": "traumatology:overview",
      "slug": "traumatology",
      "urlSlug": "traumatology",
      "moduleNo": 7,
      "icon": "🦴",
      "label": "Traumatologie",
      "service": "traumatology-service",
      "kind": "overview",
      "route": "/module/traumatology",
      "servicePath": "module/traumatology",
      "scores": [
        "iss",
        "gcs"
      ],
      "sigs": [
        {
          "endpoint": "iss",
          "fn": "iss",
          "params": [
            {
              "name": "ais_regions",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "gcs",
          "fn": "gcs",
          "params": [
            {
              "name": "ouverture_yeux",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "reponse_verbale",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "reponse_motrice",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "multilabel",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "multilabel",
        "labelNom": "",
        "classes": [
          "fracture_ouverte",
          "atteinte_viscerale",
          "chirurgie_requise"
        ],
        "features": [
          {
            "name": "iss",
            "lo": 4.0,
            "hi": 50.0
          },
          {
            "name": "gcs",
            "lo": 3.0,
            "hi": 15.0
          },
          {
            "name": "age",
            "lo": 18.0,
            "hi": 95.0
          },
          {
            "name": "fractures_n",
            "lo": 1.0,
            "hi": 6.0
          },
          {
            "name": "cobb_deg",
            "lo": 5.0,
            "hi": 70.0
          }
        ]
      }
    },
    {
      "id": "traumatology:cas",
      "slug": "traumatology",
      "urlSlug": "traumatology",
      "moduleNo": 7,
      "icon": "🦴",
      "label": "Traumatologie",
      "service": "traumatology-service",
      "kind": "cas",
      "route": "/module/traumatology/cas",
      "servicePath": "module/traumatology",
      "scores": [
        "iss",
        "gcs"
      ],
      "sigs": [
        {
          "endpoint": "iss",
          "fn": "iss",
          "params": [
            {
              "name": "ais_regions",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "gcs",
          "fn": "gcs",
          "params": [
            {
              "name": "ouverture_yeux",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "reponse_verbale",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "reponse_motrice",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "multilabel",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "multilabel",
        "labelNom": "",
        "classes": [
          "fracture_ouverte",
          "atteinte_viscerale",
          "chirurgie_requise"
        ],
        "features": [
          {
            "name": "iss",
            "lo": 4.0,
            "hi": 50.0
          },
          {
            "name": "gcs",
            "lo": 3.0,
            "hi": 15.0
          },
          {
            "name": "age",
            "lo": 18.0,
            "hi": 95.0
          },
          {
            "name": "fractures_n",
            "lo": 1.0,
            "hi": 6.0
          },
          {
            "name": "cobb_deg",
            "lo": 5.0,
            "hi": 70.0
          }
        ]
      }
    },
    {
      "id": "traumatology:detail",
      "slug": "traumatology",
      "urlSlug": "traumatology",
      "moduleNo": 7,
      "icon": "🦴",
      "label": "Traumatologie",
      "service": "traumatology-service",
      "kind": "detail",
      "route": "/module/traumatology/cas/:caseId",
      "servicePath": "module/traumatology",
      "scores": [
        "iss",
        "gcs"
      ],
      "sigs": [
        {
          "endpoint": "iss",
          "fn": "iss",
          "params": [
            {
              "name": "ais_regions",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "gcs",
          "fn": "gcs",
          "params": [
            {
              "name": "ouverture_yeux",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "reponse_verbale",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "reponse_motrice",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "multilabel",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "multilabel",
        "labelNom": "",
        "classes": [
          "fracture_ouverte",
          "atteinte_viscerale",
          "chirurgie_requise"
        ],
        "features": [
          {
            "name": "iss",
            "lo": 4.0,
            "hi": 50.0
          },
          {
            "name": "gcs",
            "lo": 3.0,
            "hi": 15.0
          },
          {
            "name": "age",
            "lo": 18.0,
            "hi": 95.0
          },
          {
            "name": "fractures_n",
            "lo": 1.0,
            "hi": 6.0
          },
          {
            "name": "cobb_deg",
            "lo": 5.0,
            "hi": 70.0
          }
        ]
      }
    },
    {
      "id": "traumatology:ia",
      "slug": "traumatology",
      "urlSlug": "traumatology",
      "moduleNo": 7,
      "icon": "🦴",
      "label": "Traumatologie",
      "service": "traumatology-service",
      "kind": "ia",
      "route": "/module/traumatology/ia",
      "servicePath": "module/traumatology",
      "scores": [
        "iss",
        "gcs"
      ],
      "sigs": [
        {
          "endpoint": "iss",
          "fn": "iss",
          "params": [
            {
              "name": "ais_regions",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "gcs",
          "fn": "gcs",
          "params": [
            {
              "name": "ouverture_yeux",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "reponse_verbale",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "reponse_motrice",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "multilabel",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "multilabel",
        "labelNom": "",
        "classes": [
          "fracture_ouverte",
          "atteinte_viscerale",
          "chirurgie_requise"
        ],
        "features": [
          {
            "name": "iss",
            "lo": 4.0,
            "hi": 50.0
          },
          {
            "name": "gcs",
            "lo": 3.0,
            "hi": 15.0
          },
          {
            "name": "age",
            "lo": 18.0,
            "hi": 95.0
          },
          {
            "name": "fractures_n",
            "lo": 1.0,
            "hi": 6.0
          },
          {
            "name": "cobb_deg",
            "lo": 5.0,
            "hi": 70.0
          }
        ]
      }
    },
    {
      "id": "cardiology:overview",
      "slug": "cardiology",
      "urlSlug": "cardiology",
      "moduleNo": 8,
      "icon": "❤️",
      "label": "Cardiologie",
      "service": "cardiology-service",
      "kind": "overview",
      "route": "/module/cardiology",
      "servicePath": "module/cardiology",
      "scores": [
        "chads2ds2vasc",
        "heart-score",
        "nyha",
        "framingham"
      ],
      "sigs": [
        {
          "endpoint": "chads2ds2vasc",
          "fn": "chads2ds2vasc",
          "params": [
            {
              "name": "insuffisance_cardiaque",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "hta",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "diabete",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "avc_ou_atcd_thrombose",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "maladie_vasculaire",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "age",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "sexe_feminin",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "heart-score",
          "fn": "heart_score",
          "params": [
            {
              "name": "anamnese",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "ecg",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "age",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "facteurs_risque",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "troponine",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "nyha",
          "fn": "nyha",
          "params": [
            {
              "name": "classe_tolerances",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "framingham",
          "fn": "framingham_10y",
          "params": [
            {
              "name": "age",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "cholesterol_mgdl",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "hdl_mgdl",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "pas",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "hta_traitee",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "fumeur",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "diabete",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "sexe",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "multiclass",
        "modalities": [
          "signal_1d",
          "tabulaire",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "multiclass",
        "labelNom": "",
        "classes": [
          "stable",
          "angor_instable",
          "sca"
        ],
        "features": [
          {
            "name": "fevg_pct",
            "lo": 15.0,
            "hi": 70.0
          },
          {
            "name": "troponine_ng_ml",
            "lo": 0.01,
            "hi": 10.0
          },
          {
            "name": "bpm",
            "lo": 40.0,
            "hi": 180.0
          },
          {
            "name": "qt_ms",
            "lo": 320.0,
            "hi": 560.0
          },
          {
            "name": "cha2ds2_vasc",
            "lo": 0.0,
            "hi": 9.0
          }
        ]
      }
    },
    {
      "id": "cardiology:cas",
      "slug": "cardiology",
      "urlSlug": "cardiology",
      "moduleNo": 8,
      "icon": "❤️",
      "label": "Cardiologie",
      "service": "cardiology-service",
      "kind": "cas",
      "route": "/module/cardiology/cas",
      "servicePath": "module/cardiology",
      "scores": [
        "chads2ds2vasc",
        "heart-score",
        "nyha",
        "framingham"
      ],
      "sigs": [
        {
          "endpoint": "chads2ds2vasc",
          "fn": "chads2ds2vasc",
          "params": [
            {
              "name": "insuffisance_cardiaque",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "hta",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "diabete",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "avc_ou_atcd_thrombose",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "maladie_vasculaire",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "age",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "sexe_feminin",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "heart-score",
          "fn": "heart_score",
          "params": [
            {
              "name": "anamnese",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "ecg",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "age",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "facteurs_risque",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "troponine",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "nyha",
          "fn": "nyha",
          "params": [
            {
              "name": "classe_tolerances",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "framingham",
          "fn": "framingham_10y",
          "params": [
            {
              "name": "age",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "cholesterol_mgdl",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "hdl_mgdl",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "pas",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "hta_traitee",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "fumeur",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "diabete",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "sexe",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "multiclass",
        "modalities": [
          "signal_1d",
          "tabulaire",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "multiclass",
        "labelNom": "",
        "classes": [
          "stable",
          "angor_instable",
          "sca"
        ],
        "features": [
          {
            "name": "fevg_pct",
            "lo": 15.0,
            "hi": 70.0
          },
          {
            "name": "troponine_ng_ml",
            "lo": 0.01,
            "hi": 10.0
          },
          {
            "name": "bpm",
            "lo": 40.0,
            "hi": 180.0
          },
          {
            "name": "qt_ms",
            "lo": 320.0,
            "hi": 560.0
          },
          {
            "name": "cha2ds2_vasc",
            "lo": 0.0,
            "hi": 9.0
          }
        ]
      }
    },
    {
      "id": "cardiology:detail",
      "slug": "cardiology",
      "urlSlug": "cardiology",
      "moduleNo": 8,
      "icon": "❤️",
      "label": "Cardiologie",
      "service": "cardiology-service",
      "kind": "detail",
      "route": "/module/cardiology/cas/:caseId",
      "servicePath": "module/cardiology",
      "scores": [
        "chads2ds2vasc",
        "heart-score",
        "nyha",
        "framingham"
      ],
      "sigs": [
        {
          "endpoint": "chads2ds2vasc",
          "fn": "chads2ds2vasc",
          "params": [
            {
              "name": "insuffisance_cardiaque",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "hta",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "diabete",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "avc_ou_atcd_thrombose",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "maladie_vasculaire",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "age",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "sexe_feminin",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "heart-score",
          "fn": "heart_score",
          "params": [
            {
              "name": "anamnese",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "ecg",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "age",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "facteurs_risque",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "troponine",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "nyha",
          "fn": "nyha",
          "params": [
            {
              "name": "classe_tolerances",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "framingham",
          "fn": "framingham_10y",
          "params": [
            {
              "name": "age",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "cholesterol_mgdl",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "hdl_mgdl",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "pas",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "hta_traitee",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "fumeur",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "diabete",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "sexe",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "multiclass",
        "modalities": [
          "signal_1d",
          "tabulaire",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "multiclass",
        "labelNom": "",
        "classes": [
          "stable",
          "angor_instable",
          "sca"
        ],
        "features": [
          {
            "name": "fevg_pct",
            "lo": 15.0,
            "hi": 70.0
          },
          {
            "name": "troponine_ng_ml",
            "lo": 0.01,
            "hi": 10.0
          },
          {
            "name": "bpm",
            "lo": 40.0,
            "hi": 180.0
          },
          {
            "name": "qt_ms",
            "lo": 320.0,
            "hi": 560.0
          },
          {
            "name": "cha2ds2_vasc",
            "lo": 0.0,
            "hi": 9.0
          }
        ]
      }
    },
    {
      "id": "cardiology:ia",
      "slug": "cardiology",
      "urlSlug": "cardiology",
      "moduleNo": 8,
      "icon": "❤️",
      "label": "Cardiologie",
      "service": "cardiology-service",
      "kind": "ia",
      "route": "/module/cardiology/ia",
      "servicePath": "module/cardiology",
      "scores": [
        "chads2ds2vasc",
        "heart-score",
        "nyha",
        "framingham"
      ],
      "sigs": [
        {
          "endpoint": "chads2ds2vasc",
          "fn": "chads2ds2vasc",
          "params": [
            {
              "name": "insuffisance_cardiaque",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "hta",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "diabete",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "avc_ou_atcd_thrombose",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "maladie_vasculaire",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "age",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "sexe_feminin",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "heart-score",
          "fn": "heart_score",
          "params": [
            {
              "name": "anamnese",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "ecg",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "age",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "facteurs_risque",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "troponine",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "nyha",
          "fn": "nyha",
          "params": [
            {
              "name": "classe_tolerances",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "framingham",
          "fn": "framingham_10y",
          "params": [
            {
              "name": "age",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "cholesterol_mgdl",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "hdl_mgdl",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "pas",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "hta_traitee",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "fumeur",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "diabete",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "sexe",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "multiclass",
        "modalities": [
          "signal_1d",
          "tabulaire",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "multiclass",
        "labelNom": "",
        "classes": [
          "stable",
          "angor_instable",
          "sca"
        ],
        "features": [
          {
            "name": "fevg_pct",
            "lo": 15.0,
            "hi": 70.0
          },
          {
            "name": "troponine_ng_ml",
            "lo": 0.01,
            "hi": 10.0
          },
          {
            "name": "bpm",
            "lo": 40.0,
            "hi": 180.0
          },
          {
            "name": "qt_ms",
            "lo": 320.0,
            "hi": 560.0
          },
          {
            "name": "cha2ds2_vasc",
            "lo": 0.0,
            "hi": 9.0
          }
        ]
      }
    },
    {
      "id": "pneumology:overview",
      "slug": "pneumology",
      "urlSlug": "pneumology",
      "moduleNo": 9,
      "icon": "🫁",
      "label": "Pneumologie",
      "service": "pneumology-service",
      "kind": "overview",
      "route": "/module/pneumology",
      "servicePath": "module/pneumology",
      "scores": [
        "gold",
        "stop-bang",
        "tb-oms",
        "spirometrie"
      ],
      "sigs": [
        {
          "endpoint": "gold",
          "fn": "gold_group",
          "params": [
            {
              "name": "mmc_pct",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "dyspnee_mrc",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "exacerbations_12m",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "hospitalisation_exacerbation",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "stop-bang",
          "fn": "stop_bang",
          "params": [
            {
              "name": "snorring",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "fatigue",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "apnee_obseree",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "pression_arterielle_haute",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "imc_over_35",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "age_over_50",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "tour_cou_over_40cm",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "sexe_masculin",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "tb-oms",
          "fn": "tb_who_screen",
          "params": [
            {
              "name": "toux_2sem_plus",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "fievre",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "sueurs_nocturnes",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "perte_poids",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "contact_tb",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "vih_positif",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "spirometrie",
          "fn": "spirometry_interpretation",
          "params": [
            {
              "name": "fev1_l",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "fvc_l",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "fev1_theo_pct",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "multilabel",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "multilabel",
        "labelNom": "",
        "classes": [
          "tb_active",
          "bpco",
          "embolie"
        ],
        "features": [
          {
            "name": "spo2_pct",
            "lo": 70.0,
            "hi": 100.0
          },
          {
            "name": "fev1_pct",
            "lo": 25.0,
            "hi": 110.0
          },
          {
            "name": "wells",
            "lo": 0.0,
            "hi": 12.0
          },
          {
            "name": "crp_mg_l",
            "lo": 1.0,
            "hi": 300.0
          },
          {
            "name": "paquets_annees",
            "lo": 0.0,
            "hi": 80.0
          }
        ]
      }
    },
    {
      "id": "pneumology:cas",
      "slug": "pneumology",
      "urlSlug": "pneumology",
      "moduleNo": 9,
      "icon": "🫁",
      "label": "Pneumologie",
      "service": "pneumology-service",
      "kind": "cas",
      "route": "/module/pneumology/cas",
      "servicePath": "module/pneumology",
      "scores": [
        "gold",
        "stop-bang",
        "tb-oms",
        "spirometrie"
      ],
      "sigs": [
        {
          "endpoint": "gold",
          "fn": "gold_group",
          "params": [
            {
              "name": "mmc_pct",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "dyspnee_mrc",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "exacerbations_12m",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "hospitalisation_exacerbation",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "stop-bang",
          "fn": "stop_bang",
          "params": [
            {
              "name": "snorring",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "fatigue",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "apnee_obseree",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "pression_arterielle_haute",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "imc_over_35",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "age_over_50",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "tour_cou_over_40cm",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "sexe_masculin",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "tb-oms",
          "fn": "tb_who_screen",
          "params": [
            {
              "name": "toux_2sem_plus",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "fievre",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "sueurs_nocturnes",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "perte_poids",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "contact_tb",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "vih_positif",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "spirometrie",
          "fn": "spirometry_interpretation",
          "params": [
            {
              "name": "fev1_l",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "fvc_l",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "fev1_theo_pct",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "multilabel",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "multilabel",
        "labelNom": "",
        "classes": [
          "tb_active",
          "bpco",
          "embolie"
        ],
        "features": [
          {
            "name": "spo2_pct",
            "lo": 70.0,
            "hi": 100.0
          },
          {
            "name": "fev1_pct",
            "lo": 25.0,
            "hi": 110.0
          },
          {
            "name": "wells",
            "lo": 0.0,
            "hi": 12.0
          },
          {
            "name": "crp_mg_l",
            "lo": 1.0,
            "hi": 300.0
          },
          {
            "name": "paquets_annees",
            "lo": 0.0,
            "hi": 80.0
          }
        ]
      }
    },
    {
      "id": "pneumology:detail",
      "slug": "pneumology",
      "urlSlug": "pneumology",
      "moduleNo": 9,
      "icon": "🫁",
      "label": "Pneumologie",
      "service": "pneumology-service",
      "kind": "detail",
      "route": "/module/pneumology/cas/:caseId",
      "servicePath": "module/pneumology",
      "scores": [
        "gold",
        "stop-bang",
        "tb-oms",
        "spirometrie"
      ],
      "sigs": [
        {
          "endpoint": "gold",
          "fn": "gold_group",
          "params": [
            {
              "name": "mmc_pct",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "dyspnee_mrc",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "exacerbations_12m",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "hospitalisation_exacerbation",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "stop-bang",
          "fn": "stop_bang",
          "params": [
            {
              "name": "snorring",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "fatigue",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "apnee_obseree",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "pression_arterielle_haute",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "imc_over_35",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "age_over_50",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "tour_cou_over_40cm",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "sexe_masculin",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "tb-oms",
          "fn": "tb_who_screen",
          "params": [
            {
              "name": "toux_2sem_plus",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "fievre",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "sueurs_nocturnes",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "perte_poids",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "contact_tb",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "vih_positif",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "spirometrie",
          "fn": "spirometry_interpretation",
          "params": [
            {
              "name": "fev1_l",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "fvc_l",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "fev1_theo_pct",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "multilabel",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "multilabel",
        "labelNom": "",
        "classes": [
          "tb_active",
          "bpco",
          "embolie"
        ],
        "features": [
          {
            "name": "spo2_pct",
            "lo": 70.0,
            "hi": 100.0
          },
          {
            "name": "fev1_pct",
            "lo": 25.0,
            "hi": 110.0
          },
          {
            "name": "wells",
            "lo": 0.0,
            "hi": 12.0
          },
          {
            "name": "crp_mg_l",
            "lo": 1.0,
            "hi": 300.0
          },
          {
            "name": "paquets_annees",
            "lo": 0.0,
            "hi": 80.0
          }
        ]
      }
    },
    {
      "id": "pneumology:ia",
      "slug": "pneumology",
      "urlSlug": "pneumology",
      "moduleNo": 9,
      "icon": "🫁",
      "label": "Pneumologie",
      "service": "pneumology-service",
      "kind": "ia",
      "route": "/module/pneumology/ia",
      "servicePath": "module/pneumology",
      "scores": [
        "gold",
        "stop-bang",
        "tb-oms",
        "spirometrie"
      ],
      "sigs": [
        {
          "endpoint": "gold",
          "fn": "gold_group",
          "params": [
            {
              "name": "mmc_pct",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "dyspnee_mrc",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "exacerbations_12m",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "hospitalisation_exacerbation",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "stop-bang",
          "fn": "stop_bang",
          "params": [
            {
              "name": "snorring",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "fatigue",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "apnee_obseree",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "pression_arterielle_haute",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "imc_over_35",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "age_over_50",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "tour_cou_over_40cm",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "sexe_masculin",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "tb-oms",
          "fn": "tb_who_screen",
          "params": [
            {
              "name": "toux_2sem_plus",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "fievre",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "sueurs_nocturnes",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "perte_poids",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "contact_tb",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "vih_positif",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "spirometrie",
          "fn": "spirometry_interpretation",
          "params": [
            {
              "name": "fev1_l",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "fvc_l",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "fev1_theo_pct",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "multilabel",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "multilabel",
        "labelNom": "",
        "classes": [
          "tb_active",
          "bpco",
          "embolie"
        ],
        "features": [
          {
            "name": "spo2_pct",
            "lo": 70.0,
            "hi": 100.0
          },
          {
            "name": "fev1_pct",
            "lo": 25.0,
            "hi": 110.0
          },
          {
            "name": "wells",
            "lo": 0.0,
            "hi": 12.0
          },
          {
            "name": "crp_mg_l",
            "lo": 1.0,
            "hi": 300.0
          },
          {
            "name": "paquets_annees",
            "lo": 0.0,
            "hi": 80.0
          }
        ]
      }
    },
    {
      "id": "obstetrics:overview",
      "slug": "obstetrics",
      "urlSlug": "obstetrics",
      "moduleNo": 10,
      "icon": "🤰",
      "label": "Obstétrique",
      "service": "obstetrics-service",
      "kind": "overview",
      "route": "/module/obstetrics",
      "servicePath": "module/obstetrics",
      "scores": [
        "bishop"
      ],
      "sigs": [
        {
          "endpoint": "bishop",
          "fn": "bishop",
          "params": [
            {
              "name": "dilatation_cm",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "effacement_pct",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "station",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "consistance",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "position",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "binary",
        "modalities": [
          "waveform",
          "imaging_2d",
          "tabulaire"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "classification",
        "labelNom": "pre_eclampsie",
        "classes": [],
        "features": [
          {
            "name": "tas_mmhg",
            "lo": 80.0,
            "hi": 180.0
          },
          {
            "name": "proteinurie_g_j",
            "lo": 0.0,
            "hi": 5.0
          },
          {
            "name": "clarte_nucale_mm",
            "lo": 0.8,
            "hi": 6.0
          },
          {
            "name": "bishop",
            "lo": 0.0,
            "hi": 13.0
          },
          {
            "name": "age_gestation_sem",
            "lo": 24.0,
            "hi": 42.0
          }
        ]
      }
    },
    {
      "id": "obstetrics:cas",
      "slug": "obstetrics",
      "urlSlug": "obstetrics",
      "moduleNo": 10,
      "icon": "🤰",
      "label": "Obstétrique",
      "service": "obstetrics-service",
      "kind": "cas",
      "route": "/module/obstetrics/cas",
      "servicePath": "module/obstetrics",
      "scores": [
        "bishop"
      ],
      "sigs": [
        {
          "endpoint": "bishop",
          "fn": "bishop",
          "params": [
            {
              "name": "dilatation_cm",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "effacement_pct",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "station",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "consistance",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "position",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "binary",
        "modalities": [
          "waveform",
          "imaging_2d",
          "tabulaire"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "classification",
        "labelNom": "pre_eclampsie",
        "classes": [],
        "features": [
          {
            "name": "tas_mmhg",
            "lo": 80.0,
            "hi": 180.0
          },
          {
            "name": "proteinurie_g_j",
            "lo": 0.0,
            "hi": 5.0
          },
          {
            "name": "clarte_nucale_mm",
            "lo": 0.8,
            "hi": 6.0
          },
          {
            "name": "bishop",
            "lo": 0.0,
            "hi": 13.0
          },
          {
            "name": "age_gestation_sem",
            "lo": 24.0,
            "hi": 42.0
          }
        ]
      }
    },
    {
      "id": "obstetrics:detail",
      "slug": "obstetrics",
      "urlSlug": "obstetrics",
      "moduleNo": 10,
      "icon": "🤰",
      "label": "Obstétrique",
      "service": "obstetrics-service",
      "kind": "detail",
      "route": "/module/obstetrics/cas/:caseId",
      "servicePath": "module/obstetrics",
      "scores": [
        "bishop"
      ],
      "sigs": [
        {
          "endpoint": "bishop",
          "fn": "bishop",
          "params": [
            {
              "name": "dilatation_cm",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "effacement_pct",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "station",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "consistance",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "position",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "binary",
        "modalities": [
          "waveform",
          "imaging_2d",
          "tabulaire"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "classification",
        "labelNom": "pre_eclampsie",
        "classes": [],
        "features": [
          {
            "name": "tas_mmhg",
            "lo": 80.0,
            "hi": 180.0
          },
          {
            "name": "proteinurie_g_j",
            "lo": 0.0,
            "hi": 5.0
          },
          {
            "name": "clarte_nucale_mm",
            "lo": 0.8,
            "hi": 6.0
          },
          {
            "name": "bishop",
            "lo": 0.0,
            "hi": 13.0
          },
          {
            "name": "age_gestation_sem",
            "lo": 24.0,
            "hi": 42.0
          }
        ]
      }
    },
    {
      "id": "obstetrics:ia",
      "slug": "obstetrics",
      "urlSlug": "obstetrics",
      "moduleNo": 10,
      "icon": "🤰",
      "label": "Obstétrique",
      "service": "obstetrics-service",
      "kind": "ia",
      "route": "/module/obstetrics/ia",
      "servicePath": "module/obstetrics",
      "scores": [
        "bishop"
      ],
      "sigs": [
        {
          "endpoint": "bishop",
          "fn": "bishop",
          "params": [
            {
              "name": "dilatation_cm",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "effacement_pct",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "station",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "consistance",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "position",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "binary",
        "modalities": [
          "waveform",
          "imaging_2d",
          "tabulaire"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "classification",
        "labelNom": "pre_eclampsie",
        "classes": [],
        "features": [
          {
            "name": "tas_mmhg",
            "lo": 80.0,
            "hi": 180.0
          },
          {
            "name": "proteinurie_g_j",
            "lo": 0.0,
            "hi": 5.0
          },
          {
            "name": "clarte_nucale_mm",
            "lo": 0.8,
            "hi": 6.0
          },
          {
            "name": "bishop",
            "lo": 0.0,
            "hi": 13.0
          },
          {
            "name": "age_gestation_sem",
            "lo": 24.0,
            "hi": 42.0
          }
        ]
      }
    },
    {
      "id": "gynecology:overview",
      "slug": "gynecology",
      "urlSlug": "gynecology",
      "moduleNo": 11,
      "icon": "🌸",
      "label": "Gynécologie",
      "service": "gynecology-service",
      "kind": "overview",
      "route": "/module/gynecology",
      "servicePath": "module/gynecology",
      "scores": [
        "iota",
        "rotterdam",
        "orads"
      ],
      "sigs": [
        {
          "endpoint": "iota",
          "fn": "iota_simple_rules",
          "params": [
            {
              "name": "M_regles",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "B_regles",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "rotterdam",
          "fn": "rotterdam_pcos",
          "params": [
            {
              "name": "oligo_anovulation",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "hyperandrogenie_clinique",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "hyperandrogenie_bio",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "follicules_2_9mm_par_ovaire",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "volume_ovarien_ml",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "orads",
          "fn": "orads_us",
          "params": [
            {
              "name": "leison_score",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "binary",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "classification",
        "labelNom": "malignite_suspectee",
        "classes": [],
        "features": [
          {
            "name": "pap_bethesda",
            "lo": 0.0,
            "hi": 5.0
          },
          {
            "name": "hpv_vl_log",
            "lo": 0.0,
            "hi": 9.0
          },
          {
            "name": "iota_score",
            "lo": 0.0,
            "hi": 10.0
          },
          {
            "name": "orads",
            "lo": 1.0,
            "hi": 5.0
          },
          {
            "name": "saignement_j",
            "lo": 0.0,
            "hi": 30.0
          }
        ]
      }
    },
    {
      "id": "gynecology:cas",
      "slug": "gynecology",
      "urlSlug": "gynecology",
      "moduleNo": 11,
      "icon": "🌸",
      "label": "Gynécologie",
      "service": "gynecology-service",
      "kind": "cas",
      "route": "/module/gynecology/cas",
      "servicePath": "module/gynecology",
      "scores": [
        "iota",
        "rotterdam",
        "orads"
      ],
      "sigs": [
        {
          "endpoint": "iota",
          "fn": "iota_simple_rules",
          "params": [
            {
              "name": "M_regles",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "B_regles",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "rotterdam",
          "fn": "rotterdam_pcos",
          "params": [
            {
              "name": "oligo_anovulation",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "hyperandrogenie_clinique",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "hyperandrogenie_bio",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "follicules_2_9mm_par_ovaire",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "volume_ovarien_ml",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "orads",
          "fn": "orads_us",
          "params": [
            {
              "name": "leison_score",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "binary",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "classification",
        "labelNom": "malignite_suspectee",
        "classes": [],
        "features": [
          {
            "name": "pap_bethesda",
            "lo": 0.0,
            "hi": 5.0
          },
          {
            "name": "hpv_vl_log",
            "lo": 0.0,
            "hi": 9.0
          },
          {
            "name": "iota_score",
            "lo": 0.0,
            "hi": 10.0
          },
          {
            "name": "orads",
            "lo": 1.0,
            "hi": 5.0
          },
          {
            "name": "saignement_j",
            "lo": 0.0,
            "hi": 30.0
          }
        ]
      }
    },
    {
      "id": "gynecology:detail",
      "slug": "gynecology",
      "urlSlug": "gynecology",
      "moduleNo": 11,
      "icon": "🌸",
      "label": "Gynécologie",
      "service": "gynecology-service",
      "kind": "detail",
      "route": "/module/gynecology/cas/:caseId",
      "servicePath": "module/gynecology",
      "scores": [
        "iota",
        "rotterdam",
        "orads"
      ],
      "sigs": [
        {
          "endpoint": "iota",
          "fn": "iota_simple_rules",
          "params": [
            {
              "name": "M_regles",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "B_regles",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "rotterdam",
          "fn": "rotterdam_pcos",
          "params": [
            {
              "name": "oligo_anovulation",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "hyperandrogenie_clinique",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "hyperandrogenie_bio",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "follicules_2_9mm_par_ovaire",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "volume_ovarien_ml",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "orads",
          "fn": "orads_us",
          "params": [
            {
              "name": "leison_score",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "binary",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "classification",
        "labelNom": "malignite_suspectee",
        "classes": [],
        "features": [
          {
            "name": "pap_bethesda",
            "lo": 0.0,
            "hi": 5.0
          },
          {
            "name": "hpv_vl_log",
            "lo": 0.0,
            "hi": 9.0
          },
          {
            "name": "iota_score",
            "lo": 0.0,
            "hi": 10.0
          },
          {
            "name": "orads",
            "lo": 1.0,
            "hi": 5.0
          },
          {
            "name": "saignement_j",
            "lo": 0.0,
            "hi": 30.0
          }
        ]
      }
    },
    {
      "id": "gynecology:ia",
      "slug": "gynecology",
      "urlSlug": "gynecology",
      "moduleNo": 11,
      "icon": "🌸",
      "label": "Gynécologie",
      "service": "gynecology-service",
      "kind": "ia",
      "route": "/module/gynecology/ia",
      "servicePath": "module/gynecology",
      "scores": [
        "iota",
        "rotterdam",
        "orads"
      ],
      "sigs": [
        {
          "endpoint": "iota",
          "fn": "iota_simple_rules",
          "params": [
            {
              "name": "M_regles",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "B_regles",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "rotterdam",
          "fn": "rotterdam_pcos",
          "params": [
            {
              "name": "oligo_anovulation",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "hyperandrogenie_clinique",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "hyperandrogenie_bio",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "follicules_2_9mm_par_ovaire",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "volume_ovarien_ml",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "orads",
          "fn": "orads_us",
          "params": [
            {
              "name": "leison_score",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "binary",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "classification",
        "labelNom": "malignite_suspectee",
        "classes": [],
        "features": [
          {
            "name": "pap_bethesda",
            "lo": 0.0,
            "hi": 5.0
          },
          {
            "name": "hpv_vl_log",
            "lo": 0.0,
            "hi": 9.0
          },
          {
            "name": "iota_score",
            "lo": 0.0,
            "hi": 10.0
          },
          {
            "name": "orads",
            "lo": 1.0,
            "hi": 5.0
          },
          {
            "name": "saignement_j",
            "lo": 0.0,
            "hi": 30.0
          }
        ]
      }
    },
    {
      "id": "fertility:overview",
      "slug": "fertility",
      "urlSlug": "fertility",
      "moduleNo": 12,
      "icon": "🧬",
      "label": "Fertilité",
      "service": "fertility-service",
      "kind": "overview",
      "route": "/module/fertility",
      "servicePath": "module/fertility",
      "scores": [
        "roma"
      ],
      "sigs": [
        {
          "endpoint": "roma",
          "fn": "roma_score",
          "params": [
            {
              "name": "ca125",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "he4",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "menopausee",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "regression",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "regression",
        "labelNom": "proba_conception",
        "classes": [],
        "features": [
          {
            "name": "amh_ng_ml",
            "lo": 0.1,
            "hi": 8.0
          },
          {
            "name": "cfa_n",
            "lo": 1.0,
            "hi": 30.0
          },
          {
            "name": "spermato_millions",
            "lo": 0.0,
            "hi": 120.0
          },
          {
            "name": "fsh_ui_l",
            "lo": 2.0,
            "hi": 25.0
          },
          {
            "name": "age_femme",
            "lo": 20.0,
            "hi": 42.0
          }
        ]
      }
    },
    {
      "id": "fertility:cas",
      "slug": "fertility",
      "urlSlug": "fertility",
      "moduleNo": 12,
      "icon": "🧬",
      "label": "Fertilité",
      "service": "fertility-service",
      "kind": "cas",
      "route": "/module/fertility/cas",
      "servicePath": "module/fertility",
      "scores": [
        "roma"
      ],
      "sigs": [
        {
          "endpoint": "roma",
          "fn": "roma_score",
          "params": [
            {
              "name": "ca125",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "he4",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "menopausee",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "regression",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "regression",
        "labelNom": "proba_conception",
        "classes": [],
        "features": [
          {
            "name": "amh_ng_ml",
            "lo": 0.1,
            "hi": 8.0
          },
          {
            "name": "cfa_n",
            "lo": 1.0,
            "hi": 30.0
          },
          {
            "name": "spermato_millions",
            "lo": 0.0,
            "hi": 120.0
          },
          {
            "name": "fsh_ui_l",
            "lo": 2.0,
            "hi": 25.0
          },
          {
            "name": "age_femme",
            "lo": 20.0,
            "hi": 42.0
          }
        ]
      }
    },
    {
      "id": "fertility:detail",
      "slug": "fertility",
      "urlSlug": "fertility",
      "moduleNo": 12,
      "icon": "🧬",
      "label": "Fertilité",
      "service": "fertility-service",
      "kind": "detail",
      "route": "/module/fertility/cas/:caseId",
      "servicePath": "module/fertility",
      "scores": [
        "roma"
      ],
      "sigs": [
        {
          "endpoint": "roma",
          "fn": "roma_score",
          "params": [
            {
              "name": "ca125",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "he4",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "menopausee",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "regression",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "regression",
        "labelNom": "proba_conception",
        "classes": [],
        "features": [
          {
            "name": "amh_ng_ml",
            "lo": 0.1,
            "hi": 8.0
          },
          {
            "name": "cfa_n",
            "lo": 1.0,
            "hi": 30.0
          },
          {
            "name": "spermato_millions",
            "lo": 0.0,
            "hi": 120.0
          },
          {
            "name": "fsh_ui_l",
            "lo": 2.0,
            "hi": 25.0
          },
          {
            "name": "age_femme",
            "lo": 20.0,
            "hi": 42.0
          }
        ]
      }
    },
    {
      "id": "fertility:ia",
      "slug": "fertility",
      "urlSlug": "fertility",
      "moduleNo": 12,
      "icon": "🧬",
      "label": "Fertilité",
      "service": "fertility-service",
      "kind": "ia",
      "route": "/module/fertility/ia",
      "servicePath": "module/fertility",
      "scores": [
        "roma"
      ],
      "sigs": [
        {
          "endpoint": "roma",
          "fn": "roma_score",
          "params": [
            {
              "name": "ca125",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "he4",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "menopausee",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "regression",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "regression",
        "labelNom": "proba_conception",
        "classes": [],
        "features": [
          {
            "name": "amh_ng_ml",
            "lo": 0.1,
            "hi": 8.0
          },
          {
            "name": "cfa_n",
            "lo": 1.0,
            "hi": 30.0
          },
          {
            "name": "spermato_millions",
            "lo": 0.0,
            "hi": 120.0
          },
          {
            "name": "fsh_ui_l",
            "lo": 2.0,
            "hi": 25.0
          },
          {
            "name": "age_femme",
            "lo": 20.0,
            "hi": 42.0
          }
        ]
      }
    },
    {
      "id": "neurology:overview",
      "slug": "neurology",
      "urlSlug": "neurology",
      "moduleNo": 13,
      "icon": "🧠",
      "label": "Neurologie",
      "service": "neurology-service",
      "kind": "overview",
      "route": "/module/neurology",
      "servicePath": "module/neurology",
      "scores": [
        "aspects",
        "nihss",
        "mmse",
        "mcdonald"
      ],
      "sigs": [
        {
          "endpoint": "aspects",
          "fn": "aspects",
          "params": [
            {
              "name": "scores_regions",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "nihss",
          "fn": "nihss",
          "params": [
            {
              "name": "items",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "mmse",
          "fn": "mmse",
          "params": [
            {
              "name": "items",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "mcdonald",
          "fn": "mcdonald_ms",
          "params": [
            {
              "name": "dissemination_espace",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "dissemination_temps",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "bande_oligoclonales",
              "kind": "text",
              "hasDefault": true
            }
          ]
        }
      ],
      "ai": {
        "task": "binary",
        "modalities": [
          "imaging_3d",
          "tabulaire",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "classification",
        "labelNom": "avc_ischemique",
        "classes": [],
        "features": [
          {
            "name": "nihss",
            "lo": 0.0,
            "hi": 30.0
          },
          {
            "name": "aspects",
            "lo": 0.0,
            "hi": 10.0
          },
          {
            "name": "mmse",
            "lo": 0.0,
            "hi": 30.0
          },
          {
            "name": "age",
            "lo": 40.0,
            "hi": 95.0
          },
          {
            "name": "delai_onset_h",
            "lo": 0.5,
            "hi": 24.0
          }
        ]
      }
    },
    {
      "id": "neurology:cas",
      "slug": "neurology",
      "urlSlug": "neurology",
      "moduleNo": 13,
      "icon": "🧠",
      "label": "Neurologie",
      "service": "neurology-service",
      "kind": "cas",
      "route": "/module/neurology/cas",
      "servicePath": "module/neurology",
      "scores": [
        "aspects",
        "nihss",
        "mmse",
        "mcdonald"
      ],
      "sigs": [
        {
          "endpoint": "aspects",
          "fn": "aspects",
          "params": [
            {
              "name": "scores_regions",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "nihss",
          "fn": "nihss",
          "params": [
            {
              "name": "items",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "mmse",
          "fn": "mmse",
          "params": [
            {
              "name": "items",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "mcdonald",
          "fn": "mcdonald_ms",
          "params": [
            {
              "name": "dissemination_espace",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "dissemination_temps",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "bande_oligoclonales",
              "kind": "text",
              "hasDefault": true
            }
          ]
        }
      ],
      "ai": {
        "task": "binary",
        "modalities": [
          "imaging_3d",
          "tabulaire",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "classification",
        "labelNom": "avc_ischemique",
        "classes": [],
        "features": [
          {
            "name": "nihss",
            "lo": 0.0,
            "hi": 30.0
          },
          {
            "name": "aspects",
            "lo": 0.0,
            "hi": 10.0
          },
          {
            "name": "mmse",
            "lo": 0.0,
            "hi": 30.0
          },
          {
            "name": "age",
            "lo": 40.0,
            "hi": 95.0
          },
          {
            "name": "delai_onset_h",
            "lo": 0.5,
            "hi": 24.0
          }
        ]
      }
    },
    {
      "id": "neurology:detail",
      "slug": "neurology",
      "urlSlug": "neurology",
      "moduleNo": 13,
      "icon": "🧠",
      "label": "Neurologie",
      "service": "neurology-service",
      "kind": "detail",
      "route": "/module/neurology/cas/:caseId",
      "servicePath": "module/neurology",
      "scores": [
        "aspects",
        "nihss",
        "mmse",
        "mcdonald"
      ],
      "sigs": [
        {
          "endpoint": "aspects",
          "fn": "aspects",
          "params": [
            {
              "name": "scores_regions",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "nihss",
          "fn": "nihss",
          "params": [
            {
              "name": "items",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "mmse",
          "fn": "mmse",
          "params": [
            {
              "name": "items",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "mcdonald",
          "fn": "mcdonald_ms",
          "params": [
            {
              "name": "dissemination_espace",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "dissemination_temps",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "bande_oligoclonales",
              "kind": "text",
              "hasDefault": true
            }
          ]
        }
      ],
      "ai": {
        "task": "binary",
        "modalities": [
          "imaging_3d",
          "tabulaire",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "classification",
        "labelNom": "avc_ischemique",
        "classes": [],
        "features": [
          {
            "name": "nihss",
            "lo": 0.0,
            "hi": 30.0
          },
          {
            "name": "aspects",
            "lo": 0.0,
            "hi": 10.0
          },
          {
            "name": "mmse",
            "lo": 0.0,
            "hi": 30.0
          },
          {
            "name": "age",
            "lo": 40.0,
            "hi": 95.0
          },
          {
            "name": "delai_onset_h",
            "lo": 0.5,
            "hi": 24.0
          }
        ]
      }
    },
    {
      "id": "neurology:ia",
      "slug": "neurology",
      "urlSlug": "neurology",
      "moduleNo": 13,
      "icon": "🧠",
      "label": "Neurologie",
      "service": "neurology-service",
      "kind": "ia",
      "route": "/module/neurology/ia",
      "servicePath": "module/neurology",
      "scores": [
        "aspects",
        "nihss",
        "mmse",
        "mcdonald"
      ],
      "sigs": [
        {
          "endpoint": "aspects",
          "fn": "aspects",
          "params": [
            {
              "name": "scores_regions",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "nihss",
          "fn": "nihss",
          "params": [
            {
              "name": "items",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "mmse",
          "fn": "mmse",
          "params": [
            {
              "name": "items",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "mcdonald",
          "fn": "mcdonald_ms",
          "params": [
            {
              "name": "dissemination_espace",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "dissemination_temps",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "bande_oligoclonales",
              "kind": "text",
              "hasDefault": true
            }
          ]
        }
      ],
      "ai": {
        "task": "binary",
        "modalities": [
          "imaging_3d",
          "tabulaire",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "classification",
        "labelNom": "avc_ischemique",
        "classes": [],
        "features": [
          {
            "name": "nihss",
            "lo": 0.0,
            "hi": 30.0
          },
          {
            "name": "aspects",
            "lo": 0.0,
            "hi": 10.0
          },
          {
            "name": "mmse",
            "lo": 0.0,
            "hi": 30.0
          },
          {
            "name": "age",
            "lo": 40.0,
            "hi": 95.0
          },
          {
            "name": "delai_onset_h",
            "lo": 0.5,
            "hi": 24.0
          }
        ]
      }
    },
    {
      "id": "psychiatry:overview",
      "slug": "psychiatry",
      "urlSlug": "psychiatry",
      "moduleNo": 14,
      "icon": "🧬",
      "label": "Psychiatrie",
      "service": "psychiatry-service",
      "kind": "overview",
      "route": "/module/psychiatry",
      "servicePath": "module/psychiatry",
      "scores": [
        "phq9",
        "gad7",
        "cssrs",
        "audit-c"
      ],
      "sigs": [
        {
          "endpoint": "phq9",
          "fn": "phq9",
          "params": [
            {
              "name": "scores_items",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "gad7",
          "fn": "gad7",
          "params": [
            {
              "name": "scores_items",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "cssrs",
          "fn": "cssrs_risk",
          "params": [
            {
              "name": "ideation_passive",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "ideation_active",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "intention",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "plan",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "tentative_antecedente",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "audit-c",
          "fn": "audit_c",
          "params": [
            {
              "name": "nb_jours_boisson_semaine",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "verres_jour_type",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "episodes_6verres",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "regression",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "regression",
        "labelNom": "severite_globale",
        "classes": [],
        "features": [
          {
            "name": "phq9",
            "lo": 0.0,
            "hi": 27.0
          },
          {
            "name": "gad7",
            "lo": 0.0,
            "hi": 21.0
          },
          {
            "name": "audit",
            "lo": 0.0,
            "hi": 40.0
          },
          {
            "name": "sommeil_h",
            "lo": 2.0,
            "hi": 11.0
          },
          {
            "name": "cssrs",
            "lo": 0.0,
            "hi": 5.0
          }
        ]
      }
    },
    {
      "id": "psychiatry:cas",
      "slug": "psychiatry",
      "urlSlug": "psychiatry",
      "moduleNo": 14,
      "icon": "🧬",
      "label": "Psychiatrie",
      "service": "psychiatry-service",
      "kind": "cas",
      "route": "/module/psychiatry/cas",
      "servicePath": "module/psychiatry",
      "scores": [
        "phq9",
        "gad7",
        "cssrs",
        "audit-c"
      ],
      "sigs": [
        {
          "endpoint": "phq9",
          "fn": "phq9",
          "params": [
            {
              "name": "scores_items",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "gad7",
          "fn": "gad7",
          "params": [
            {
              "name": "scores_items",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "cssrs",
          "fn": "cssrs_risk",
          "params": [
            {
              "name": "ideation_passive",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "ideation_active",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "intention",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "plan",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "tentative_antecedente",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "audit-c",
          "fn": "audit_c",
          "params": [
            {
              "name": "nb_jours_boisson_semaine",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "verres_jour_type",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "episodes_6verres",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "regression",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "regression",
        "labelNom": "severite_globale",
        "classes": [],
        "features": [
          {
            "name": "phq9",
            "lo": 0.0,
            "hi": 27.0
          },
          {
            "name": "gad7",
            "lo": 0.0,
            "hi": 21.0
          },
          {
            "name": "audit",
            "lo": 0.0,
            "hi": 40.0
          },
          {
            "name": "sommeil_h",
            "lo": 2.0,
            "hi": 11.0
          },
          {
            "name": "cssrs",
            "lo": 0.0,
            "hi": 5.0
          }
        ]
      }
    },
    {
      "id": "psychiatry:detail",
      "slug": "psychiatry",
      "urlSlug": "psychiatry",
      "moduleNo": 14,
      "icon": "🧬",
      "label": "Psychiatrie",
      "service": "psychiatry-service",
      "kind": "detail",
      "route": "/module/psychiatry/cas/:caseId",
      "servicePath": "module/psychiatry",
      "scores": [
        "phq9",
        "gad7",
        "cssrs",
        "audit-c"
      ],
      "sigs": [
        {
          "endpoint": "phq9",
          "fn": "phq9",
          "params": [
            {
              "name": "scores_items",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "gad7",
          "fn": "gad7",
          "params": [
            {
              "name": "scores_items",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "cssrs",
          "fn": "cssrs_risk",
          "params": [
            {
              "name": "ideation_passive",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "ideation_active",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "intention",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "plan",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "tentative_antecedente",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "audit-c",
          "fn": "audit_c",
          "params": [
            {
              "name": "nb_jours_boisson_semaine",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "verres_jour_type",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "episodes_6verres",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "regression",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "regression",
        "labelNom": "severite_globale",
        "classes": [],
        "features": [
          {
            "name": "phq9",
            "lo": 0.0,
            "hi": 27.0
          },
          {
            "name": "gad7",
            "lo": 0.0,
            "hi": 21.0
          },
          {
            "name": "audit",
            "lo": 0.0,
            "hi": 40.0
          },
          {
            "name": "sommeil_h",
            "lo": 2.0,
            "hi": 11.0
          },
          {
            "name": "cssrs",
            "lo": 0.0,
            "hi": 5.0
          }
        ]
      }
    },
    {
      "id": "psychiatry:ia",
      "slug": "psychiatry",
      "urlSlug": "psychiatry",
      "moduleNo": 14,
      "icon": "🧬",
      "label": "Psychiatrie",
      "service": "psychiatry-service",
      "kind": "ia",
      "route": "/module/psychiatry/ia",
      "servicePath": "module/psychiatry",
      "scores": [
        "phq9",
        "gad7",
        "cssrs",
        "audit-c"
      ],
      "sigs": [
        {
          "endpoint": "phq9",
          "fn": "phq9",
          "params": [
            {
              "name": "scores_items",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "gad7",
          "fn": "gad7",
          "params": [
            {
              "name": "scores_items",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "cssrs",
          "fn": "cssrs_risk",
          "params": [
            {
              "name": "ideation_passive",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "ideation_active",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "intention",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "plan",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "tentative_antecedente",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "audit-c",
          "fn": "audit_c",
          "params": [
            {
              "name": "nb_jours_boisson_semaine",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "verres_jour_type",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "episodes_6verres",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "regression",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "regression",
        "labelNom": "severite_globale",
        "classes": [],
        "features": [
          {
            "name": "phq9",
            "lo": 0.0,
            "hi": 27.0
          },
          {
            "name": "gad7",
            "lo": 0.0,
            "hi": 21.0
          },
          {
            "name": "audit",
            "lo": 0.0,
            "hi": 40.0
          },
          {
            "name": "sommeil_h",
            "lo": 2.0,
            "hi": 11.0
          },
          {
            "name": "cssrs",
            "lo": 0.0,
            "hi": 5.0
          }
        ]
      }
    },
    {
      "id": "pediatrics:overview",
      "slug": "pediatrics",
      "urlSlug": "pediatrics",
      "moduleNo": 15,
      "icon": "👶",
      "label": "Pédiatrie",
      "service": "pediatrics-service",
      "kind": "overview",
      "route": "/module/pediatrics",
      "servicePath": "module/pediatrics",
      "scores": [
        "imc-pediatre"
      ],
      "sigs": [
        {
          "endpoint": "imc-pediatre",
          "fn": "categorie_oms",
          "params": [
            {
              "name": "imc_value",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "regression",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "regression",
        "labelNom": "indice_croissance",
        "classes": [],
        "features": [
          {
            "name": "poids_z",
            "lo": -3.0,
            "hi": 2.5
          },
          {
            "name": "taille_z",
            "lo": -3.0,
            "hi": 2.5
          },
          {
            "name": "apgar",
            "lo": 1.0,
            "hi": 10.0
          },
          {
            "name": "bilirubine_mg_dl",
            "lo": 1.0,
            "hi": 18.0
          },
          {
            "name": "age_mois",
            "lo": 0.0,
            "hi": 60.0
          }
        ]
      }
    },
    {
      "id": "pediatrics:cas",
      "slug": "pediatrics",
      "urlSlug": "pediatrics",
      "moduleNo": 15,
      "icon": "👶",
      "label": "Pédiatrie",
      "service": "pediatrics-service",
      "kind": "cas",
      "route": "/module/pediatrics/cas",
      "servicePath": "module/pediatrics",
      "scores": [
        "imc-pediatre"
      ],
      "sigs": [
        {
          "endpoint": "imc-pediatre",
          "fn": "categorie_oms",
          "params": [
            {
              "name": "imc_value",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "regression",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "regression",
        "labelNom": "indice_croissance",
        "classes": [],
        "features": [
          {
            "name": "poids_z",
            "lo": -3.0,
            "hi": 2.5
          },
          {
            "name": "taille_z",
            "lo": -3.0,
            "hi": 2.5
          },
          {
            "name": "apgar",
            "lo": 1.0,
            "hi": 10.0
          },
          {
            "name": "bilirubine_mg_dl",
            "lo": 1.0,
            "hi": 18.0
          },
          {
            "name": "age_mois",
            "lo": 0.0,
            "hi": 60.0
          }
        ]
      }
    },
    {
      "id": "pediatrics:detail",
      "slug": "pediatrics",
      "urlSlug": "pediatrics",
      "moduleNo": 15,
      "icon": "👶",
      "label": "Pédiatrie",
      "service": "pediatrics-service",
      "kind": "detail",
      "route": "/module/pediatrics/cas/:caseId",
      "servicePath": "module/pediatrics",
      "scores": [
        "imc-pediatre"
      ],
      "sigs": [
        {
          "endpoint": "imc-pediatre",
          "fn": "categorie_oms",
          "params": [
            {
              "name": "imc_value",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "regression",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "regression",
        "labelNom": "indice_croissance",
        "classes": [],
        "features": [
          {
            "name": "poids_z",
            "lo": -3.0,
            "hi": 2.5
          },
          {
            "name": "taille_z",
            "lo": -3.0,
            "hi": 2.5
          },
          {
            "name": "apgar",
            "lo": 1.0,
            "hi": 10.0
          },
          {
            "name": "bilirubine_mg_dl",
            "lo": 1.0,
            "hi": 18.0
          },
          {
            "name": "age_mois",
            "lo": 0.0,
            "hi": 60.0
          }
        ]
      }
    },
    {
      "id": "pediatrics:ia",
      "slug": "pediatrics",
      "urlSlug": "pediatrics",
      "moduleNo": 15,
      "icon": "👶",
      "label": "Pédiatrie",
      "service": "pediatrics-service",
      "kind": "ia",
      "route": "/module/pediatrics/ia",
      "servicePath": "module/pediatrics",
      "scores": [
        "imc-pediatre"
      ],
      "sigs": [
        {
          "endpoint": "imc-pediatre",
          "fn": "categorie_oms",
          "params": [
            {
              "name": "imc_value",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "regression",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "regression",
        "labelNom": "indice_croissance",
        "classes": [],
        "features": [
          {
            "name": "poids_z",
            "lo": -3.0,
            "hi": 2.5
          },
          {
            "name": "taille_z",
            "lo": -3.0,
            "hi": 2.5
          },
          {
            "name": "apgar",
            "lo": 1.0,
            "hi": 10.0
          },
          {
            "name": "bilirubine_mg_dl",
            "lo": 1.0,
            "hi": 18.0
          },
          {
            "name": "age_mois",
            "lo": 0.0,
            "hi": 60.0
          }
        ]
      }
    },
    {
      "id": "nephrology:overview",
      "slug": "nephrology",
      "urlSlug": "nephrology",
      "moduleNo": 16,
      "icon": "🫘",
      "label": "Néphrologie",
      "service": "nephrology-service",
      "kind": "overview",
      "route": "/module/nephrology",
      "servicePath": "module/nephrology",
      "scores": [
        "dfg-ckd-epi",
        "kdigo-mrc",
        "kdigo-aki",
        "ktv"
      ],
      "sigs": [
        {
          "endpoint": "dfg-ckd-epi",
          "fn": "ckd_epi_2021",
          "params": [
            {
              "name": "age",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "sexe",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "creatinine_mgdl",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "kdigo-mrc",
          "fn": "kdigo_ckd_stage",
          "params": [
            {
              "name": "egfr",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "albuminurie_mg_g",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "kdigo-aki",
          "fn": "kdigo_aki_stage",
          "params": [
            {
              "name": "creatinine_baseline",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "creatinine_actuelle",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "diurese_ml_kg_h",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "ktv",
          "fn": "ktv_daugirdas",
          "params": [
            {
              "name": "uree_pre_mmol_l",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "uree_post_mmol_l",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "uf_total_l",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "poids_post_kg",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "duree_h",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "regression",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "regression",
        "labelNom": "stade_ckd_1_5",
        "classes": [],
        "features": [
          {
            "name": "creatinine_mg_l",
            "lo": 4.0,
            "hi": 120.0
          },
          {
            "name": "dfao_ckdepi",
            "lo": 3.0,
            "hi": 120.0
          },
          {
            "name": "kaliemia_mmol_l",
            "lo": 2.5,
            "hi": 6.8
          },
          {
            "name": "proteinurie_g_j",
            "lo": 0.0,
            "hi": 6.0
          },
          {
            "name": "ktv",
            "lo": 0.6,
            "hi": 2.2
          }
        ]
      }
    },
    {
      "id": "nephrology:cas",
      "slug": "nephrology",
      "urlSlug": "nephrology",
      "moduleNo": 16,
      "icon": "🫘",
      "label": "Néphrologie",
      "service": "nephrology-service",
      "kind": "cas",
      "route": "/module/nephrology/cas",
      "servicePath": "module/nephrology",
      "scores": [
        "dfg-ckd-epi",
        "kdigo-mrc",
        "kdigo-aki",
        "ktv"
      ],
      "sigs": [
        {
          "endpoint": "dfg-ckd-epi",
          "fn": "ckd_epi_2021",
          "params": [
            {
              "name": "age",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "sexe",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "creatinine_mgdl",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "kdigo-mrc",
          "fn": "kdigo_ckd_stage",
          "params": [
            {
              "name": "egfr",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "albuminurie_mg_g",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "kdigo-aki",
          "fn": "kdigo_aki_stage",
          "params": [
            {
              "name": "creatinine_baseline",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "creatinine_actuelle",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "diurese_ml_kg_h",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "ktv",
          "fn": "ktv_daugirdas",
          "params": [
            {
              "name": "uree_pre_mmol_l",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "uree_post_mmol_l",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "uf_total_l",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "poids_post_kg",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "duree_h",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "regression",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "regression",
        "labelNom": "stade_ckd_1_5",
        "classes": [],
        "features": [
          {
            "name": "creatinine_mg_l",
            "lo": 4.0,
            "hi": 120.0
          },
          {
            "name": "dfao_ckdepi",
            "lo": 3.0,
            "hi": 120.0
          },
          {
            "name": "kaliemia_mmol_l",
            "lo": 2.5,
            "hi": 6.8
          },
          {
            "name": "proteinurie_g_j",
            "lo": 0.0,
            "hi": 6.0
          },
          {
            "name": "ktv",
            "lo": 0.6,
            "hi": 2.2
          }
        ]
      }
    },
    {
      "id": "nephrology:detail",
      "slug": "nephrology",
      "urlSlug": "nephrology",
      "moduleNo": 16,
      "icon": "🫘",
      "label": "Néphrologie",
      "service": "nephrology-service",
      "kind": "detail",
      "route": "/module/nephrology/cas/:caseId",
      "servicePath": "module/nephrology",
      "scores": [
        "dfg-ckd-epi",
        "kdigo-mrc",
        "kdigo-aki",
        "ktv"
      ],
      "sigs": [
        {
          "endpoint": "dfg-ckd-epi",
          "fn": "ckd_epi_2021",
          "params": [
            {
              "name": "age",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "sexe",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "creatinine_mgdl",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "kdigo-mrc",
          "fn": "kdigo_ckd_stage",
          "params": [
            {
              "name": "egfr",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "albuminurie_mg_g",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "kdigo-aki",
          "fn": "kdigo_aki_stage",
          "params": [
            {
              "name": "creatinine_baseline",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "creatinine_actuelle",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "diurese_ml_kg_h",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "ktv",
          "fn": "ktv_daugirdas",
          "params": [
            {
              "name": "uree_pre_mmol_l",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "uree_post_mmol_l",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "uf_total_l",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "poids_post_kg",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "duree_h",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "regression",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "regression",
        "labelNom": "stade_ckd_1_5",
        "classes": [],
        "features": [
          {
            "name": "creatinine_mg_l",
            "lo": 4.0,
            "hi": 120.0
          },
          {
            "name": "dfao_ckdepi",
            "lo": 3.0,
            "hi": 120.0
          },
          {
            "name": "kaliemia_mmol_l",
            "lo": 2.5,
            "hi": 6.8
          },
          {
            "name": "proteinurie_g_j",
            "lo": 0.0,
            "hi": 6.0
          },
          {
            "name": "ktv",
            "lo": 0.6,
            "hi": 2.2
          }
        ]
      }
    },
    {
      "id": "nephrology:ia",
      "slug": "nephrology",
      "urlSlug": "nephrology",
      "moduleNo": 16,
      "icon": "🫘",
      "label": "Néphrologie",
      "service": "nephrology-service",
      "kind": "ia",
      "route": "/module/nephrology/ia",
      "servicePath": "module/nephrology",
      "scores": [
        "dfg-ckd-epi",
        "kdigo-mrc",
        "kdigo-aki",
        "ktv"
      ],
      "sigs": [
        {
          "endpoint": "dfg-ckd-epi",
          "fn": "ckd_epi_2021",
          "params": [
            {
              "name": "age",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "sexe",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "creatinine_mgdl",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "kdigo-mrc",
          "fn": "kdigo_ckd_stage",
          "params": [
            {
              "name": "egfr",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "albuminurie_mg_g",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "kdigo-aki",
          "fn": "kdigo_aki_stage",
          "params": [
            {
              "name": "creatinine_baseline",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "creatinine_actuelle",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "diurese_ml_kg_h",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "ktv",
          "fn": "ktv_daugirdas",
          "params": [
            {
              "name": "uree_pre_mmol_l",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "uree_post_mmol_l",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "uf_total_l",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "poids_post_kg",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "duree_h",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "regression",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "regression",
        "labelNom": "stade_ckd_1_5",
        "classes": [],
        "features": [
          {
            "name": "creatinine_mg_l",
            "lo": 4.0,
            "hi": 120.0
          },
          {
            "name": "dfao_ckdepi",
            "lo": 3.0,
            "hi": 120.0
          },
          {
            "name": "kaliemia_mmol_l",
            "lo": 2.5,
            "hi": 6.8
          },
          {
            "name": "proteinurie_g_j",
            "lo": 0.0,
            "hi": 6.0
          },
          {
            "name": "ktv",
            "lo": 0.6,
            "hi": 2.2
          }
        ]
      }
    },
    {
      "id": "gastroenterology:overview",
      "slug": "gastroenterology",
      "urlSlug": "gastroenterology",
      "moduleNo": 17,
      "icon": "🫄",
      "label": "Gastro-entérologie",
      "service": "gastroenterology-service",
      "kind": "overview",
      "route": "/module/gastroenterology",
      "servicePath": "module/gastroenterology",
      "scores": [
        "child-pugh",
        "meld",
        "mayo",
        "forrest"
      ],
      "sigs": [
        {
          "endpoint": "child-pugh",
          "fn": "child_pugh",
          "params": [
            {
              "name": "bilirubine_mgdl",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "albumine_gdl",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "inr",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "ascite",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "encephalopathie",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "meld",
          "fn": "meld",
          "params": [
            {
              "name": "bilirubine_mgdl",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "creatinine_mgdl",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "inr",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "sodium_mmol_l",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "dialyse",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "mayo",
          "fn": "mayo_endoscopic",
          "params": [
            {
              "name": "mucosa",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "forrest",
          "fn": "forrest",
          "params": [
            {
              "name": "clot_state",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "binary",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "classification",
        "labelNom": "hemorragie_active",
        "classes": [],
        "features": [
          {
            "name": "forrest",
            "lo": 1.0,
            "hi": 3.0
          },
          {
            "name": "li_rads",
            "lo": 1.0,
            "hi": 5.0
          },
          {
            "name": "hb_g_dl",
            "lo": 4.0,
            "hi": 16.0
          },
          {
            "name": "alcool_u_sem",
            "lo": 0.0,
            "hi": 60.0
          },
          {
            "name": "nodule_mm",
            "lo": 2.0,
            "hi": 60.0
          }
        ]
      }
    },
    {
      "id": "gastroenterology:cas",
      "slug": "gastroenterology",
      "urlSlug": "gastroenterology",
      "moduleNo": 17,
      "icon": "🫄",
      "label": "Gastro-entérologie",
      "service": "gastroenterology-service",
      "kind": "cas",
      "route": "/module/gastroenterology/cas",
      "servicePath": "module/gastroenterology",
      "scores": [
        "child-pugh",
        "meld",
        "mayo",
        "forrest"
      ],
      "sigs": [
        {
          "endpoint": "child-pugh",
          "fn": "child_pugh",
          "params": [
            {
              "name": "bilirubine_mgdl",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "albumine_gdl",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "inr",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "ascite",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "encephalopathie",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "meld",
          "fn": "meld",
          "params": [
            {
              "name": "bilirubine_mgdl",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "creatinine_mgdl",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "inr",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "sodium_mmol_l",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "dialyse",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "mayo",
          "fn": "mayo_endoscopic",
          "params": [
            {
              "name": "mucosa",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "forrest",
          "fn": "forrest",
          "params": [
            {
              "name": "clot_state",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "binary",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "classification",
        "labelNom": "hemorragie_active",
        "classes": [],
        "features": [
          {
            "name": "forrest",
            "lo": 1.0,
            "hi": 3.0
          },
          {
            "name": "li_rads",
            "lo": 1.0,
            "hi": 5.0
          },
          {
            "name": "hb_g_dl",
            "lo": 4.0,
            "hi": 16.0
          },
          {
            "name": "alcool_u_sem",
            "lo": 0.0,
            "hi": 60.0
          },
          {
            "name": "nodule_mm",
            "lo": 2.0,
            "hi": 60.0
          }
        ]
      }
    },
    {
      "id": "gastroenterology:detail",
      "slug": "gastroenterology",
      "urlSlug": "gastroenterology",
      "moduleNo": 17,
      "icon": "🫄",
      "label": "Gastro-entérologie",
      "service": "gastroenterology-service",
      "kind": "detail",
      "route": "/module/gastroenterology/cas/:caseId",
      "servicePath": "module/gastroenterology",
      "scores": [
        "child-pugh",
        "meld",
        "mayo",
        "forrest"
      ],
      "sigs": [
        {
          "endpoint": "child-pugh",
          "fn": "child_pugh",
          "params": [
            {
              "name": "bilirubine_mgdl",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "albumine_gdl",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "inr",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "ascite",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "encephalopathie",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "meld",
          "fn": "meld",
          "params": [
            {
              "name": "bilirubine_mgdl",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "creatinine_mgdl",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "inr",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "sodium_mmol_l",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "dialyse",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "mayo",
          "fn": "mayo_endoscopic",
          "params": [
            {
              "name": "mucosa",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "forrest",
          "fn": "forrest",
          "params": [
            {
              "name": "clot_state",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "binary",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "classification",
        "labelNom": "hemorragie_active",
        "classes": [],
        "features": [
          {
            "name": "forrest",
            "lo": 1.0,
            "hi": 3.0
          },
          {
            "name": "li_rads",
            "lo": 1.0,
            "hi": 5.0
          },
          {
            "name": "hb_g_dl",
            "lo": 4.0,
            "hi": 16.0
          },
          {
            "name": "alcool_u_sem",
            "lo": 0.0,
            "hi": 60.0
          },
          {
            "name": "nodule_mm",
            "lo": 2.0,
            "hi": 60.0
          }
        ]
      }
    },
    {
      "id": "gastroenterology:ia",
      "slug": "gastroenterology",
      "urlSlug": "gastroenterology",
      "moduleNo": 17,
      "icon": "🫄",
      "label": "Gastro-entérologie",
      "service": "gastroenterology-service",
      "kind": "ia",
      "route": "/module/gastroenterology/ia",
      "servicePath": "module/gastroenterology",
      "scores": [
        "child-pugh",
        "meld",
        "mayo",
        "forrest"
      ],
      "sigs": [
        {
          "endpoint": "child-pugh",
          "fn": "child_pugh",
          "params": [
            {
              "name": "bilirubine_mgdl",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "albumine_gdl",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "inr",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "ascite",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "encephalopathie",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "meld",
          "fn": "meld",
          "params": [
            {
              "name": "bilirubine_mgdl",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "creatinine_mgdl",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "inr",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "sodium_mmol_l",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "dialyse",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "mayo",
          "fn": "mayo_endoscopic",
          "params": [
            {
              "name": "mucosa",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "forrest",
          "fn": "forrest",
          "params": [
            {
              "name": "clot_state",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "binary",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "classification",
        "labelNom": "hemorragie_active",
        "classes": [],
        "features": [
          {
            "name": "forrest",
            "lo": 1.0,
            "hi": 3.0
          },
          {
            "name": "li_rads",
            "lo": 1.0,
            "hi": 5.0
          },
          {
            "name": "hb_g_dl",
            "lo": 4.0,
            "hi": 16.0
          },
          {
            "name": "alcool_u_sem",
            "lo": 0.0,
            "hi": 60.0
          },
          {
            "name": "nodule_mm",
            "lo": 2.0,
            "hi": 60.0
          }
        ]
      }
    },
    {
      "id": "dermatology:overview",
      "slug": "dermatology",
      "urlSlug": "dermatology",
      "moduleNo": 18,
      "icon": "🩹",
      "label": "Dermatologie",
      "service": "dermatology-service",
      "kind": "overview",
      "route": "/module/dermatology",
      "servicePath": "module/dermatology",
      "scores": [
        "abcde",
        "pasi",
        "scorad"
      ],
      "sigs": [
        {
          "endpoint": "abcde",
          "fn": "abcde",
          "params": [
            {
              "name": "asymetrie",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "bord_irregulier",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "couleur_multipe",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "diametre_mm",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "evolution",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "pasi",
          "fn": "pasi",
          "params": [
            {
              "name": "erytheme",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "infiltration",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "desquamation",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "surface_pcts",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "scorad",
          "fn": "scorad",
          "params": [
            {
              "name": "surface_pct",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "prurit_0_10",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "erytheme",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "oedema",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "croutes",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "lichenification",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "secheresse",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "insomnie_0_10",
              "kind": "text",
              "hasDefault": true
            }
          ]
        }
      ],
      "ai": {
        "task": "multiclass",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "multiclass",
        "labelNom": "",
        "classes": [
          "nevus",
          "douteux",
          "melanome"
        ],
        "features": [
          {
            "name": "diametre_mm",
            "lo": 2.0,
            "hi": 60.0
          },
          {
            "name": "asymetrie",
            "lo": 0.0,
            "hi": 3.0
          },
          {
            "name": "couleurs_n",
            "lo": 1.0,
            "hi": 6.0
          },
          {
            "name": "breslow_mm",
            "lo": 0.1,
            "hi": 8.0
          },
          {
            "name": "evolutivite",
            "lo": 0.0,
            "hi": 3.0
          }
        ]
      }
    },
    {
      "id": "dermatology:cas",
      "slug": "dermatology",
      "urlSlug": "dermatology",
      "moduleNo": 18,
      "icon": "🩹",
      "label": "Dermatologie",
      "service": "dermatology-service",
      "kind": "cas",
      "route": "/module/dermatology/cas",
      "servicePath": "module/dermatology",
      "scores": [
        "abcde",
        "pasi",
        "scorad"
      ],
      "sigs": [
        {
          "endpoint": "abcde",
          "fn": "abcde",
          "params": [
            {
              "name": "asymetrie",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "bord_irregulier",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "couleur_multipe",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "diametre_mm",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "evolution",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "pasi",
          "fn": "pasi",
          "params": [
            {
              "name": "erytheme",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "infiltration",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "desquamation",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "surface_pcts",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "scorad",
          "fn": "scorad",
          "params": [
            {
              "name": "surface_pct",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "prurit_0_10",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "erytheme",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "oedema",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "croutes",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "lichenification",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "secheresse",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "insomnie_0_10",
              "kind": "text",
              "hasDefault": true
            }
          ]
        }
      ],
      "ai": {
        "task": "multiclass",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "multiclass",
        "labelNom": "",
        "classes": [
          "nevus",
          "douteux",
          "melanome"
        ],
        "features": [
          {
            "name": "diametre_mm",
            "lo": 2.0,
            "hi": 60.0
          },
          {
            "name": "asymetrie",
            "lo": 0.0,
            "hi": 3.0
          },
          {
            "name": "couleurs_n",
            "lo": 1.0,
            "hi": 6.0
          },
          {
            "name": "breslow_mm",
            "lo": 0.1,
            "hi": 8.0
          },
          {
            "name": "evolutivite",
            "lo": 0.0,
            "hi": 3.0
          }
        ]
      }
    },
    {
      "id": "dermatology:detail",
      "slug": "dermatology",
      "urlSlug": "dermatology",
      "moduleNo": 18,
      "icon": "🩹",
      "label": "Dermatologie",
      "service": "dermatology-service",
      "kind": "detail",
      "route": "/module/dermatology/cas/:caseId",
      "servicePath": "module/dermatology",
      "scores": [
        "abcde",
        "pasi",
        "scorad"
      ],
      "sigs": [
        {
          "endpoint": "abcde",
          "fn": "abcde",
          "params": [
            {
              "name": "asymetrie",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "bord_irregulier",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "couleur_multipe",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "diametre_mm",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "evolution",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "pasi",
          "fn": "pasi",
          "params": [
            {
              "name": "erytheme",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "infiltration",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "desquamation",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "surface_pcts",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "scorad",
          "fn": "scorad",
          "params": [
            {
              "name": "surface_pct",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "prurit_0_10",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "erytheme",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "oedema",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "croutes",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "lichenification",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "secheresse",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "insomnie_0_10",
              "kind": "text",
              "hasDefault": true
            }
          ]
        }
      ],
      "ai": {
        "task": "multiclass",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "multiclass",
        "labelNom": "",
        "classes": [
          "nevus",
          "douteux",
          "melanome"
        ],
        "features": [
          {
            "name": "diametre_mm",
            "lo": 2.0,
            "hi": 60.0
          },
          {
            "name": "asymetrie",
            "lo": 0.0,
            "hi": 3.0
          },
          {
            "name": "couleurs_n",
            "lo": 1.0,
            "hi": 6.0
          },
          {
            "name": "breslow_mm",
            "lo": 0.1,
            "hi": 8.0
          },
          {
            "name": "evolutivite",
            "lo": 0.0,
            "hi": 3.0
          }
        ]
      }
    },
    {
      "id": "dermatology:ia",
      "slug": "dermatology",
      "urlSlug": "dermatology",
      "moduleNo": 18,
      "icon": "🩹",
      "label": "Dermatologie",
      "service": "dermatology-service",
      "kind": "ia",
      "route": "/module/dermatology/ia",
      "servicePath": "module/dermatology",
      "scores": [
        "abcde",
        "pasi",
        "scorad"
      ],
      "sigs": [
        {
          "endpoint": "abcde",
          "fn": "abcde",
          "params": [
            {
              "name": "asymetrie",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "bord_irregulier",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "couleur_multipe",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "diametre_mm",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "evolution",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "pasi",
          "fn": "pasi",
          "params": [
            {
              "name": "erytheme",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "infiltration",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "desquamation",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "surface_pcts",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "scorad",
          "fn": "scorad",
          "params": [
            {
              "name": "surface_pct",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "prurit_0_10",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "erytheme",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "oedema",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "croutes",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "lichenification",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "secheresse",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "insomnie_0_10",
              "kind": "text",
              "hasDefault": true
            }
          ]
        }
      ],
      "ai": {
        "task": "multiclass",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "multiclass",
        "labelNom": "",
        "classes": [
          "nevus",
          "douteux",
          "melanome"
        ],
        "features": [
          {
            "name": "diametre_mm",
            "lo": 2.0,
            "hi": 60.0
          },
          {
            "name": "asymetrie",
            "lo": 0.0,
            "hi": 3.0
          },
          {
            "name": "couleurs_n",
            "lo": 1.0,
            "hi": 6.0
          },
          {
            "name": "breslow_mm",
            "lo": 0.1,
            "hi": 8.0
          },
          {
            "name": "evolutivite",
            "lo": 0.0,
            "hi": 3.0
          }
        ]
      }
    },
    {
      "id": "ent:overview",
      "slug": "ent",
      "urlSlug": "ent",
      "moduleNo": 19,
      "icon": "👂",
      "label": "ORL",
      "service": "ent-service",
      "kind": "overview",
      "route": "/module/ent",
      "servicePath": "module/ent",
      "scores": [
        "pta-oms",
        "lund-mackay",
        "bppv"
      ],
      "sigs": [
        {
          "endpoint": "pta-oms",
          "fn": "pta_audiogramme",
          "params": [
            {
              "name": "seuils_db_4freq",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "lund-mackay",
          "fn": "lund_mackay",
          "params": [
            {
              "name": "scores_sinusiens",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "bppv",
          "fn": "bppv_interpretation",
          "params": [
            {
              "name": "hallpike_droit",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "hallpike_gauche",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "vertige_latence",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "fatigue",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "binary",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "classification",
        "labelNom": "tumeur_orl_suspectee",
        "classes": [],
        "features": [
          {
            "name": "perte_db",
            "lo": 10.0,
            "hi": 90.0
          },
          {
            "name": "lund_mackay",
            "lo": 0.0,
            "hi": 24.0
          },
          {
            "name": "pta_db",
            "lo": 10.0,
            "hi": 85.0
          },
          {
            "name": "tinnitus",
            "lo": 0.0,
            "hi": 3.0
          },
          {
            "name": "hpv_pos",
            "lo": 0.0,
            "hi": 1.0
          }
        ]
      }
    },
    {
      "id": "ent:cas",
      "slug": "ent",
      "urlSlug": "ent",
      "moduleNo": 19,
      "icon": "👂",
      "label": "ORL",
      "service": "ent-service",
      "kind": "cas",
      "route": "/module/ent/cas",
      "servicePath": "module/ent",
      "scores": [
        "pta-oms",
        "lund-mackay",
        "bppv"
      ],
      "sigs": [
        {
          "endpoint": "pta-oms",
          "fn": "pta_audiogramme",
          "params": [
            {
              "name": "seuils_db_4freq",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "lund-mackay",
          "fn": "lund_mackay",
          "params": [
            {
              "name": "scores_sinusiens",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "bppv",
          "fn": "bppv_interpretation",
          "params": [
            {
              "name": "hallpike_droit",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "hallpike_gauche",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "vertige_latence",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "fatigue",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "binary",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "classification",
        "labelNom": "tumeur_orl_suspectee",
        "classes": [],
        "features": [
          {
            "name": "perte_db",
            "lo": 10.0,
            "hi": 90.0
          },
          {
            "name": "lund_mackay",
            "lo": 0.0,
            "hi": 24.0
          },
          {
            "name": "pta_db",
            "lo": 10.0,
            "hi": 85.0
          },
          {
            "name": "tinnitus",
            "lo": 0.0,
            "hi": 3.0
          },
          {
            "name": "hpv_pos",
            "lo": 0.0,
            "hi": 1.0
          }
        ]
      }
    },
    {
      "id": "ent:detail",
      "slug": "ent",
      "urlSlug": "ent",
      "moduleNo": 19,
      "icon": "👂",
      "label": "ORL",
      "service": "ent-service",
      "kind": "detail",
      "route": "/module/ent/cas/:caseId",
      "servicePath": "module/ent",
      "scores": [
        "pta-oms",
        "lund-mackay",
        "bppv"
      ],
      "sigs": [
        {
          "endpoint": "pta-oms",
          "fn": "pta_audiogramme",
          "params": [
            {
              "name": "seuils_db_4freq",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "lund-mackay",
          "fn": "lund_mackay",
          "params": [
            {
              "name": "scores_sinusiens",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "bppv",
          "fn": "bppv_interpretation",
          "params": [
            {
              "name": "hallpike_droit",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "hallpike_gauche",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "vertige_latence",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "fatigue",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "binary",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "classification",
        "labelNom": "tumeur_orl_suspectee",
        "classes": [],
        "features": [
          {
            "name": "perte_db",
            "lo": 10.0,
            "hi": 90.0
          },
          {
            "name": "lund_mackay",
            "lo": 0.0,
            "hi": 24.0
          },
          {
            "name": "pta_db",
            "lo": 10.0,
            "hi": 85.0
          },
          {
            "name": "tinnitus",
            "lo": 0.0,
            "hi": 3.0
          },
          {
            "name": "hpv_pos",
            "lo": 0.0,
            "hi": 1.0
          }
        ]
      }
    },
    {
      "id": "ent:ia",
      "slug": "ent",
      "urlSlug": "ent",
      "moduleNo": 19,
      "icon": "👂",
      "label": "ORL",
      "service": "ent-service",
      "kind": "ia",
      "route": "/module/ent/ia",
      "servicePath": "module/ent",
      "scores": [
        "pta-oms",
        "lund-mackay",
        "bppv"
      ],
      "sigs": [
        {
          "endpoint": "pta-oms",
          "fn": "pta_audiogramme",
          "params": [
            {
              "name": "seuils_db_4freq",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "lund-mackay",
          "fn": "lund_mackay",
          "params": [
            {
              "name": "scores_sinusiens",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "bppv",
          "fn": "bppv_interpretation",
          "params": [
            {
              "name": "hallpike_droit",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "hallpike_gauche",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "vertige_latence",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "fatigue",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "binary",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "classification",
        "labelNom": "tumeur_orl_suspectee",
        "classes": [],
        "features": [
          {
            "name": "perte_db",
            "lo": 10.0,
            "hi": 90.0
          },
          {
            "name": "lund_mackay",
            "lo": 0.0,
            "hi": 24.0
          },
          {
            "name": "pta_db",
            "lo": 10.0,
            "hi": 85.0
          },
          {
            "name": "tinnitus",
            "lo": 0.0,
            "hi": 3.0
          },
          {
            "name": "hpv_pos",
            "lo": 0.0,
            "hi": 1.0
          }
        ]
      }
    },
    {
      "id": "rheumatology:overview",
      "slug": "rheumatology",
      "urlSlug": "rheumatology",
      "moduleNo": 20,
      "icon": "🦴",
      "label": "Rhumatologie",
      "service": "rheumatology-service",
      "kind": "overview",
      "route": "/module/rheumatology",
      "servicePath": "module/rheumatology",
      "scores": [
        "das28",
        "basdai",
        "sledaik",
        "kellgren"
      ],
      "sigs": [
        {
          "endpoint": "das28",
          "fn": "das28",
          "params": [
            {
              "name": "tender_count",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "swollen_count",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "vsr_mm_h",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "santé_globale_0_100",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "basdai",
          "fn": "basdai",
          "params": [
            {
              "name": "fatigue",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "douleur_cervicale_dos",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "douleur_peripherique",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "douleur_sensibilite",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "raideur_matinale_intensite",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "raideur_matinale_duree_h",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "sledaik",
          "fn": "sledaik",
          "params": [
            {
              "name": "criteres",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "kellgren",
          "fn": "kellgren_lawrence",
          "params": [
            {
              "name": "pincement",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "osteophytes",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "sclerosis",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "deformite",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "regression",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "regression",
        "labelNom": "activite_0_10",
        "classes": [],
        "features": [
          {
            "name": "das28",
            "lo": 1.0,
            "hi": 9.0
          },
          {
            "name": "crp_mg_l",
            "lo": 1.0,
            "hi": 120.0
          },
          {
            "name": "facteur_rhumato_ui",
            "lo": 0.0,
            "hi": 300.0
          },
          {
            "name": "sledai",
            "lo": 0.0,
            "hi": 24.0
          },
          {
            "name": "kl_grade",
            "lo": 0.0,
            "hi": 4.0
          }
        ]
      }
    },
    {
      "id": "rheumatology:cas",
      "slug": "rheumatology",
      "urlSlug": "rheumatology",
      "moduleNo": 20,
      "icon": "🦴",
      "label": "Rhumatologie",
      "service": "rheumatology-service",
      "kind": "cas",
      "route": "/module/rheumatology/cas",
      "servicePath": "module/rheumatology",
      "scores": [
        "das28",
        "basdai",
        "sledaik",
        "kellgren"
      ],
      "sigs": [
        {
          "endpoint": "das28",
          "fn": "das28",
          "params": [
            {
              "name": "tender_count",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "swollen_count",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "vsr_mm_h",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "santé_globale_0_100",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "basdai",
          "fn": "basdai",
          "params": [
            {
              "name": "fatigue",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "douleur_cervicale_dos",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "douleur_peripherique",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "douleur_sensibilite",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "raideur_matinale_intensite",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "raideur_matinale_duree_h",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "sledaik",
          "fn": "sledaik",
          "params": [
            {
              "name": "criteres",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "kellgren",
          "fn": "kellgren_lawrence",
          "params": [
            {
              "name": "pincement",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "osteophytes",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "sclerosis",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "deformite",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "regression",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "regression",
        "labelNom": "activite_0_10",
        "classes": [],
        "features": [
          {
            "name": "das28",
            "lo": 1.0,
            "hi": 9.0
          },
          {
            "name": "crp_mg_l",
            "lo": 1.0,
            "hi": 120.0
          },
          {
            "name": "facteur_rhumato_ui",
            "lo": 0.0,
            "hi": 300.0
          },
          {
            "name": "sledai",
            "lo": 0.0,
            "hi": 24.0
          },
          {
            "name": "kl_grade",
            "lo": 0.0,
            "hi": 4.0
          }
        ]
      }
    },
    {
      "id": "rheumatology:detail",
      "slug": "rheumatology",
      "urlSlug": "rheumatology",
      "moduleNo": 20,
      "icon": "🦴",
      "label": "Rhumatologie",
      "service": "rheumatology-service",
      "kind": "detail",
      "route": "/module/rheumatology/cas/:caseId",
      "servicePath": "module/rheumatology",
      "scores": [
        "das28",
        "basdai",
        "sledaik",
        "kellgren"
      ],
      "sigs": [
        {
          "endpoint": "das28",
          "fn": "das28",
          "params": [
            {
              "name": "tender_count",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "swollen_count",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "vsr_mm_h",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "santé_globale_0_100",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "basdai",
          "fn": "basdai",
          "params": [
            {
              "name": "fatigue",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "douleur_cervicale_dos",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "douleur_peripherique",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "douleur_sensibilite",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "raideur_matinale_intensite",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "raideur_matinale_duree_h",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "sledaik",
          "fn": "sledaik",
          "params": [
            {
              "name": "criteres",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "kellgren",
          "fn": "kellgren_lawrence",
          "params": [
            {
              "name": "pincement",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "osteophytes",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "sclerosis",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "deformite",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "regression",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "regression",
        "labelNom": "activite_0_10",
        "classes": [],
        "features": [
          {
            "name": "das28",
            "lo": 1.0,
            "hi": 9.0
          },
          {
            "name": "crp_mg_l",
            "lo": 1.0,
            "hi": 120.0
          },
          {
            "name": "facteur_rhumato_ui",
            "lo": 0.0,
            "hi": 300.0
          },
          {
            "name": "sledai",
            "lo": 0.0,
            "hi": 24.0
          },
          {
            "name": "kl_grade",
            "lo": 0.0,
            "hi": 4.0
          }
        ]
      }
    },
    {
      "id": "rheumatology:ia",
      "slug": "rheumatology",
      "urlSlug": "rheumatology",
      "moduleNo": 20,
      "icon": "🦴",
      "label": "Rhumatologie",
      "service": "rheumatology-service",
      "kind": "ia",
      "route": "/module/rheumatology/ia",
      "servicePath": "module/rheumatology",
      "scores": [
        "das28",
        "basdai",
        "sledaik",
        "kellgren"
      ],
      "sigs": [
        {
          "endpoint": "das28",
          "fn": "das28",
          "params": [
            {
              "name": "tender_count",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "swollen_count",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "vsr_mm_h",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "santé_globale_0_100",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "basdai",
          "fn": "basdai",
          "params": [
            {
              "name": "fatigue",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "douleur_cervicale_dos",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "douleur_peripherique",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "douleur_sensibilite",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "raideur_matinale_intensite",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "raideur_matinale_duree_h",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "sledaik",
          "fn": "sledaik",
          "params": [
            {
              "name": "criteres",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "kellgren",
          "fn": "kellgren_lawrence",
          "params": [
            {
              "name": "pincement",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "osteophytes",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "sclerosis",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "deformite",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "regression",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "regression",
        "labelNom": "activite_0_10",
        "classes": [],
        "features": [
          {
            "name": "das28",
            "lo": 1.0,
            "hi": 9.0
          },
          {
            "name": "crp_mg_l",
            "lo": 1.0,
            "hi": 120.0
          },
          {
            "name": "facteur_rhumato_ui",
            "lo": 0.0,
            "hi": 300.0
          },
          {
            "name": "sledai",
            "lo": 0.0,
            "hi": 24.0
          },
          {
            "name": "kl_grade",
            "lo": 0.0,
            "hi": 4.0
          }
        ]
      }
    },
    {
      "id": "urology:overview",
      "slug": "urology",
      "urlSlug": "urology",
      "moduleNo": 21,
      "icon": "🚹",
      "label": "Urologie",
      "service": "urology-service",
      "kind": "overview",
      "route": "/module/urology",
      "servicePath": "module/urology",
      "scores": [
        "ipss",
        "gleason",
        "renal-score",
        "pirads"
      ],
      "sigs": [
        {
          "endpoint": "ipss",
          "fn": "ipss",
          "params": [
            {
              "name": "frequence_nocturne",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "frequence_2h",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "retenue",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "jets_faibles",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "straining",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "incomplets",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "gleason",
          "fn": "gleason_grade_group",
          "params": [
            {
              "name": "primaire",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "secondaire",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "renal-score",
          "fn": "renal_nephrometry",
          "params": [
            {
              "name": "ray_cm",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "endophytique_pct",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "near_urothelium",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "anterieur_posterieur",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "polar",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "pirads",
          "fn": "pirads_lesions",
          "params": [
            {
              "name": "lesions",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "binary",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "classification",
        "labelNom": "ca_prostate_significatif",
        "classes": [],
        "features": [
          {
            "name": "pirads",
            "lo": 1.0,
            "hi": 5.0
          },
          {
            "name": "ips",
            "lo": 0.0,
            "hi": 35.0
          },
          {
            "name": "psa_ng_ml",
            "lo": 0.1,
            "hi": 80.0
          },
          {
            "name": "gleason",
            "lo": 6.0,
            "hi": 10.0
          },
          {
            "name": "renal_score",
            "lo": 4.0,
            "hi": 12.0
          }
        ]
      }
    },
    {
      "id": "urology:cas",
      "slug": "urology",
      "urlSlug": "urology",
      "moduleNo": 21,
      "icon": "🚹",
      "label": "Urologie",
      "service": "urology-service",
      "kind": "cas",
      "route": "/module/urology/cas",
      "servicePath": "module/urology",
      "scores": [
        "ipss",
        "gleason",
        "renal-score",
        "pirads"
      ],
      "sigs": [
        {
          "endpoint": "ipss",
          "fn": "ipss",
          "params": [
            {
              "name": "frequence_nocturne",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "frequence_2h",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "retenue",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "jets_faibles",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "straining",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "incomplets",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "gleason",
          "fn": "gleason_grade_group",
          "params": [
            {
              "name": "primaire",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "secondaire",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "renal-score",
          "fn": "renal_nephrometry",
          "params": [
            {
              "name": "ray_cm",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "endophytique_pct",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "near_urothelium",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "anterieur_posterieur",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "polar",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "pirads",
          "fn": "pirads_lesions",
          "params": [
            {
              "name": "lesions",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "binary",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "classification",
        "labelNom": "ca_prostate_significatif",
        "classes": [],
        "features": [
          {
            "name": "pirads",
            "lo": 1.0,
            "hi": 5.0
          },
          {
            "name": "ips",
            "lo": 0.0,
            "hi": 35.0
          },
          {
            "name": "psa_ng_ml",
            "lo": 0.1,
            "hi": 80.0
          },
          {
            "name": "gleason",
            "lo": 6.0,
            "hi": 10.0
          },
          {
            "name": "renal_score",
            "lo": 4.0,
            "hi": 12.0
          }
        ]
      }
    },
    {
      "id": "urology:detail",
      "slug": "urology",
      "urlSlug": "urology",
      "moduleNo": 21,
      "icon": "🚹",
      "label": "Urologie",
      "service": "urology-service",
      "kind": "detail",
      "route": "/module/urology/cas/:caseId",
      "servicePath": "module/urology",
      "scores": [
        "ipss",
        "gleason",
        "renal-score",
        "pirads"
      ],
      "sigs": [
        {
          "endpoint": "ipss",
          "fn": "ipss",
          "params": [
            {
              "name": "frequence_nocturne",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "frequence_2h",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "retenue",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "jets_faibles",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "straining",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "incomplets",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "gleason",
          "fn": "gleason_grade_group",
          "params": [
            {
              "name": "primaire",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "secondaire",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "renal-score",
          "fn": "renal_nephrometry",
          "params": [
            {
              "name": "ray_cm",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "endophytique_pct",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "near_urothelium",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "anterieur_posterieur",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "polar",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "pirads",
          "fn": "pirads_lesions",
          "params": [
            {
              "name": "lesions",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "binary",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "classification",
        "labelNom": "ca_prostate_significatif",
        "classes": [],
        "features": [
          {
            "name": "pirads",
            "lo": 1.0,
            "hi": 5.0
          },
          {
            "name": "ips",
            "lo": 0.0,
            "hi": 35.0
          },
          {
            "name": "psa_ng_ml",
            "lo": 0.1,
            "hi": 80.0
          },
          {
            "name": "gleason",
            "lo": 6.0,
            "hi": 10.0
          },
          {
            "name": "renal_score",
            "lo": 4.0,
            "hi": 12.0
          }
        ]
      }
    },
    {
      "id": "urology:ia",
      "slug": "urology",
      "urlSlug": "urology",
      "moduleNo": 21,
      "icon": "🚹",
      "label": "Urologie",
      "service": "urology-service",
      "kind": "ia",
      "route": "/module/urology/ia",
      "servicePath": "module/urology",
      "scores": [
        "ipss",
        "gleason",
        "renal-score",
        "pirads"
      ],
      "sigs": [
        {
          "endpoint": "ipss",
          "fn": "ipss",
          "params": [
            {
              "name": "frequence_nocturne",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "frequence_2h",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "retenue",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "jets_faibles",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "straining",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "incomplets",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "gleason",
          "fn": "gleason_grade_group",
          "params": [
            {
              "name": "primaire",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "secondaire",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "renal-score",
          "fn": "renal_nephrometry",
          "params": [
            {
              "name": "ray_cm",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "endophytique_pct",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "near_urothelium",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "anterieur_posterieur",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "polar",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "pirads",
          "fn": "pirads_lesions",
          "params": [
            {
              "name": "lesions",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "binary",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "classification",
        "labelNom": "ca_prostate_significatif",
        "classes": [],
        "features": [
          {
            "name": "pirads",
            "lo": 1.0,
            "hi": 5.0
          },
          {
            "name": "ips",
            "lo": 0.0,
            "hi": 35.0
          },
          {
            "name": "psa_ng_ml",
            "lo": 0.1,
            "hi": 80.0
          },
          {
            "name": "gleason",
            "lo": 6.0,
            "hi": 10.0
          },
          {
            "name": "renal_score",
            "lo": 4.0,
            "hi": 12.0
          }
        ]
      }
    },
    {
      "id": "nuclear-medicine:overview",
      "slug": "nuclear_medicine",
      "urlSlug": "nuclear-medicine",
      "moduleNo": 22,
      "icon": "☢️",
      "label": "Médecine nucléaire",
      "service": "nuclear-medicine-service",
      "kind": "overview",
      "route": "/module/nuclear-medicine",
      "servicePath": "module/nuclear-medicine",
      "scores": [
        "ecog"
      ],
      "sigs": [
        {
          "endpoint": "ecog",
          "fn": "ecog",
          "params": [
            {
              "name": "karnofsky",
              "kind": "text",
              "hasDefault": true
            },
            {
              "name": "description",
              "kind": "text",
              "hasDefault": true
            }
          ]
        }
      ],
      "ai": {
        "task": "regression",
        "modalities": [
          "imaging_3d",
          "tabulaire"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "regression",
        "labelNom": "reponse_pct",
        "classes": [],
        "features": [
          {
            "name": "suv_max",
            "lo": 1.0,
            "hi": 40.0
          },
          {
            "name": "mtv_cm3",
            "lo": 1.0,
            "hi": 400.0
          },
          {
            "name": "tlg",
            "lo": 1.0,
            "hi": 1200.0
          },
          {
            "name": "dose_mbq",
            "lo": 100.0,
            "hi": 7400.0
          },
          {
            "name": "dlco_pct",
            "lo": 30.0,
            "hi": 110.0
          }
        ]
      }
    },
    {
      "id": "nuclear-medicine:cas",
      "slug": "nuclear_medicine",
      "urlSlug": "nuclear-medicine",
      "moduleNo": 22,
      "icon": "☢️",
      "label": "Médecine nucléaire",
      "service": "nuclear-medicine-service",
      "kind": "cas",
      "route": "/module/nuclear-medicine/cas",
      "servicePath": "module/nuclear-medicine",
      "scores": [
        "ecog"
      ],
      "sigs": [
        {
          "endpoint": "ecog",
          "fn": "ecog",
          "params": [
            {
              "name": "karnofsky",
              "kind": "text",
              "hasDefault": true
            },
            {
              "name": "description",
              "kind": "text",
              "hasDefault": true
            }
          ]
        }
      ],
      "ai": {
        "task": "regression",
        "modalities": [
          "imaging_3d",
          "tabulaire"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "regression",
        "labelNom": "reponse_pct",
        "classes": [],
        "features": [
          {
            "name": "suv_max",
            "lo": 1.0,
            "hi": 40.0
          },
          {
            "name": "mtv_cm3",
            "lo": 1.0,
            "hi": 400.0
          },
          {
            "name": "tlg",
            "lo": 1.0,
            "hi": 1200.0
          },
          {
            "name": "dose_mbq",
            "lo": 100.0,
            "hi": 7400.0
          },
          {
            "name": "dlco_pct",
            "lo": 30.0,
            "hi": 110.0
          }
        ]
      }
    },
    {
      "id": "nuclear-medicine:detail",
      "slug": "nuclear_medicine",
      "urlSlug": "nuclear-medicine",
      "moduleNo": 22,
      "icon": "☢️",
      "label": "Médecine nucléaire",
      "service": "nuclear-medicine-service",
      "kind": "detail",
      "route": "/module/nuclear-medicine/cas/:caseId",
      "servicePath": "module/nuclear-medicine",
      "scores": [
        "ecog"
      ],
      "sigs": [
        {
          "endpoint": "ecog",
          "fn": "ecog",
          "params": [
            {
              "name": "karnofsky",
              "kind": "text",
              "hasDefault": true
            },
            {
              "name": "description",
              "kind": "text",
              "hasDefault": true
            }
          ]
        }
      ],
      "ai": {
        "task": "regression",
        "modalities": [
          "imaging_3d",
          "tabulaire"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "regression",
        "labelNom": "reponse_pct",
        "classes": [],
        "features": [
          {
            "name": "suv_max",
            "lo": 1.0,
            "hi": 40.0
          },
          {
            "name": "mtv_cm3",
            "lo": 1.0,
            "hi": 400.0
          },
          {
            "name": "tlg",
            "lo": 1.0,
            "hi": 1200.0
          },
          {
            "name": "dose_mbq",
            "lo": 100.0,
            "hi": 7400.0
          },
          {
            "name": "dlco_pct",
            "lo": 30.0,
            "hi": 110.0
          }
        ]
      }
    },
    {
      "id": "nuclear-medicine:ia",
      "slug": "nuclear_medicine",
      "urlSlug": "nuclear-medicine",
      "moduleNo": 22,
      "icon": "☢️",
      "label": "Médecine nucléaire",
      "service": "nuclear-medicine-service",
      "kind": "ia",
      "route": "/module/nuclear-medicine/ia",
      "servicePath": "module/nuclear-medicine",
      "scores": [
        "ecog"
      ],
      "sigs": [
        {
          "endpoint": "ecog",
          "fn": "ecog",
          "params": [
            {
              "name": "karnofsky",
              "kind": "text",
              "hasDefault": true
            },
            {
              "name": "description",
              "kind": "text",
              "hasDefault": true
            }
          ]
        }
      ],
      "ai": {
        "task": "regression",
        "modalities": [
          "imaging_3d",
          "tabulaire"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "regression",
        "labelNom": "reponse_pct",
        "classes": [],
        "features": [
          {
            "name": "suv_max",
            "lo": 1.0,
            "hi": 40.0
          },
          {
            "name": "mtv_cm3",
            "lo": 1.0,
            "hi": 400.0
          },
          {
            "name": "tlg",
            "lo": 1.0,
            "hi": 1200.0
          },
          {
            "name": "dose_mbq",
            "lo": 100.0,
            "hi": 7400.0
          },
          {
            "name": "dlco_pct",
            "lo": 30.0,
            "hi": 110.0
          }
        ]
      }
    },
    {
      "id": "radiotherapy:overview",
      "slug": "radiotherapy",
      "urlSlug": "radiotherapy",
      "moduleNo": 23,
      "icon": "🎯",
      "label": "Radiothérapie",
      "service": "radiotherapy-service",
      "kind": "overview",
      "route": "/module/radiotherapy",
      "servicePath": "module/radiotherapy",
      "scores": [
        "ecog"
      ],
      "sigs": [
        {
          "endpoint": "ecog",
          "fn": "ecog",
          "params": [
            {
              "name": "karnofsky",
              "kind": "text",
              "hasDefault": true
            },
            {
              "name": "description",
              "kind": "text",
              "hasDefault": true
            }
          ]
        }
      ],
      "ai": {
        "task": "regression",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "regression",
        "labelNom": "toxicite_0_1",
        "classes": [],
        "features": [
          {
            "name": "dose_gy",
            "lo": 30.0,
            "hi": 74.0
          },
          {
            "name": "fractions",
            "lo": 5.0,
            "hi": 35.0
          },
          {
            "name": "v20_pct",
            "lo": 5.0,
            "hi": 45.0
          },
          {
            "name": "gamma_pct",
            "lo": 85.0,
            "hi": 100.0
          },
          {
            "name": "eqd2_gy",
            "lo": 40.0,
            "hi": 90.0
          }
        ]
      }
    },
    {
      "id": "radiotherapy:cas",
      "slug": "radiotherapy",
      "urlSlug": "radiotherapy",
      "moduleNo": 23,
      "icon": "🎯",
      "label": "Radiothérapie",
      "service": "radiotherapy-service",
      "kind": "cas",
      "route": "/module/radiotherapy/cas",
      "servicePath": "module/radiotherapy",
      "scores": [
        "ecog"
      ],
      "sigs": [
        {
          "endpoint": "ecog",
          "fn": "ecog",
          "params": [
            {
              "name": "karnofsky",
              "kind": "text",
              "hasDefault": true
            },
            {
              "name": "description",
              "kind": "text",
              "hasDefault": true
            }
          ]
        }
      ],
      "ai": {
        "task": "regression",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "regression",
        "labelNom": "toxicite_0_1",
        "classes": [],
        "features": [
          {
            "name": "dose_gy",
            "lo": 30.0,
            "hi": 74.0
          },
          {
            "name": "fractions",
            "lo": 5.0,
            "hi": 35.0
          },
          {
            "name": "v20_pct",
            "lo": 5.0,
            "hi": 45.0
          },
          {
            "name": "gamma_pct",
            "lo": 85.0,
            "hi": 100.0
          },
          {
            "name": "eqd2_gy",
            "lo": 40.0,
            "hi": 90.0
          }
        ]
      }
    },
    {
      "id": "radiotherapy:detail",
      "slug": "radiotherapy",
      "urlSlug": "radiotherapy",
      "moduleNo": 23,
      "icon": "🎯",
      "label": "Radiothérapie",
      "service": "radiotherapy-service",
      "kind": "detail",
      "route": "/module/radiotherapy/cas/:caseId",
      "servicePath": "module/radiotherapy",
      "scores": [
        "ecog"
      ],
      "sigs": [
        {
          "endpoint": "ecog",
          "fn": "ecog",
          "params": [
            {
              "name": "karnofsky",
              "kind": "text",
              "hasDefault": true
            },
            {
              "name": "description",
              "kind": "text",
              "hasDefault": true
            }
          ]
        }
      ],
      "ai": {
        "task": "regression",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "regression",
        "labelNom": "toxicite_0_1",
        "classes": [],
        "features": [
          {
            "name": "dose_gy",
            "lo": 30.0,
            "hi": 74.0
          },
          {
            "name": "fractions",
            "lo": 5.0,
            "hi": 35.0
          },
          {
            "name": "v20_pct",
            "lo": 5.0,
            "hi": 45.0
          },
          {
            "name": "gamma_pct",
            "lo": 85.0,
            "hi": 100.0
          },
          {
            "name": "eqd2_gy",
            "lo": 40.0,
            "hi": 90.0
          }
        ]
      }
    },
    {
      "id": "radiotherapy:ia",
      "slug": "radiotherapy",
      "urlSlug": "radiotherapy",
      "moduleNo": 23,
      "icon": "🎯",
      "label": "Radiothérapie",
      "service": "radiotherapy-service",
      "kind": "ia",
      "route": "/module/radiotherapy/ia",
      "servicePath": "module/radiotherapy",
      "scores": [
        "ecog"
      ],
      "sigs": [
        {
          "endpoint": "ecog",
          "fn": "ecog",
          "params": [
            {
              "name": "karnofsky",
              "kind": "text",
              "hasDefault": true
            },
            {
              "name": "description",
              "kind": "text",
              "hasDefault": true
            }
          ]
        }
      ],
      "ai": {
        "task": "regression",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "regression",
        "labelNom": "toxicite_0_1",
        "classes": [],
        "features": [
          {
            "name": "dose_gy",
            "lo": 30.0,
            "hi": 74.0
          },
          {
            "name": "fractions",
            "lo": 5.0,
            "hi": 35.0
          },
          {
            "name": "v20_pct",
            "lo": 5.0,
            "hi": 45.0
          },
          {
            "name": "gamma_pct",
            "lo": 85.0,
            "hi": 100.0
          },
          {
            "name": "eqd2_gy",
            "lo": 40.0,
            "hi": 90.0
          }
        ]
      }
    },
    {
      "id": "anesthesia:overview",
      "slug": "anesthesia",
      "urlSlug": "anesthesia",
      "moduleNo": 24,
      "icon": "💉",
      "label": "Anesthésie-Réanimation",
      "service": "anesthesia-service",
      "kind": "overview",
      "route": "/module/anesthesia",
      "servicePath": "module/anesthesia",
      "scores": [
        "sofa",
        "stop-bang",
        "gcs"
      ],
      "sigs": [
        {
          "endpoint": "sofa",
          "fn": "sofa",
          "params": [
            {
              "name": "respiration_pa02_fio2",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "plaquettes_kul",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "map_mmhg_ou_vasopresseurs",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "gcs",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "bilirubine_mgdl",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "creatinine_mgdl",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "stop-bang",
          "fn": "stop_bang",
          "params": [
            {
              "name": "snorring",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "fatigue",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "apnee_obseree",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "pression_arterielle_haute",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "imc_over_35",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "age_over_50",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "tour_cou_over_40cm",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "sexe_masculin",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "gcs",
          "fn": "gcs",
          "params": [
            {
              "name": "ouverture_yeux",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "reponse_verbale",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "reponse_motrice",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "binary",
        "modalities": [
          "signal_1d",
          "tabulaire",
          "waveform"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "classification",
        "labelNom": "evenement_perop",
        "classes": [],
        "features": [
          {
            "name": "asa",
            "lo": 1.0,
            "hi": 5.0
          },
          {
            "name": "lee_rcri",
            "lo": 0.0,
            "hi": 4.0
          },
          {
            "name": "stopbang",
            "lo": 0.0,
            "hi": 8.0
          },
          {
            "name": "sofa",
            "lo": 0.0,
            "hi": 24.0
          },
          {
            "name": "duree_chir_h",
            "lo": 0.5,
            "hi": 10.0
          }
        ]
      }
    },
    {
      "id": "anesthesia:cas",
      "slug": "anesthesia",
      "urlSlug": "anesthesia",
      "moduleNo": 24,
      "icon": "💉",
      "label": "Anesthésie-Réanimation",
      "service": "anesthesia-service",
      "kind": "cas",
      "route": "/module/anesthesia/cas",
      "servicePath": "module/anesthesia",
      "scores": [
        "sofa",
        "stop-bang",
        "gcs"
      ],
      "sigs": [
        {
          "endpoint": "sofa",
          "fn": "sofa",
          "params": [
            {
              "name": "respiration_pa02_fio2",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "plaquettes_kul",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "map_mmhg_ou_vasopresseurs",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "gcs",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "bilirubine_mgdl",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "creatinine_mgdl",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "stop-bang",
          "fn": "stop_bang",
          "params": [
            {
              "name": "snorring",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "fatigue",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "apnee_obseree",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "pression_arterielle_haute",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "imc_over_35",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "age_over_50",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "tour_cou_over_40cm",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "sexe_masculin",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "gcs",
          "fn": "gcs",
          "params": [
            {
              "name": "ouverture_yeux",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "reponse_verbale",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "reponse_motrice",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "binary",
        "modalities": [
          "signal_1d",
          "tabulaire",
          "waveform"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "classification",
        "labelNom": "evenement_perop",
        "classes": [],
        "features": [
          {
            "name": "asa",
            "lo": 1.0,
            "hi": 5.0
          },
          {
            "name": "lee_rcri",
            "lo": 0.0,
            "hi": 4.0
          },
          {
            "name": "stopbang",
            "lo": 0.0,
            "hi": 8.0
          },
          {
            "name": "sofa",
            "lo": 0.0,
            "hi": 24.0
          },
          {
            "name": "duree_chir_h",
            "lo": 0.5,
            "hi": 10.0
          }
        ]
      }
    },
    {
      "id": "anesthesia:detail",
      "slug": "anesthesia",
      "urlSlug": "anesthesia",
      "moduleNo": 24,
      "icon": "💉",
      "label": "Anesthésie-Réanimation",
      "service": "anesthesia-service",
      "kind": "detail",
      "route": "/module/anesthesia/cas/:caseId",
      "servicePath": "module/anesthesia",
      "scores": [
        "sofa",
        "stop-bang",
        "gcs"
      ],
      "sigs": [
        {
          "endpoint": "sofa",
          "fn": "sofa",
          "params": [
            {
              "name": "respiration_pa02_fio2",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "plaquettes_kul",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "map_mmhg_ou_vasopresseurs",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "gcs",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "bilirubine_mgdl",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "creatinine_mgdl",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "stop-bang",
          "fn": "stop_bang",
          "params": [
            {
              "name": "snorring",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "fatigue",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "apnee_obseree",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "pression_arterielle_haute",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "imc_over_35",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "age_over_50",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "tour_cou_over_40cm",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "sexe_masculin",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "gcs",
          "fn": "gcs",
          "params": [
            {
              "name": "ouverture_yeux",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "reponse_verbale",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "reponse_motrice",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "binary",
        "modalities": [
          "signal_1d",
          "tabulaire",
          "waveform"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "classification",
        "labelNom": "evenement_perop",
        "classes": [],
        "features": [
          {
            "name": "asa",
            "lo": 1.0,
            "hi": 5.0
          },
          {
            "name": "lee_rcri",
            "lo": 0.0,
            "hi": 4.0
          },
          {
            "name": "stopbang",
            "lo": 0.0,
            "hi": 8.0
          },
          {
            "name": "sofa",
            "lo": 0.0,
            "hi": 24.0
          },
          {
            "name": "duree_chir_h",
            "lo": 0.5,
            "hi": 10.0
          }
        ]
      }
    },
    {
      "id": "anesthesia:ia",
      "slug": "anesthesia",
      "urlSlug": "anesthesia",
      "moduleNo": 24,
      "icon": "💉",
      "label": "Anesthésie-Réanimation",
      "service": "anesthesia-service",
      "kind": "ia",
      "route": "/module/anesthesia/ia",
      "servicePath": "module/anesthesia",
      "scores": [
        "sofa",
        "stop-bang",
        "gcs"
      ],
      "sigs": [
        {
          "endpoint": "sofa",
          "fn": "sofa",
          "params": [
            {
              "name": "respiration_pa02_fio2",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "plaquettes_kul",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "map_mmhg_ou_vasopresseurs",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "gcs",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "bilirubine_mgdl",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "creatinine_mgdl",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "stop-bang",
          "fn": "stop_bang",
          "params": [
            {
              "name": "snorring",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "fatigue",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "apnee_obseree",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "pression_arterielle_haute",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "imc_over_35",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "age_over_50",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "tour_cou_over_40cm",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "sexe_masculin",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "gcs",
          "fn": "gcs",
          "params": [
            {
              "name": "ouverture_yeux",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "reponse_verbale",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "reponse_motrice",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "binary",
        "modalities": [
          "signal_1d",
          "tabulaire",
          "waveform"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "classification",
        "labelNom": "evenement_perop",
        "classes": [],
        "features": [
          {
            "name": "asa",
            "lo": 1.0,
            "hi": 5.0
          },
          {
            "name": "lee_rcri",
            "lo": 0.0,
            "hi": 4.0
          },
          {
            "name": "stopbang",
            "lo": 0.0,
            "hi": 8.0
          },
          {
            "name": "sofa",
            "lo": 0.0,
            "hi": 24.0
          },
          {
            "name": "duree_chir_h",
            "lo": 0.5,
            "hi": 10.0
          }
        ]
      }
    },
    {
      "id": "geriatrics:overview",
      "slug": "geriatrics",
      "urlSlug": "geriatrics",
      "moduleNo": 25,
      "icon": "👴",
      "label": "Gériatrie",
      "service": "geriatrics-service",
      "kind": "overview",
      "route": "/module/geriatrics",
      "servicePath": "module/geriatrics",
      "scores": [
        "fried",
        "tug",
        "braden",
        "mna-sf",
        "beers"
      ],
      "sigs": [
        {
          "endpoint": "fried",
          "fn": "fried",
          "params": [
            {
              "name": "fatigue_epuisee",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "perte_poids_recente",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "faible_prise_force",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "marche_lente",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "activite_physique_basse",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "tug",
          "fn": "timed_up_and_go",
          "params": [
            {
              "name": "secondes",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "marche_canne",
              "kind": "text",
              "hasDefault": true
            }
          ]
        },
        {
          "endpoint": "braden",
          "fn": "braden",
          "params": [
            {
              "name": "perception",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "humidite",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "activite",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "mobilite",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "nutrition",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "frottement",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "mna-sf",
          "fn": "mna_sf",
          "params": [
            {
              "name": "declin_repas",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "perte_poids",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "mobilite_reduite",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "stress_maladie",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "neuropsychologique",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "imc_value",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "beers",
          "fn": "beers_risky_medicaments",
          "params": [
            {
              "name": "medicaments",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "binary",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "classification",
        "labelNom": "chute_12_mois",
        "classes": [],
        "features": [
          {
            "name": "fried",
            "lo": 0.0,
            "hi": 5.0
          },
          {
            "name": "rockwood",
            "lo": 1.0,
            "hi": 9.0
          },
          {
            "name": "tug_s",
            "lo": 7.0,
            "hi": 45.0
          },
          {
            "name": "mna",
            "lo": 7.0,
            "hi": 30.0
          },
          {
            "name": "beers_n",
            "lo": 0.0,
            "hi": 12.0
          },
          {
            "name": "braden",
            "lo": 6.0,
            "hi": 23.0
          }
        ]
      }
    },
    {
      "id": "geriatrics:cas",
      "slug": "geriatrics",
      "urlSlug": "geriatrics",
      "moduleNo": 25,
      "icon": "👴",
      "label": "Gériatrie",
      "service": "geriatrics-service",
      "kind": "cas",
      "route": "/module/geriatrics/cas",
      "servicePath": "module/geriatrics",
      "scores": [
        "fried",
        "tug",
        "braden",
        "mna-sf",
        "beers"
      ],
      "sigs": [
        {
          "endpoint": "fried",
          "fn": "fried",
          "params": [
            {
              "name": "fatigue_epuisee",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "perte_poids_recente",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "faible_prise_force",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "marche_lente",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "activite_physique_basse",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "tug",
          "fn": "timed_up_and_go",
          "params": [
            {
              "name": "secondes",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "marche_canne",
              "kind": "text",
              "hasDefault": true
            }
          ]
        },
        {
          "endpoint": "braden",
          "fn": "braden",
          "params": [
            {
              "name": "perception",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "humidite",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "activite",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "mobilite",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "nutrition",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "frottement",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "mna-sf",
          "fn": "mna_sf",
          "params": [
            {
              "name": "declin_repas",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "perte_poids",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "mobilite_reduite",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "stress_maladie",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "neuropsychologique",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "imc_value",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "beers",
          "fn": "beers_risky_medicaments",
          "params": [
            {
              "name": "medicaments",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "binary",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "classification",
        "labelNom": "chute_12_mois",
        "classes": [],
        "features": [
          {
            "name": "fried",
            "lo": 0.0,
            "hi": 5.0
          },
          {
            "name": "rockwood",
            "lo": 1.0,
            "hi": 9.0
          },
          {
            "name": "tug_s",
            "lo": 7.0,
            "hi": 45.0
          },
          {
            "name": "mna",
            "lo": 7.0,
            "hi": 30.0
          },
          {
            "name": "beers_n",
            "lo": 0.0,
            "hi": 12.0
          },
          {
            "name": "braden",
            "lo": 6.0,
            "hi": 23.0
          }
        ]
      }
    },
    {
      "id": "geriatrics:detail",
      "slug": "geriatrics",
      "urlSlug": "geriatrics",
      "moduleNo": 25,
      "icon": "👴",
      "label": "Gériatrie",
      "service": "geriatrics-service",
      "kind": "detail",
      "route": "/module/geriatrics/cas/:caseId",
      "servicePath": "module/geriatrics",
      "scores": [
        "fried",
        "tug",
        "braden",
        "mna-sf",
        "beers"
      ],
      "sigs": [
        {
          "endpoint": "fried",
          "fn": "fried",
          "params": [
            {
              "name": "fatigue_epuisee",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "perte_poids_recente",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "faible_prise_force",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "marche_lente",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "activite_physique_basse",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "tug",
          "fn": "timed_up_and_go",
          "params": [
            {
              "name": "secondes",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "marche_canne",
              "kind": "text",
              "hasDefault": true
            }
          ]
        },
        {
          "endpoint": "braden",
          "fn": "braden",
          "params": [
            {
              "name": "perception",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "humidite",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "activite",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "mobilite",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "nutrition",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "frottement",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "mna-sf",
          "fn": "mna_sf",
          "params": [
            {
              "name": "declin_repas",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "perte_poids",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "mobilite_reduite",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "stress_maladie",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "neuropsychologique",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "imc_value",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "beers",
          "fn": "beers_risky_medicaments",
          "params": [
            {
              "name": "medicaments",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "binary",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "classification",
        "labelNom": "chute_12_mois",
        "classes": [],
        "features": [
          {
            "name": "fried",
            "lo": 0.0,
            "hi": 5.0
          },
          {
            "name": "rockwood",
            "lo": 1.0,
            "hi": 9.0
          },
          {
            "name": "tug_s",
            "lo": 7.0,
            "hi": 45.0
          },
          {
            "name": "mna",
            "lo": 7.0,
            "hi": 30.0
          },
          {
            "name": "beers_n",
            "lo": 0.0,
            "hi": 12.0
          },
          {
            "name": "braden",
            "lo": 6.0,
            "hi": 23.0
          }
        ]
      }
    },
    {
      "id": "geriatrics:ia",
      "slug": "geriatrics",
      "urlSlug": "geriatrics",
      "moduleNo": 25,
      "icon": "👴",
      "label": "Gériatrie",
      "service": "geriatrics-service",
      "kind": "ia",
      "route": "/module/geriatrics/ia",
      "servicePath": "module/geriatrics",
      "scores": [
        "fried",
        "tug",
        "braden",
        "mna-sf",
        "beers"
      ],
      "sigs": [
        {
          "endpoint": "fried",
          "fn": "fried",
          "params": [
            {
              "name": "fatigue_epuisee",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "perte_poids_recente",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "faible_prise_force",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "marche_lente",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "activite_physique_basse",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "tug",
          "fn": "timed_up_and_go",
          "params": [
            {
              "name": "secondes",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "marche_canne",
              "kind": "text",
              "hasDefault": true
            }
          ]
        },
        {
          "endpoint": "braden",
          "fn": "braden",
          "params": [
            {
              "name": "perception",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "humidite",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "activite",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "mobilite",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "nutrition",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "frottement",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "mna-sf",
          "fn": "mna_sf",
          "params": [
            {
              "name": "declin_repas",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "perte_poids",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "mobilite_reduite",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "stress_maladie",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "neuropsychologique",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "imc_value",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "beers",
          "fn": "beers_risky_medicaments",
          "params": [
            {
              "name": "medicaments",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "binary",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "classification",
        "labelNom": "chute_12_mois",
        "classes": [],
        "features": [
          {
            "name": "fried",
            "lo": 0.0,
            "hi": 5.0
          },
          {
            "name": "rockwood",
            "lo": 1.0,
            "hi": 9.0
          },
          {
            "name": "tug_s",
            "lo": 7.0,
            "hi": 45.0
          },
          {
            "name": "mna",
            "lo": 7.0,
            "hi": 30.0
          },
          {
            "name": "beers_n",
            "lo": 0.0,
            "hi": 12.0
          },
          {
            "name": "braden",
            "lo": 6.0,
            "hi": 23.0
          }
        ]
      }
    },
    {
      "id": "emergency:overview",
      "slug": "emergency",
      "urlSlug": "emergency",
      "moduleNo": 26,
      "icon": "🚨",
      "label": "Urgences",
      "service": "emergency-service",
      "kind": "overview",
      "route": "/module/emergency",
      "servicePath": "module/emergency",
      "scores": [
        "esi",
        "ctmp",
        "qsofa",
        "parkland",
        "curbs65",
        "shock-index"
      ],
      "sigs": [
        {
          "endpoint": "esi",
          "fn": "esi",
          "params": [
            {
              "name": "niveau_ressources",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "voies_aeriennes_stables",
              "kind": "text",
              "hasDefault": true
            },
            {
              "name": "conscience_stable",
              "kind": "text",
              "hasDefault": true
            },
            {
              "name": "signes_vitaux_dangereux",
              "kind": "text",
              "hasDefault": true
            },
            {
              "name": "facteur_risque_haut",
              "kind": "text",
              "hasDefault": true
            },
            {
              "name": "douleur_severe",
              "kind": "text",
              "hasDefault": true
            },
            {
              "name": "saignement_actif",
              "kind": "text",
              "hasDefault": true
            }
          ]
        },
        {
          "endpoint": "ctmp",
          "fn": "ctmp",
          "params": [
            {
              "name": "score",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "qsofa",
          "fn": "qsofa",
          "params": [
            {
              "name": "freq_resp",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "pas_systolique",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "gcs_ou_avpu",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "parkland",
          "fn": "parkland",
          "params": [
            {
              "name": "poids_kg",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "pct_sbc",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "heures_depuis_brule",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "curbs65",
          "fn": "curbs65",
          "params": [
            {
              "name": "confusion",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "uree_mmol_l",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "freq_resp",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "pas_systolique",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "age",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "shock-index",
          "fn": "shock_index",
          "params": [
            {
              "name": "pouls",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "pas_systolique",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "multiclass",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "multiclass",
        "labelNom": "",
        "classes": [
          "hors_danger",
          "urgent",
          "tres_urgent",
          "vital"
        ],
        "features": [
          {
            "name": "esi",
            "lo": 1.0,
            "hi": 5.0
          },
          {
            "name": "qsofa",
            "lo": 0.0,
            "hi": 3.0
          },
          {
            "name": "iss",
            "lo": 1.0,
            "hi": 50.0
          },
          {
            "name": "nihss",
            "lo": 0.0,
            "hi": 30.0
          },
          {
            "name": "shock_index",
            "lo": 0.4,
            "hi": 1.8
          }
        ]
      }
    },
    {
      "id": "emergency:cas",
      "slug": "emergency",
      "urlSlug": "emergency",
      "moduleNo": 26,
      "icon": "🚨",
      "label": "Urgences",
      "service": "emergency-service",
      "kind": "cas",
      "route": "/module/emergency/cas",
      "servicePath": "module/emergency",
      "scores": [
        "esi",
        "ctmp",
        "qsofa",
        "parkland",
        "curbs65",
        "shock-index"
      ],
      "sigs": [
        {
          "endpoint": "esi",
          "fn": "esi",
          "params": [
            {
              "name": "niveau_ressources",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "voies_aeriennes_stables",
              "kind": "text",
              "hasDefault": true
            },
            {
              "name": "conscience_stable",
              "kind": "text",
              "hasDefault": true
            },
            {
              "name": "signes_vitaux_dangereux",
              "kind": "text",
              "hasDefault": true
            },
            {
              "name": "facteur_risque_haut",
              "kind": "text",
              "hasDefault": true
            },
            {
              "name": "douleur_severe",
              "kind": "text",
              "hasDefault": true
            },
            {
              "name": "saignement_actif",
              "kind": "text",
              "hasDefault": true
            }
          ]
        },
        {
          "endpoint": "ctmp",
          "fn": "ctmp",
          "params": [
            {
              "name": "score",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "qsofa",
          "fn": "qsofa",
          "params": [
            {
              "name": "freq_resp",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "pas_systolique",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "gcs_ou_avpu",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "parkland",
          "fn": "parkland",
          "params": [
            {
              "name": "poids_kg",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "pct_sbc",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "heures_depuis_brule",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "curbs65",
          "fn": "curbs65",
          "params": [
            {
              "name": "confusion",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "uree_mmol_l",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "freq_resp",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "pas_systolique",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "age",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "shock-index",
          "fn": "shock_index",
          "params": [
            {
              "name": "pouls",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "pas_systolique",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "multiclass",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "multiclass",
        "labelNom": "",
        "classes": [
          "hors_danger",
          "urgent",
          "tres_urgent",
          "vital"
        ],
        "features": [
          {
            "name": "esi",
            "lo": 1.0,
            "hi": 5.0
          },
          {
            "name": "qsofa",
            "lo": 0.0,
            "hi": 3.0
          },
          {
            "name": "iss",
            "lo": 1.0,
            "hi": 50.0
          },
          {
            "name": "nihss",
            "lo": 0.0,
            "hi": 30.0
          },
          {
            "name": "shock_index",
            "lo": 0.4,
            "hi": 1.8
          }
        ]
      }
    },
    {
      "id": "emergency:detail",
      "slug": "emergency",
      "urlSlug": "emergency",
      "moduleNo": 26,
      "icon": "🚨",
      "label": "Urgences",
      "service": "emergency-service",
      "kind": "detail",
      "route": "/module/emergency/cas/:caseId",
      "servicePath": "module/emergency",
      "scores": [
        "esi",
        "ctmp",
        "qsofa",
        "parkland",
        "curbs65",
        "shock-index"
      ],
      "sigs": [
        {
          "endpoint": "esi",
          "fn": "esi",
          "params": [
            {
              "name": "niveau_ressources",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "voies_aeriennes_stables",
              "kind": "text",
              "hasDefault": true
            },
            {
              "name": "conscience_stable",
              "kind": "text",
              "hasDefault": true
            },
            {
              "name": "signes_vitaux_dangereux",
              "kind": "text",
              "hasDefault": true
            },
            {
              "name": "facteur_risque_haut",
              "kind": "text",
              "hasDefault": true
            },
            {
              "name": "douleur_severe",
              "kind": "text",
              "hasDefault": true
            },
            {
              "name": "saignement_actif",
              "kind": "text",
              "hasDefault": true
            }
          ]
        },
        {
          "endpoint": "ctmp",
          "fn": "ctmp",
          "params": [
            {
              "name": "score",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "qsofa",
          "fn": "qsofa",
          "params": [
            {
              "name": "freq_resp",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "pas_systolique",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "gcs_ou_avpu",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "parkland",
          "fn": "parkland",
          "params": [
            {
              "name": "poids_kg",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "pct_sbc",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "heures_depuis_brule",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "curbs65",
          "fn": "curbs65",
          "params": [
            {
              "name": "confusion",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "uree_mmol_l",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "freq_resp",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "pas_systolique",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "age",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "shock-index",
          "fn": "shock_index",
          "params": [
            {
              "name": "pouls",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "pas_systolique",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "multiclass",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "multiclass",
        "labelNom": "",
        "classes": [
          "hors_danger",
          "urgent",
          "tres_urgent",
          "vital"
        ],
        "features": [
          {
            "name": "esi",
            "lo": 1.0,
            "hi": 5.0
          },
          {
            "name": "qsofa",
            "lo": 0.0,
            "hi": 3.0
          },
          {
            "name": "iss",
            "lo": 1.0,
            "hi": 50.0
          },
          {
            "name": "nihss",
            "lo": 0.0,
            "hi": 30.0
          },
          {
            "name": "shock_index",
            "lo": 0.4,
            "hi": 1.8
          }
        ]
      }
    },
    {
      "id": "emergency:ia",
      "slug": "emergency",
      "urlSlug": "emergency",
      "moduleNo": 26,
      "icon": "🚨",
      "label": "Urgences",
      "service": "emergency-service",
      "kind": "ia",
      "route": "/module/emergency/ia",
      "servicePath": "module/emergency",
      "scores": [
        "esi",
        "ctmp",
        "qsofa",
        "parkland",
        "curbs65",
        "shock-index"
      ],
      "sigs": [
        {
          "endpoint": "esi",
          "fn": "esi",
          "params": [
            {
              "name": "niveau_ressources",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "voies_aeriennes_stables",
              "kind": "text",
              "hasDefault": true
            },
            {
              "name": "conscience_stable",
              "kind": "text",
              "hasDefault": true
            },
            {
              "name": "signes_vitaux_dangereux",
              "kind": "text",
              "hasDefault": true
            },
            {
              "name": "facteur_risque_haut",
              "kind": "text",
              "hasDefault": true
            },
            {
              "name": "douleur_severe",
              "kind": "text",
              "hasDefault": true
            },
            {
              "name": "saignement_actif",
              "kind": "text",
              "hasDefault": true
            }
          ]
        },
        {
          "endpoint": "ctmp",
          "fn": "ctmp",
          "params": [
            {
              "name": "score",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "qsofa",
          "fn": "qsofa",
          "params": [
            {
              "name": "freq_resp",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "pas_systolique",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "gcs_ou_avpu",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "parkland",
          "fn": "parkland",
          "params": [
            {
              "name": "poids_kg",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "pct_sbc",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "heures_depuis_brule",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "curbs65",
          "fn": "curbs65",
          "params": [
            {
              "name": "confusion",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "uree_mmol_l",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "freq_resp",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "pas_systolique",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "age",
              "kind": "text",
              "hasDefault": false
            }
          ]
        },
        {
          "endpoint": "shock-index",
          "fn": "shock_index",
          "params": [
            {
              "name": "pouls",
              "kind": "text",
              "hasDefault": false
            },
            {
              "name": "pas_systolique",
              "kind": "text",
              "hasDefault": false
            }
          ]
        }
      ],
      "ai": {
        "task": "multiclass",
        "modalities": [
          "tabulaire",
          "imaging_2d",
          "texte"
        ],
        "missingPolicy": "degrade_elegamment",
        "sharedTrunk": true,
        "explainability": [
          "modality_importance",
          "attention_viz",
          "shap_multimodal"
        ],
        "labelTask": "multiclass",
        "labelNom": "",
        "classes": [
          "hors_danger",
          "urgent",
          "tres_urgent",
          "vital"
        ],
        "features": [
          {
            "name": "esi",
            "lo": 1.0,
            "hi": 5.0
          },
          {
            "name": "qsofa",
            "lo": 0.0,
            "hi": 3.0
          },
          {
            "name": "iss",
            "lo": 1.0,
            "hi": 50.0
          },
          {
            "name": "nihss",
            "lo": 0.0,
            "hi": 30.0
          },
          {
            "name": "shock_index",
            "lo": 0.4,
            "hi": 1.8
          }
        ]
      }
    },
];

export function screenById(id: string): ScreenDef | undefined {
  return SCREENS.find((s) => s.id === id);
}

export function screensOfModule(urlSlug: string): ScreenDef[] {
  return SCREENS.filter((s) => s.urlSlug === urlSlug);
}
