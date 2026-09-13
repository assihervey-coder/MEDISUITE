/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Oncologie · Liste des cas cliniques.
 *  Route : /module/oncology/cas · service : oncology-service (module 03).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseListScreen from "../templates/CaseListScreen";
import { screenById } from "../registry.generated";

export default function OncologyCaseList() {
  return <CaseListScreen screen={screenById("oncology:cas")!} />;
}
