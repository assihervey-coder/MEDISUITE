/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Gynécologie · Vue d'ensemble du module.
 *  Route : /module/gynecology · service : gynecology-service (module 11).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import OverviewScreen from "../templates/OverviewScreen";
import { screenById } from "../registry.generated";

export default function GynecologyOverview() {
  return <OverviewScreen screen={screenById("gynecology:overview")!} />;
}
