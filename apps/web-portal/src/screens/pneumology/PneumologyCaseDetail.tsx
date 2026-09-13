/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Pneumologie · Fiche cas clinique.
 *  Route : /module/pneumology/cas/:caseId · service : pneumology-service (module 09).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseDetailScreen from "../templates/CaseDetailScreen";
import { screenById } from "../registry.generated";

export default function PneumologyCaseDetail() {
  return <CaseDetailScreen screen={screenById("pneumology:detail")!} />;
}
