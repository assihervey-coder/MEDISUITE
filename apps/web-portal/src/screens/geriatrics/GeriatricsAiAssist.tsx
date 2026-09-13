/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Gériatrie · Assistance IA (non validée — R6-R8).
 *  Route : /module/geriatrics/ia · service : geriatrics-service (module 25).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import AiAssistScreen from "../templates/AiAssistScreen";
import { screenById } from "../registry.generated";

export default function GeriatricsAiAssist() {
  return <AiAssistScreen screen={screenById("geriatrics:ia")!} />;
}
