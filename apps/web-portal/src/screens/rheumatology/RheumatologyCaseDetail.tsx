/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Rhumatologie · Fiche cas clinique.
 *  Route : /module/rheumatology/cas/:caseId · service : rheumatology-service (module 20).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseDetailScreen from "../templates/CaseDetailScreen";
import { screenById } from "../registry.generated";

export default function RheumatologyCaseDetail() {
  return <CaseDetailScreen screen={screenById("rheumatology:detail")!} />;
}
