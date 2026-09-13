/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Pneumologie · Liste des cas cliniques.
 *  Route : /module/pneumology/cas · service : pneumology-service (module 09).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseListScreen from "../templates/CaseListScreen";
import { screenById } from "../registry.generated";

export default function PneumologyCaseList() {
  return <CaseListScreen screen={screenById("pneumology:cas")!} />;
}
