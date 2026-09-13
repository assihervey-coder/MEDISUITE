/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Obstétrique · Assistance IA (non validée — R6-R8).
 *  Route : /module/obstetrics/ia · service : obstetrics-service (module 10).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import AiAssistScreen from "../templates/AiAssistScreen";
import { screenById } from "../registry.generated";

export default function ObstetricsAiAssist() {
  return <AiAssistScreen screen={screenById("obstetrics:ia")!} />;
}
