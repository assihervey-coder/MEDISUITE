/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Oncologie · Vue d'ensemble du module.
 *  Route : /module/oncology · service : oncology-service (module 03).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import OverviewScreen from "../templates/OverviewScreen";
import { screenById } from "../registry.generated";

export default function OncologyOverview() {
  return <OverviewScreen screen={screenById("oncology:overview")!} />;
}
