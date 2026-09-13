/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Anesthésie-Réanimation · Liste des cas cliniques.
 *  Route : /module/anesthesia/cas · service : anesthesia-service (module 24).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseListScreen from "../templates/CaseListScreen";
import { screenById } from "../registry.generated";

export default function AnesthesiaCaseList() {
  return <CaseListScreen screen={screenById("anesthesia:cas")!} />;
}
