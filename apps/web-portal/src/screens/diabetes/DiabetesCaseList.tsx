/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Diabétologie · Liste des cas cliniques.
 *  Route : /module/diabetes/cas · service : diabetes-service (module 06).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseListScreen from "../templates/CaseListScreen";
import { screenById } from "../registry.generated";

export default function DiabetesCaseList() {
  return <CaseListScreen screen={screenById("diabetes:cas")!} />;
}
