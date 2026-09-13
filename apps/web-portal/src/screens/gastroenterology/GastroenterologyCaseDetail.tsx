/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Gastro-entérologie · Fiche cas clinique.
 *  Route : /module/gastroenterology/cas/:caseId · service : gastroenterology-service (module 17).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseDetailScreen from "../templates/CaseDetailScreen";
import { screenById } from "../registry.generated";

export default function GastroenterologyCaseDetail() {
  return <CaseDetailScreen screen={screenById("gastroenterology:detail")!} />;
}
