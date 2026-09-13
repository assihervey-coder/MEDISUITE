/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Fertilité · Assistance IA (non validée — R6-R8).
 *  Route : /module/fertility/ia · service : fertility-service (module 12).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import AiAssistScreen from "../templates/AiAssistScreen";
import { screenById } from "../registry.generated";

export default function FertilityAiAssist() {
  return <AiAssistScreen screen={screenById("fertility:ia")!} />;
}
