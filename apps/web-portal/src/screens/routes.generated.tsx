/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — NE PAS ÉDITER À LA MAIN.
 *  Régénérer : `make screens` · vérifier : `python tools/generate_screens.py --check`.
 */
import type { ReactNode } from "react";
import OncologyOverview from "./oncology/OncologyOverview";
import OncologyCaseList from "./oncology/OncologyCaseList";
import OncologyCaseDetail from "./oncology/OncologyCaseDetail";
import OncologyAiAssist from "./oncology/OncologyAiAssist";
import TumorOverview from "./tumor/TumorOverview";
import TumorCaseList from "./tumor/TumorCaseList";
import TumorCaseDetail from "./tumor/TumorCaseDetail";
import TumorAiAssist from "./tumor/TumorAiAssist";
import OphthalmologyOverview from "./ophthalmology/OphthalmologyOverview";
import OphthalmologyCaseList from "./ophthalmology/OphthalmologyCaseList";
import OphthalmologyCaseDetail from "./ophthalmology/OphthalmologyCaseDetail";
import OphthalmologyAiAssist from "./ophthalmology/OphthalmologyAiAssist";
import DiabetesOverview from "./diabetes/DiabetesOverview";
import DiabetesCaseList from "./diabetes/DiabetesCaseList";
import DiabetesCaseDetail from "./diabetes/DiabetesCaseDetail";
import DiabetesAiAssist from "./diabetes/DiabetesAiAssist";
import TraumatologyOverview from "./traumatology/TraumatologyOverview";
import TraumatologyCaseList from "./traumatology/TraumatologyCaseList";
import TraumatologyCaseDetail from "./traumatology/TraumatologyCaseDetail";
import TraumatologyAiAssist from "./traumatology/TraumatologyAiAssist";
import CardiologyOverview from "./cardiology/CardiologyOverview";
import CardiologyCaseList from "./cardiology/CardiologyCaseList";
import CardiologyCaseDetail from "./cardiology/CardiologyCaseDetail";
import CardiologyAiAssist from "./cardiology/CardiologyAiAssist";
import PneumologyOverview from "./pneumology/PneumologyOverview";
import PneumologyCaseList from "./pneumology/PneumologyCaseList";
import PneumologyCaseDetail from "./pneumology/PneumologyCaseDetail";
import PneumologyAiAssist from "./pneumology/PneumologyAiAssist";
import ObstetricsOverview from "./obstetrics/ObstetricsOverview";
import ObstetricsCaseList from "./obstetrics/ObstetricsCaseList";
import ObstetricsCaseDetail from "./obstetrics/ObstetricsCaseDetail";
import ObstetricsAiAssist from "./obstetrics/ObstetricsAiAssist";
import GynecologyOverview from "./gynecology/GynecologyOverview";
import GynecologyCaseList from "./gynecology/GynecologyCaseList";
import GynecologyCaseDetail from "./gynecology/GynecologyCaseDetail";
import GynecologyAiAssist from "./gynecology/GynecologyAiAssist";
import FertilityOverview from "./fertility/FertilityOverview";
import FertilityCaseList from "./fertility/FertilityCaseList";
import FertilityCaseDetail from "./fertility/FertilityCaseDetail";
import FertilityAiAssist from "./fertility/FertilityAiAssist";
import NeurologyOverview from "./neurology/NeurologyOverview";
import NeurologyCaseList from "./neurology/NeurologyCaseList";
import NeurologyCaseDetail from "./neurology/NeurologyCaseDetail";
import NeurologyAiAssist from "./neurology/NeurologyAiAssist";
import PsychiatryOverview from "./psychiatry/PsychiatryOverview";
import PsychiatryCaseList from "./psychiatry/PsychiatryCaseList";
import PsychiatryCaseDetail from "./psychiatry/PsychiatryCaseDetail";
import PsychiatryAiAssist from "./psychiatry/PsychiatryAiAssist";
import PediatricsOverview from "./pediatrics/PediatricsOverview";
import PediatricsCaseList from "./pediatrics/PediatricsCaseList";
import PediatricsCaseDetail from "./pediatrics/PediatricsCaseDetail";
import PediatricsAiAssist from "./pediatrics/PediatricsAiAssist";
import NephrologyOverview from "./nephrology/NephrologyOverview";
import NephrologyCaseList from "./nephrology/NephrologyCaseList";
import NephrologyCaseDetail from "./nephrology/NephrologyCaseDetail";
import NephrologyAiAssist from "./nephrology/NephrologyAiAssist";
import GastroenterologyOverview from "./gastroenterology/GastroenterologyOverview";
import GastroenterologyCaseList from "./gastroenterology/GastroenterologyCaseList";
import GastroenterologyCaseDetail from "./gastroenterology/GastroenterologyCaseDetail";
import GastroenterologyAiAssist from "./gastroenterology/GastroenterologyAiAssist";
import DermatologyOverview from "./dermatology/DermatologyOverview";
import DermatologyCaseList from "./dermatology/DermatologyCaseList";
import DermatologyCaseDetail from "./dermatology/DermatologyCaseDetail";
import DermatologyAiAssist from "./dermatology/DermatologyAiAssist";
import EntOverview from "./ent/EntOverview";
import EntCaseList from "./ent/EntCaseList";
import EntCaseDetail from "./ent/EntCaseDetail";
import EntAiAssist from "./ent/EntAiAssist";
import RheumatologyOverview from "./rheumatology/RheumatologyOverview";
import RheumatologyCaseList from "./rheumatology/RheumatologyCaseList";
import RheumatologyCaseDetail from "./rheumatology/RheumatologyCaseDetail";
import RheumatologyAiAssist from "./rheumatology/RheumatologyAiAssist";
import UrologyOverview from "./urology/UrologyOverview";
import UrologyCaseList from "./urology/UrologyCaseList";
import UrologyCaseDetail from "./urology/UrologyCaseDetail";
import UrologyAiAssist from "./urology/UrologyAiAssist";
import NuclearMedicineOverview from "./nuclear-medicine/NuclearMedicineOverview";
import NuclearMedicineCaseList from "./nuclear-medicine/NuclearMedicineCaseList";
import NuclearMedicineCaseDetail from "./nuclear-medicine/NuclearMedicineCaseDetail";
import NuclearMedicineAiAssist from "./nuclear-medicine/NuclearMedicineAiAssist";
import RadiotherapyOverview from "./radiotherapy/RadiotherapyOverview";
import RadiotherapyCaseList from "./radiotherapy/RadiotherapyCaseList";
import RadiotherapyCaseDetail from "./radiotherapy/RadiotherapyCaseDetail";
import RadiotherapyAiAssist from "./radiotherapy/RadiotherapyAiAssist";
import AnesthesiaOverview from "./anesthesia/AnesthesiaOverview";
import AnesthesiaCaseList from "./anesthesia/AnesthesiaCaseList";
import AnesthesiaCaseDetail from "./anesthesia/AnesthesiaCaseDetail";
import AnesthesiaAiAssist from "./anesthesia/AnesthesiaAiAssist";
import GeriatricsOverview from "./geriatrics/GeriatricsOverview";
import GeriatricsCaseList from "./geriatrics/GeriatricsCaseList";
import GeriatricsCaseDetail from "./geriatrics/GeriatricsCaseDetail";
import GeriatricsAiAssist from "./geriatrics/GeriatricsAiAssist";
import EmergencyOverview from "./emergency/EmergencyOverview";
import EmergencyCaseList from "./emergency/EmergencyCaseList";
import EmergencyCaseDetail from "./emergency/EmergencyCaseDetail";
import EmergencyAiAssist from "./emergency/EmergencyAiAssist";

/** Routes des 96 écrans fins — consommées par App.tsx (une seule map). */
export const SCREEN_ROUTES: Array<{ path: string; element: ReactNode }> = [
  { path: "/module/oncology", element: <OncologyOverview /> },
  { path: "/module/oncology/cas", element: <OncologyCaseList /> },
  { path: "/module/oncology/cas/:caseId", element: <OncologyCaseDetail /> },
  { path: "/module/oncology/ia", element: <OncologyAiAssist /> },
  { path: "/module/tumor", element: <TumorOverview /> },
  { path: "/module/tumor/cas", element: <TumorCaseList /> },
  { path: "/module/tumor/cas/:caseId", element: <TumorCaseDetail /> },
  { path: "/module/tumor/ia", element: <TumorAiAssist /> },
  { path: "/module/ophthalmology", element: <OphthalmologyOverview /> },
  { path: "/module/ophthalmology/cas", element: <OphthalmologyCaseList /> },
  { path: "/module/ophthalmology/cas/:caseId", element: <OphthalmologyCaseDetail /> },
  { path: "/module/ophthalmology/ia", element: <OphthalmologyAiAssist /> },
  { path: "/module/diabetes", element: <DiabetesOverview /> },
  { path: "/module/diabetes/cas", element: <DiabetesCaseList /> },
  { path: "/module/diabetes/cas/:caseId", element: <DiabetesCaseDetail /> },
  { path: "/module/diabetes/ia", element: <DiabetesAiAssist /> },
  { path: "/module/traumatology", element: <TraumatologyOverview /> },
  { path: "/module/traumatology/cas", element: <TraumatologyCaseList /> },
  { path: "/module/traumatology/cas/:caseId", element: <TraumatologyCaseDetail /> },
  { path: "/module/traumatology/ia", element: <TraumatologyAiAssist /> },
  { path: "/module/cardiology", element: <CardiologyOverview /> },
  { path: "/module/cardiology/cas", element: <CardiologyCaseList /> },
  { path: "/module/cardiology/cas/:caseId", element: <CardiologyCaseDetail /> },
  { path: "/module/cardiology/ia", element: <CardiologyAiAssist /> },
  { path: "/module/pneumology", element: <PneumologyOverview /> },
  { path: "/module/pneumology/cas", element: <PneumologyCaseList /> },
  { path: "/module/pneumology/cas/:caseId", element: <PneumologyCaseDetail /> },
  { path: "/module/pneumology/ia", element: <PneumologyAiAssist /> },
  { path: "/module/obstetrics", element: <ObstetricsOverview /> },
  { path: "/module/obstetrics/cas", element: <ObstetricsCaseList /> },
  { path: "/module/obstetrics/cas/:caseId", element: <ObstetricsCaseDetail /> },
  { path: "/module/obstetrics/ia", element: <ObstetricsAiAssist /> },
  { path: "/module/gynecology", element: <GynecologyOverview /> },
  { path: "/module/gynecology/cas", element: <GynecologyCaseList /> },
  { path: "/module/gynecology/cas/:caseId", element: <GynecologyCaseDetail /> },
  { path: "/module/gynecology/ia", element: <GynecologyAiAssist /> },
  { path: "/module/fertility", element: <FertilityOverview /> },
  { path: "/module/fertility/cas", element: <FertilityCaseList /> },
  { path: "/module/fertility/cas/:caseId", element: <FertilityCaseDetail /> },
  { path: "/module/fertility/ia", element: <FertilityAiAssist /> },
  { path: "/module/neurology", element: <NeurologyOverview /> },
  { path: "/module/neurology/cas", element: <NeurologyCaseList /> },
  { path: "/module/neurology/cas/:caseId", element: <NeurologyCaseDetail /> },
  { path: "/module/neurology/ia", element: <NeurologyAiAssist /> },
  { path: "/module/psychiatry", element: <PsychiatryOverview /> },
  { path: "/module/psychiatry/cas", element: <PsychiatryCaseList /> },
  { path: "/module/psychiatry/cas/:caseId", element: <PsychiatryCaseDetail /> },
  { path: "/module/psychiatry/ia", element: <PsychiatryAiAssist /> },
  { path: "/module/pediatrics", element: <PediatricsOverview /> },
  { path: "/module/pediatrics/cas", element: <PediatricsCaseList /> },
  { path: "/module/pediatrics/cas/:caseId", element: <PediatricsCaseDetail /> },
  { path: "/module/pediatrics/ia", element: <PediatricsAiAssist /> },
  { path: "/module/nephrology", element: <NephrologyOverview /> },
  { path: "/module/nephrology/cas", element: <NephrologyCaseList /> },
  { path: "/module/nephrology/cas/:caseId", element: <NephrologyCaseDetail /> },
  { path: "/module/nephrology/ia", element: <NephrologyAiAssist /> },
  { path: "/module/gastroenterology", element: <GastroenterologyOverview /> },
  { path: "/module/gastroenterology/cas", element: <GastroenterologyCaseList /> },
  { path: "/module/gastroenterology/cas/:caseId", element: <GastroenterologyCaseDetail /> },
  { path: "/module/gastroenterology/ia", element: <GastroenterologyAiAssist /> },
  { path: "/module/dermatology", element: <DermatologyOverview /> },
  { path: "/module/dermatology/cas", element: <DermatologyCaseList /> },
  { path: "/module/dermatology/cas/:caseId", element: <DermatologyCaseDetail /> },
  { path: "/module/dermatology/ia", element: <DermatologyAiAssist /> },
  { path: "/module/ent", element: <EntOverview /> },
  { path: "/module/ent/cas", element: <EntCaseList /> },
  { path: "/module/ent/cas/:caseId", element: <EntCaseDetail /> },
  { path: "/module/ent/ia", element: <EntAiAssist /> },
  { path: "/module/rheumatology", element: <RheumatologyOverview /> },
  { path: "/module/rheumatology/cas", element: <RheumatologyCaseList /> },
  { path: "/module/rheumatology/cas/:caseId", element: <RheumatologyCaseDetail /> },
  { path: "/module/rheumatology/ia", element: <RheumatologyAiAssist /> },
  { path: "/module/urology", element: <UrologyOverview /> },
  { path: "/module/urology/cas", element: <UrologyCaseList /> },
  { path: "/module/urology/cas/:caseId", element: <UrologyCaseDetail /> },
  { path: "/module/urology/ia", element: <UrologyAiAssist /> },
  { path: "/module/nuclear-medicine", element: <NuclearMedicineOverview /> },
  { path: "/module/nuclear-medicine/cas", element: <NuclearMedicineCaseList /> },
  { path: "/module/nuclear-medicine/cas/:caseId", element: <NuclearMedicineCaseDetail /> },
  { path: "/module/nuclear-medicine/ia", element: <NuclearMedicineAiAssist /> },
  { path: "/module/radiotherapy", element: <RadiotherapyOverview /> },
  { path: "/module/radiotherapy/cas", element: <RadiotherapyCaseList /> },
  { path: "/module/radiotherapy/cas/:caseId", element: <RadiotherapyCaseDetail /> },
  { path: "/module/radiotherapy/ia", element: <RadiotherapyAiAssist /> },
  { path: "/module/anesthesia", element: <AnesthesiaOverview /> },
  { path: "/module/anesthesia/cas", element: <AnesthesiaCaseList /> },
  { path: "/module/anesthesia/cas/:caseId", element: <AnesthesiaCaseDetail /> },
  { path: "/module/anesthesia/ia", element: <AnesthesiaAiAssist /> },
  { path: "/module/geriatrics", element: <GeriatricsOverview /> },
  { path: "/module/geriatrics/cas", element: <GeriatricsCaseList /> },
  { path: "/module/geriatrics/cas/:caseId", element: <GeriatricsCaseDetail /> },
  { path: "/module/geriatrics/ia", element: <GeriatricsAiAssist /> },
  { path: "/module/emergency", element: <EmergencyOverview /> },
  { path: "/module/emergency/cas", element: <EmergencyCaseList /> },
  { path: "/module/emergency/cas/:caseId", element: <EmergencyCaseDetail /> },
  { path: "/module/emergency/ia", element: <EmergencyAiAssist /> },
];
