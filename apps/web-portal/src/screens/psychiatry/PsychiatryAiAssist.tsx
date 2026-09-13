/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Psychiatrie · Assistance IA (non validée — R6-R8).
 *  Route : /module/psychiatry/ia · service : psychiatry-service (module 14).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import AiAssistScreen from "../templates/AiAssistScreen";
import { screenById } from "../registry.generated";

export default function PsychiatryAiAssist() {
  return <AiAssistScreen screen={screenById("psychiatry:ia")!} />;
}
