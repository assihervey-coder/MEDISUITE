/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Ophtalmologie · Assistance IA (non validée — R6-R8).
 *  Route : /module/ophthalmology/ia · service : ophthalmology-service (module 05).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import AiAssistScreen from "../templates/AiAssistScreen";
import { screenById } from "../registry.generated";

export default function OphthalmologyAiAssist() {
  return <AiAssistScreen screen={screenById("ophthalmology:ia")!} />;
}
