/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Gynécologie · Liste des cas cliniques.
 *  Route : /module/gynecology/cas · service : gynecology-service (module 11).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseListScreen from "../templates/CaseListScreen";
import { screenById } from "../registry.generated";

export default function GynecologyCaseList() {
  return <CaseListScreen screen={screenById("gynecology:cas")!} />;
}
