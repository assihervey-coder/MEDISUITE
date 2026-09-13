/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Traumatologie · Liste des cas cliniques.
 *  Route : /module/traumatology/cas · service : traumatology-service (module 07).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseListScreen from "../templates/CaseListScreen";
import { screenById } from "../registry.generated";

export default function TraumatologyCaseList() {
  return <CaseListScreen screen={screenById("traumatology:cas")!} />;
}
