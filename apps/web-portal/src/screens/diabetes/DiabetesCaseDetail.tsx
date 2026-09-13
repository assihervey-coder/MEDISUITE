/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Diabétologie · Fiche cas clinique.
 *  Route : /module/diabetes/cas/:caseId · service : diabetes-service (module 06).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseDetailScreen from "../templates/CaseDetailScreen";
import { screenById } from "../registry.generated";

export default function DiabetesCaseDetail() {
  return <CaseDetailScreen screen={screenById("diabetes:detail")!} />;
}
