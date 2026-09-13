/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Dermatologie · Assistance IA (non validée — R6-R8).
 *  Route : /module/dermatology/ia · service : dermatology-service (module 18).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import AiAssistScreen from "../templates/AiAssistScreen";
import { screenById } from "../registry.generated";

export default function DermatologyAiAssist() {
  return <AiAssistScreen screen={screenById("dermatology:ia")!} />;
}
