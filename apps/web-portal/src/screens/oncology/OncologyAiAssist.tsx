/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Oncologie · Assistance IA (non validée — R6-R8).
 *  Route : /module/oncology/ia · service : oncology-service (module 03).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import AiAssistScreen from "../templates/AiAssistScreen";
import { screenById } from "../registry.generated";

export default function OncologyAiAssist() {
  return <AiAssistScreen screen={screenById("oncology:ia")!} />;
}
