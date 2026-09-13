/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Oncologie · Fiche cas clinique.
 *  Route : /module/oncology/cas/:caseId · service : oncology-service (module 03).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseDetailScreen from "../templates/CaseDetailScreen";
import { screenById } from "../registry.generated";

export default function OncologyCaseDetail() {
  return <CaseDetailScreen screen={screenById("oncology:detail")!} />;
}
