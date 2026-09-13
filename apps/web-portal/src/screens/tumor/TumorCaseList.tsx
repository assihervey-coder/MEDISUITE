/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Tumeurs · Liste des cas cliniques.
 *  Route : /module/tumor/cas · service : tumor-service (module 04).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseListScreen from "../templates/CaseListScreen";
import { screenById } from "../registry.generated";

export default function TumorCaseList() {
  return <CaseListScreen screen={screenById("tumor:cas")!} />;
}
