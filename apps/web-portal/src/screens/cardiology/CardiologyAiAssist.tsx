/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Cardiologie · Assistance IA (non validée — R6-R8).
 *  Route : /module/cardiology/ia · service : cardiology-service (module 08).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import AiAssistScreen from "../templates/AiAssistScreen";
import { screenById } from "../registry.generated";

export default function CardiologyAiAssist() {
  return <AiAssistScreen screen={screenById("cardiology:ia")!} />;
}
