/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Traumatologie · Fiche cas clinique.
 *  Route : /module/traumatology/cas/:caseId · service : traumatology-service (module 07).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseDetailScreen from "../templates/CaseDetailScreen";
import { screenById } from "../registry.generated";

export default function TraumatologyCaseDetail() {
  return <CaseDetailScreen screen={screenById("traumatology:detail")!} />;
}
