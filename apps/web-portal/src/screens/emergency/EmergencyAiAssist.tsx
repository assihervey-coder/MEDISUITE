/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Urgences · Assistance IA (non validée — R6-R8).
 *  Route : /module/emergency/ia · service : emergency-service (module 26).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import AiAssistScreen from "../templates/AiAssistScreen";
import { screenById } from "../registry.generated";

export default function EmergencyAiAssist() {
  return <AiAssistScreen screen={screenById("emergency:ia")!} />;
}
