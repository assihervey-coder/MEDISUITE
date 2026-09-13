/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Néphrologie · Assistance IA (non validée — R6-R8).
 *  Route : /module/nephrology/ia · service : nephrology-service (module 16).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import AiAssistScreen from "../templates/AiAssistScreen";
import { screenById } from "../registry.generated";

export default function NephrologyAiAssist() {
  return <AiAssistScreen screen={screenById("nephrology:ia")!} />;
}
