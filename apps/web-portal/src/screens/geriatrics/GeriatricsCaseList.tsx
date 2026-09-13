/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Gériatrie · Liste des cas cliniques.
 *  Route : /module/geriatrics/cas · service : geriatrics-service (module 25).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseListScreen from "../templates/CaseListScreen";
import { screenById } from "../registry.generated";

export default function GeriatricsCaseList() {
  return <CaseListScreen screen={screenById("geriatrics:cas")!} />;
}
