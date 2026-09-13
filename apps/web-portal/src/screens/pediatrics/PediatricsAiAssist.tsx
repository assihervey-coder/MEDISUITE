/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Pédiatrie · Assistance IA (non validée — R6-R8).
 *  Route : /module/pediatrics/ia · service : pediatrics-service (module 15).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import AiAssistScreen from "../templates/AiAssistScreen";
import { screenById } from "../registry.generated";

export default function PediatricsAiAssist() {
  return <AiAssistScreen screen={screenById("pediatrics:ia")!} />;
}
