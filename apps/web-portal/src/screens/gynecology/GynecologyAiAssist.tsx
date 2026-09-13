/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Gynécologie · Assistance IA (non validée — R6-R8).
 *  Route : /module/gynecology/ia · service : gynecology-service (module 11).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import AiAssistScreen from "../templates/AiAssistScreen";
import { screenById } from "../registry.generated";

export default function GynecologyAiAssist() {
  return <AiAssistScreen screen={screenById("gynecology:ia")!} />;
}
