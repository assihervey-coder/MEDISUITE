/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Pneumologie · Assistance IA (non validée — R6-R8).
 *  Route : /module/pneumology/ia · service : pneumology-service (module 09).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import AiAssistScreen from "../templates/AiAssistScreen";
import { screenById } from "../registry.generated";

export default function PneumologyAiAssist() {
  return <AiAssistScreen screen={screenById("pneumology:ia")!} />;
}
