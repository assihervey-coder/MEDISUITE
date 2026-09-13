/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Pédiatrie · Liste des cas cliniques.
 *  Route : /module/pediatrics/cas · service : pediatrics-service (module 15).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseListScreen from "../templates/CaseListScreen";
import { screenById } from "../registry.generated";

export default function PediatricsCaseList() {
  return <CaseListScreen screen={screenById("pediatrics:cas")!} />;
}
