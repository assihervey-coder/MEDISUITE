/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Cardiologie · Fiche cas clinique.
 *  Route : /module/cardiology/cas/:caseId · service : cardiology-service (module 08).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseDetailScreen from "../templates/CaseDetailScreen";
import { screenById } from "../registry.generated";

export default function CardiologyCaseDetail() {
  return <CaseDetailScreen screen={screenById("cardiology:detail")!} />;
}
