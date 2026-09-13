/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Radiothérapie · Fiche cas clinique.
 *  Route : /module/radiotherapy/cas/:caseId · service : radiotherapy-service (module 23).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseDetailScreen from "../templates/CaseDetailScreen";
import { screenById } from "../registry.generated";

export default function RadiotherapyCaseDetail() {
  return <CaseDetailScreen screen={screenById("radiotherapy:detail")!} />;
}
