/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Dermatologie · Vue d'ensemble du module.
 *  Route : /module/dermatology · service : dermatology-service (module 18).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import OverviewScreen from "../templates/OverviewScreen";
import { screenById } from "../registry.generated";

export default function DermatologyOverview() {
  return <OverviewScreen screen={screenById("dermatology:overview")!} />;
}
