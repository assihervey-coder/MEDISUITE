/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Dermatologie · Liste des cas cliniques.
 *  Route : /module/dermatology/cas · service : dermatology-service (module 18).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseListScreen from "../templates/CaseListScreen";
import { screenById } from "../registry.generated";

export default function DermatologyCaseList() {
  return <CaseListScreen screen={screenById("dermatology:cas")!} />;
}
