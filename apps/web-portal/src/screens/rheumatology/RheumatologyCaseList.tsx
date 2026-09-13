/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Rhumatologie · Liste des cas cliniques.
 *  Route : /module/rheumatology/cas · service : rheumatology-service (module 20).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseListScreen from "../templates/CaseListScreen";
import { screenById } from "../registry.generated";

export default function RheumatologyCaseList() {
  return <CaseListScreen screen={screenById("rheumatology:cas")!} />;
}
