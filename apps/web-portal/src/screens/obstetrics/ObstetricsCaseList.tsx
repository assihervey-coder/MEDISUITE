/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Obstétrique · Liste des cas cliniques.
 *  Route : /module/obstetrics/cas · service : obstetrics-service (module 10).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseListScreen from "../templates/CaseListScreen";
import { screenById } from "../registry.generated";

export default function ObstetricsCaseList() {
  return <CaseListScreen screen={screenById("obstetrics:cas")!} />;
}
