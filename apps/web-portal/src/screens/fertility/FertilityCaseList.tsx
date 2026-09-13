/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Fertilité · Liste des cas cliniques.
 *  Route : /module/fertility/cas · service : fertility-service (module 12).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseListScreen from "../templates/CaseListScreen";
import { screenById } from "../registry.generated";

export default function FertilityCaseList() {
  return <CaseListScreen screen={screenById("fertility:cas")!} />;
}
