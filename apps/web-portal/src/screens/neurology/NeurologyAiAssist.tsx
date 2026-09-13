/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Neurologie · Assistance IA (non validée — R6-R8).
 *  Route : /module/neurology/ia · service : neurology-service (module 13).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import AiAssistScreen from "../templates/AiAssistScreen";
import { screenById } from "../registry.generated";

export default function NeurologyAiAssist() {
  return <AiAssistScreen screen={screenById("neurology:ia")!} />;
}
