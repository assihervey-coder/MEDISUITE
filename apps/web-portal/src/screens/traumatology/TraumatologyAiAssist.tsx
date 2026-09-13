/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Traumatologie · Assistance IA (non validée — R6-R8).
 *  Route : /module/traumatology/ia · service : traumatology-service (module 07).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import AiAssistScreen from "../templates/AiAssistScreen";
import { screenById } from "../registry.generated";

export default function TraumatologyAiAssist() {
  return <AiAssistScreen screen={screenById("traumatology:ia")!} />;
}
