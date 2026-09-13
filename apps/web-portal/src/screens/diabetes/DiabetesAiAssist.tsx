/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Diabétologie · Assistance IA (non validée — R6-R8).
 *  Route : /module/diabetes/ia · service : diabetes-service (module 06).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import AiAssistScreen from "../templates/AiAssistScreen";
import { screenById } from "../registry.generated";

export default function DiabetesAiAssist() {
  return <AiAssistScreen screen={screenById("diabetes:ia")!} />;
}
