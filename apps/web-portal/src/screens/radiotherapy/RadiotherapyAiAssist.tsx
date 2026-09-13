/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Radiothérapie · Assistance IA (non validée — R6-R8).
 *  Route : /module/radiotherapy/ia · service : radiotherapy-service (module 23).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import AiAssistScreen from "../templates/AiAssistScreen";
import { screenById } from "../registry.generated";

export default function RadiotherapyAiAssist() {
  return <AiAssistScreen screen={screenById("radiotherapy:ia")!} />;
}
