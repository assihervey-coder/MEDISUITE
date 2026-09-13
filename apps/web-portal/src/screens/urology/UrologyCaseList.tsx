/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Urologie · Liste des cas cliniques.
 *  Route : /module/urology/cas · service : urology-service (module 21).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseListScreen from "../templates/CaseListScreen";
import { screenById } from "../registry.generated";

export default function UrologyCaseList() {
  return <CaseListScreen screen={screenById("urology:cas")!} />;
}
