/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Urologie · Vue d'ensemble du module.
 *  Route : /module/urology · service : urology-service (module 21).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import OverviewScreen from "../templates/OverviewScreen";
import { screenById } from "../registry.generated";

export default function UrologyOverview() {
  return <OverviewScreen screen={screenById("urology:overview")!} />;
}
