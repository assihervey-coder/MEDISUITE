/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Rhumatologie · Vue d'ensemble du module.
 *  Route : /module/rheumatology · service : rheumatology-service (module 20).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import OverviewScreen from "../templates/OverviewScreen";
import { screenById } from "../registry.generated";

export default function RheumatologyOverview() {
  return <OverviewScreen screen={screenById("rheumatology:overview")!} />;
}
