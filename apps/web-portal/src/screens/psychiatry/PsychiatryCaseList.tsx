/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Psychiatrie · Liste des cas cliniques.
 *  Route : /module/psychiatry/cas · service : psychiatry-service (module 14).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseListScreen from "../templates/CaseListScreen";
import { screenById } from "../registry.generated";

export default function PsychiatryCaseList() {
  return <CaseListScreen screen={screenById("psychiatry:cas")!} />;
}
