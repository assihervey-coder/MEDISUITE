/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Cardiologie · Liste des cas cliniques.
 *  Route : /module/cardiology/cas · service : cardiology-service (module 08).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseListScreen from "../templates/CaseListScreen";
import { screenById } from "../registry.generated";

export default function CardiologyCaseList() {
  return <CaseListScreen screen={screenById("cardiology:cas")!} />;
}
