/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Médecine nucléaire · Assistance IA (non validée — R6-R8).
 *  Route : /module/nuclear-medicine/ia · service : nuclear-medicine-service (module 22).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import AiAssistScreen from "../templates/AiAssistScreen";
import { screenById } from "../registry.generated";

export default function NuclearMedicineAiAssist() {
  return <AiAssistScreen screen={screenById("nuclear-medicine:ia")!} />;
}
