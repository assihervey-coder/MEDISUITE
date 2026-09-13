/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Gériatrie · Fiche cas clinique.
 *  Route : /module/geriatrics/cas/:caseId · service : geriatrics-service (module 25).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseDetailScreen from "../templates/CaseDetailScreen";
import { screenById } from "../registry.generated";

export default function GeriatricsCaseDetail() {
  return <CaseDetailScreen screen={screenById("geriatrics:detail")!} />;
}
