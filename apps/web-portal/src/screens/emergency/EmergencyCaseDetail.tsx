/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Urgences · Fiche cas clinique.
 *  Route : /module/emergency/cas/:caseId · service : emergency-service (module 26).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseDetailScreen from "../templates/CaseDetailScreen";
import { screenById } from "../registry.generated";

export default function EmergencyCaseDetail() {
  return <CaseDetailScreen screen={screenById("emergency:detail")!} />;
}
