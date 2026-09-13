/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Tumeurs · Assistance IA (non validée — R6-R8).
 *  Route : /module/tumor/ia · service : tumor-service (module 04).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import AiAssistScreen from "../templates/AiAssistScreen";
import { screenById } from "../registry.generated";

export default function TumorAiAssist() {
  return <AiAssistScreen screen={screenById("tumor:ia")!} />;
}
