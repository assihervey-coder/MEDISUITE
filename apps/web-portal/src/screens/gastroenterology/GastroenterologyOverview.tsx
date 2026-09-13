/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Gastro-entérologie · Vue d'ensemble du module.
 *  Route : /module/gastroenterology · service : gastroenterology-service (module 17).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import OverviewScreen from "../templates/OverviewScreen";
import { screenById } from "../registry.generated";

export default function GastroenterologyOverview() {
  return <OverviewScreen screen={screenById("gastroenterology:overview")!} />;
}
