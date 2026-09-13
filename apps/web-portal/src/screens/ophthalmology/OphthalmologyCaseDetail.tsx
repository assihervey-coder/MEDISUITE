/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Ophtalmologie · Fiche cas clinique.
 *  Route : /module/ophthalmology/cas/:caseId · service : ophthalmology-service (module 05).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseDetailScreen from "../templates/CaseDetailScreen";
import { screenById } from "../registry.generated";

export default function OphthalmologyCaseDetail() {
  return <CaseDetailScreen screen={screenById("ophthalmology:detail")!} />;
}
