/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Gynécologie · Fiche cas clinique.
 *  Route : /module/gynecology/cas/:caseId · service : gynecology-service (module 11).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseDetailScreen from "../templates/CaseDetailScreen";
import { screenById } from "../registry.generated";

export default function GynecologyCaseDetail() {
  return <CaseDetailScreen screen={screenById("gynecology:detail")!} />;
}
