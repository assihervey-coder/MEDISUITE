/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Urologie · Fiche cas clinique.
 *  Route : /module/urology/cas/:caseId · service : urology-service (module 21).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseDetailScreen from "../templates/CaseDetailScreen";
import { screenById } from "../registry.generated";

export default function UrologyCaseDetail() {
  return <CaseDetailScreen screen={screenById("urology:detail")!} />;
}
