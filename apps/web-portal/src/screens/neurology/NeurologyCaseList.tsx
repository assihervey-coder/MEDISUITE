/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Neurologie · Liste des cas cliniques.
 *  Route : /module/neurology/cas · service : neurology-service (module 13).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseListScreen from "../templates/CaseListScreen";
import { screenById } from "../registry.generated";

export default function NeurologyCaseList() {
  return <CaseListScreen screen={screenById("neurology:cas")!} />;
}
