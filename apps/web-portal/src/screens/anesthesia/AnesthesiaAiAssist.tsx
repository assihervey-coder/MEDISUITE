/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Anesthésie-Réanimation · Assistance IA (non validée — R6-R8).
 *  Route : /module/anesthesia/ia · service : anesthesia-service (module 24).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import AiAssistScreen from "../templates/AiAssistScreen";
import { screenById } from "../registry.generated";

export default function AnesthesiaAiAssist() {
  return <AiAssistScreen screen={screenById("anesthesia:ia")!} />;
}
