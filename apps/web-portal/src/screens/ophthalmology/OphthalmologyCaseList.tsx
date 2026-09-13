/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Ophtalmologie · Liste des cas cliniques.
 *  Route : /module/ophthalmology/cas · service : ophthalmology-service (module 05).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseListScreen from "../templates/CaseListScreen";
import { screenById } from "../registry.generated";

export default function OphthalmologyCaseList() {
  return <CaseListScreen screen={screenById("ophthalmology:cas")!} />;
}
