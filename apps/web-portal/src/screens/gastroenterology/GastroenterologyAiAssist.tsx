/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Gastro-entérologie · Assistance IA (non validée — R6-R8).
 *  Route : /module/gastroenterology/ia · service : gastroenterology-service (module 17).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import AiAssistScreen from "../templates/AiAssistScreen";
import { screenById } from "../registry.generated";

export default function GastroenterologyAiAssist() {
  return <AiAssistScreen screen={screenById("gastroenterology:ia")!} />;
}
