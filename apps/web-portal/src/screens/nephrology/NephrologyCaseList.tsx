/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Néphrologie · Liste des cas cliniques.
 *  Route : /module/nephrology/cas · service : nephrology-service (module 16).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseListScreen from "../templates/CaseListScreen";
import { screenById } from "../registry.generated";

export default function NephrologyCaseList() {
  return <CaseListScreen screen={screenById("nephrology:cas")!} />;
}
