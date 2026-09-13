/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Néphrologie · Fiche cas clinique.
 *  Route : /module/nephrology/cas/:caseId · service : nephrology-service (module 16).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseDetailScreen from "../templates/CaseDetailScreen";
import { screenById } from "../registry.generated";

export default function NephrologyCaseDetail() {
  return <CaseDetailScreen screen={screenById("nephrology:detail")!} />;
}
