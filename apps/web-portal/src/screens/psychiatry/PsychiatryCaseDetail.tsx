/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Psychiatrie · Fiche cas clinique.
 *  Route : /module/psychiatry/cas/:caseId · service : psychiatry-service (module 14).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseDetailScreen from "../templates/CaseDetailScreen";
import { screenById } from "../registry.generated";

export default function PsychiatryCaseDetail() {
  return <CaseDetailScreen screen={screenById("psychiatry:detail")!} />;
}
