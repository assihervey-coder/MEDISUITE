/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Urgences · Liste des cas cliniques.
 *  Route : /module/emergency/cas · service : emergency-service (module 26).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseListScreen from "../templates/CaseListScreen";
import { screenById } from "../registry.generated";

export default function EmergencyCaseList() {
  return <CaseListScreen screen={screenById("emergency:cas")!} />;
}
