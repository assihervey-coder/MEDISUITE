# Index des model-cards MEDISUITE — 26 modules

> Générées par `tools/generate_model_cards.py` 1.0.0 depuis les
> sources de vérité du dépôt (registry + configs IA + audit 26 modules).
> **État global** : 🟢 structure livrée · 🟠 données synthétiques ·
> 🔴 métriques R6-R8 (verrou M+18 → SAP → CER TD-11, ADR-0026).

| Fiche | Module | Nom | Tâche | Modalités | Service | Données / métriques |
|---|---|---|---|---|---|---|
| MC-01 | [imaging](MC-01-imaging.md) | Imagerie — détection d'anomalies | `classification` | imaging_2d, imaging_3d, tabulaire | `imaging-service` | 🟠 synthétique / 🔴 R6 |
| MC-02 | [laboratory](MC-02-laboratory.md) | Laboratoire — sévérité biologique | `regression` | tabulaire, texte | `laboratory-service` | 🟠 synthétique / 🔴 R6 |
| MC-03 | [oncology](MC-03-oncology.md) | Oncologie — stadification tumorale | `multiclass` | imaging_2d, imaging_3d, tabulaire, texte, genomique | `oncology-service` | 🟠 synthétique / 🔴 R6 |
| MC-04 | [tumor](MC-04-tumor.md) | Tumeurs cérébrales — volumétrie | `segmentation` | imaging_3d, tabulaire | `tumor-service` | 🟠 synthétique / 🔴 R6 |
| MC-05 | [ophthalmology](MC-05-ophthalmology.md) | Ophtalmologie — rétinopathie / glaucome | `multiclass` | imaging_2d, tabulaire | `ophthalmology-service` | 🟠 synthétique / 🔴 R6 |
| MC-06 | [diabetes](MC-06-diabetes.md) | Diabète — risque de complication | `regression` | tabulaire, imaging_2d, texte | `diabetes-service` | 🟠 synthétique / 🔴 R6 |
| MC-07 | [traumatology](MC-07-traumatology.md) | Traumatologie — polytrauma | `multilabel` | tabulaire, imaging_2d, texte | `traumatology-service` | 🟠 synthétique / 🔴 R6 |
| MC-08 | [cardiology](MC-08-cardiology.md) | Cardiologie — syndrome coronarien | `multiclass` | signal_1d, tabulaire, texte | `cardiology-service` | 🟠 synthétique / 🔴 R6 |
| MC-09 | [pneumology](MC-09-pneumology.md) | Pneumologie — TB / BPCO / embolie | `multilabel` | tabulaire, imaging_2d, texte | `pneumology-service` | 🟠 synthétique / 🔴 R6 |
| MC-10 | [obstetrics](MC-10-obstetrics.md) | Obstétrique — pré-éclampsie | `classification` | waveform, imaging_2d, tabulaire | `obstetrics-service` | 🟠 synthétique / 🔴 R6 |
| MC-11 | [gynecology](MC-11-gynecology.md) | Gynécologie — malignité suspectée | `classification` | tabulaire, imaging_2d, texte | `gynecology-service` | 🟠 synthétique / 🔴 R6 |
| MC-12 | [fertility](MC-12-fertility.md) | Fertilité — pronostic de conception | `regression` | tabulaire, imaging_2d, texte | `fertility-service` | 🟠 synthétique / 🔴 R6 |
| MC-13 | [neurology](MC-13-neurology.md) | Neurologie — AVC ischémique | `classification` | imaging_3d, tabulaire, texte | `neurology-service` | 🟠 synthétique / 🔴 R6 |
| MC-14 | [psychiatry](MC-14-psychiatry.md) | Psychiatrie — sévérité globale | `regression` | tabulaire, imaging_2d, texte | `psychiatry-service` | 🟠 synthétique / 🔴 R6 |
| MC-15 | [pediatrics](MC-15-pediatrics.md) | Pédiatrie — croissance | `regression` | tabulaire, imaging_2d, texte | `pediatrics-service` | 🟠 synthétique / 🔴 R6 |
| MC-16 | [nephrology](MC-16-nephrology.md) | Néphrologie — stade d'insuffisance rénale | `regression` | tabulaire, imaging_2d, texte | `nephrology-service` | 🟠 synthétique / 🔴 R6 |
| MC-17 | [gastroenterology](MC-17-gastroenterology.md) | Gastro-entérologie — hémorragie active | `classification` | tabulaire, imaging_2d, texte | `gastroenterology-service` | 🟠 synthétique / 🔴 R6 |
| MC-18 | [dermatology](MC-18-dermatology.md) | Dermatologie — lésions pigmentaires | `multiclass` | tabulaire, imaging_2d, texte | `dermatology-service` | 🟠 synthétique / 🔴 R6 |
| MC-19 | [ent](MC-19-ent.md) | ORL — tumeur suspectée | `classification` | tabulaire, imaging_2d, texte | `ent-service` | 🟠 synthétique / 🔴 R6 |
| MC-20 | [rheumatology](MC-20-rheumatology.md) | Rhumatologie — activité inflammatoire | `regression` | tabulaire, imaging_2d, texte | `rheumatology-service` | 🟠 synthétique / 🔴 R6 |
| MC-21 | [urology](MC-21-urology.md) | Urologie — cancer de prostate significatif | `classification` | tabulaire, imaging_2d, texte | `urology-service` | 🟠 synthétique / 🔴 R6 |
| MC-22 | [nuclear_medicine](MC-22-nuclear_medicine.md) | Médecine nucléaire — réponse thérapeutique | `regression` | imaging_3d, tabulaire | `nuclear-medicine-service` | 🟠 synthétique / 🔴 R6 |
| MC-23 | [radiotherapy](MC-23-radiotherapy.md) | Radiothérapie — toxicité prédite | `regression` | tabulaire, imaging_2d, texte | `radiotherapy-service` | 🟠 synthétique / 🔴 R6 |
| MC-24 | [anesthesia](MC-24-anesthesia.md) | Anesthésie — événement péri-opératoire | `classification` | signal_1d, tabulaire, waveform | `anesthesia-service` | 🟠 synthétique / 🔴 R6 |
| MC-25 | [geriatrics](MC-25-geriatrics.md) | Gériatrie — risque de chute | `classification` | tabulaire, imaging_2d, texte | `geriatrics-service` | 🟠 synthétique / 🔴 R6 |
| MC-26 | [emergency](MC-26-emergency.md) | Urgences — triage | `multiclass` | tabulaire, imaging_2d, texte | `emergency-service` | 🟠 synthétique / 🔴 R6 |

**Liens** : audit reproductible `docs/audit-26-modules.md` · registry
`datasets/registry.py` · plan de validation `compliance/mdr/technical-documentation/08-plan-validation-v1.0.0.md`
(R6 = entraînement réel + model-cards finalisées) · CER `compliance/mdr/technical-documentation/11-rapport-evaluation-clinique-meddev-271.md`.
26 fiches couvrent l'intégralité des 26 modules cliniques.
