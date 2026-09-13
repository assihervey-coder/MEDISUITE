/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Neurologie · Fiche cas clinique.
 *  Route : /module/neurology/cas/:caseId · service : neurology-service (module 13).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseDetailScreen from "../templates/CaseDetailScreen";
import { screenById } from "../registry.generated";

export default function NeurologyCaseDetail() {
  return <CaseDetailScreen screen={screenById("neurology:detail")!} />;
}
