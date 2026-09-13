/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Radiothérapie · Liste des cas cliniques.
 *  Route : /module/radiotherapy/cas · service : radiotherapy-service (module 23).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseListScreen from "../templates/CaseListScreen";
import { screenById } from "../registry.generated";

export default function RadiotherapyCaseList() {
  return <CaseListScreen screen={screenById("radiotherapy:cas")!} />;
}
