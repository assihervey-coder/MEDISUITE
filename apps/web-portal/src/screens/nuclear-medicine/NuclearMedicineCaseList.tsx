/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Médecine nucléaire · Liste des cas cliniques.
 *  Route : /module/nuclear-medicine/cas · service : nuclear-medicine-service (module 22).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseListScreen from "../templates/CaseListScreen";
import { screenById } from "../registry.generated";

export default function NuclearMedicineCaseList() {
  return <CaseListScreen screen={screenById("nuclear-medicine:cas")!} />;
}
