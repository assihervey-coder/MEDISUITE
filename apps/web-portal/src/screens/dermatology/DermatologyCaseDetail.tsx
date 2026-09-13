/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Dermatologie · Fiche cas clinique.
 *  Route : /module/dermatology/cas/:caseId · service : dermatology-service (module 18).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseDetailScreen from "../templates/CaseDetailScreen";
import { screenById } from "../registry.generated";

export default function DermatologyCaseDetail() {
  return <CaseDetailScreen screen={screenById("dermatology:detail")!} />;
}
