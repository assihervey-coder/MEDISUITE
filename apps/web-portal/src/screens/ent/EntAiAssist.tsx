/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : ORL · Assistance IA (non validée — R6-R8).
 *  Route : /module/ent/ia · service : ent-service (module 19).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import AiAssistScreen from "../templates/AiAssistScreen";
import { screenById } from "../registry.generated";

export default function EntAiAssist() {
  return <AiAssistScreen screen={screenById("ent:ia")!} />;
}
