/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Traumatologie · Vue d'ensemble du module.
 *  Route : /module/traumatology · service : traumatology-service (module 07).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import OverviewScreen from "../templates/OverviewScreen";
import { screenById } from "../registry.generated";

export default function TraumatologyOverview() {
  return <OverviewScreen screen={screenById("traumatology:overview")!} />;
}
