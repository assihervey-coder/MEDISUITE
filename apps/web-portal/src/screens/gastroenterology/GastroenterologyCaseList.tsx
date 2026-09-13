/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Gastro-entérologie · Liste des cas cliniques.
 *  Route : /module/gastroenterology/cas · service : gastroenterology-service (module 17).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseListScreen from "../templates/CaseListScreen";
import { screenById } from "../registry.generated";

export default function GastroenterologyCaseList() {
  return <CaseListScreen screen={screenById("gastroenterology:cas")!} />;
}
