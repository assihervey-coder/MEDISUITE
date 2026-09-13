/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Tumeurs · Fiche cas clinique.
 *  Route : /module/tumor/cas/:caseId · service : tumor-service (module 04).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseDetailScreen from "../templates/CaseDetailScreen";
import { screenById } from "../registry.generated";

export default function TumorCaseDetail() {
  return <CaseDetailScreen screen={screenById("tumor:detail")!} />;
}
