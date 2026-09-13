/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Rhumatologie · Assistance IA (non validée — R6-R8).
 *  Route : /module/rheumatology/ia · service : rheumatology-service (module 20).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import AiAssistScreen from "../templates/AiAssistScreen";
import { screenById } from "../registry.generated";

export default function RheumatologyAiAssist() {
  return <AiAssistScreen screen={screenById("rheumatology:ia")!} />;
}
