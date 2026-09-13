/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Urologie · Assistance IA (non validée — R6-R8).
 *  Route : /module/urology/ia · service : urology-service (module 21).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import AiAssistScreen from "../templates/AiAssistScreen";
import { screenById } from "../registry.generated";

export default function UrologyAiAssist() {
  return <AiAssistScreen screen={screenById("urology:ia")!} />;
}
