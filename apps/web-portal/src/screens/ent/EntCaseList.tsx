/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : ORL · Liste des cas cliniques.
 *  Route : /module/ent/cas · service : ent-service (module 19).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseListScreen from "../templates/CaseListScreen";
import { screenById } from "../registry.generated";

export default function EntCaseList() {
  return <CaseListScreen screen={screenById("ent:cas")!} />;
}
