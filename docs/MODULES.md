# Les 26 modules cliniques de MEDISUITE

| # | Module | Service | Périmètre fonctionnel |
|---|---|---|---|
| 1 | 🩻 Imaging | `imaging-service` | Radiographie, scanner, IRM, échographie — DICOMweb complet |
| 2 | 🧪 Laboratory | `laboratory-service` | Prescription → prélèvement → analyse → validation → compte-rendu |
| 3 | 🎗️ Oncology | `oncology-service` | Dépistage (7 organes), BI-RADS, TNM/AJCC 8e, biomarqueurs, RCP |
| 4 | 🧠 Tumor | `tumor-service` | Segmentation cérébrale, volumétrie, grading OMS 2021, planif RT |
| 5 | 👁️ Ophthalmology | `ophthalmology-service` | Fond d'œil, OCT, glaucome (C/D, RNFL), rétinopathie diabétique |
| 6 | 🩸 Diabetes | `diabetes-service` | Risque ADA, HbA1c/TIR, complications, CGM (Dexcom/Libre/Medtronic) |
| 7 | 🦴 Traumatology | `traumatology-service` | Fractures AO/OTA, ligaments (LCA…), Cobb, FRAX, polytrauma ISS |
| 8 | ❤️ Cardiology | `cardiology-service` | ECG 12 dérivations, ETT (FEVG), coro-CT CAD-RADS, Holter, CHA2DS2-VASc |
| 9 | 🫁 Pneumology | `pneumology-service` | Nodules (Fleischner/Lung-RADS), TB, BPCO GOLD, embolie (Wells), spirométrie |
| 10 | 🤰 Obstetrics | `obstetrics-service` | Biométrie fœtale, CTG/FIGO, clarté nucale, pré-éclampsie, Bishop |
| 11 | 🌸 Gynecology | `gynecology-service` | Pap/Bethesda, HPV, IOTA simple rules, O-RADS, SOPK Rotterdam, ENZIAN |
| 12 | 🧬 Fertility | `fertility-service` | Réserve ovarienne (AMH/CFA), spermogramme OMS 2021, sélection embryonnaire |
| 13 | 🧠 Neurology | `neurology-service` | AVC (ASPECTS, NIHSS), épilepsie EEG, MMSE/MoCA, Parkinson UPDRS, McDonald/EDSS |
| 14 | 🧬 Psychiatry | `psychiatry-service` | PHQ-9, GAD-7, Y-BOCS, C-SSRS risque suicidaire, AUDIT/DAST |
| 15 | 👶 Pediatrics | `pediatrics-service` | APGAR, courbes OMS, ictère néonatal, calendrier vaccinal PEV, Denver |
| 16 | 🫘 Nephrology | `nephrology-service` | CKD-EPI/KDIGO, AKI KDIGO, kt/V dialyse, néphrométrie RENAL |
| 17 | 🫄 Gastroenterology | `gastroenterology-service` | Polypes, LI-RADS, Mayo/CDEIS (MICI), Los Angeles (RGO), Forrest |
| 18 | 🩹 Dermatology | `dermatology-service` | Mélanome ABCDE/7-points, Breslow, PASI, SCORAD, VASI |
| 19 | 👂 ENT | `ent-service` | Audiogramme, BPPV, Lund-Mackay, cancers ORL (HPV) |
| 20 | 🦴 Rheumatology | `rheumatology-service` | DAS28, BASDAI/ASDAS, SLEDAI, Kellgren-Lawrence, critères ANCA |
| 21 | 🚹 Urology | `urology-service` | PI-RADS, Gleason, IPSS, score RENAL, calculs (SWL/URS) |
| 22 | ☢️ Nuclear Medicine | `nuclear-medicine-service` | SUV, MTV/TLG, PERCIST, dosimétrie MIRD, théranostique Lu-177 |
| 23 | 🎯 Radiotherapy | `radiotherapy-service` | GTV/CTV/PTV, IMRT/VMAT, DVH, gamma index, EQD2, QA machine |
| 24 | 💉 Anesthesia | `anesthesia-service` | ASA, Lee/RCRI, STOP-BANG, SOFA/APACHE II, RASS, analgésie multimodale |
| 25 | 👴 Geriatrics | `geriatrics-service` | Fried, Rockwood, TUG, MMSE/MoCA, Beers/STOPP-START, MNA, Braden, Barthel |
| 26 | 🚨 Emergency | `emergency-service` | ESI/CTMP/Manchester, qSOFA, ISS, NIHSS code AVC, STEMI, Parkland |

> Chaque module est un microservice indépendant partageant le noyau `packages/clinical-rules`.
> Test : `make test-services`. Ports 8100-8123 (ordre du tableau).