/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Cardiologie · Vue d'ensemble du module.
 *  Route : /module/cardiology · service : cardiology-service (module 08).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import OverviewScreen from "../templates/OverviewScreen";
import { screenById } from "../registry.generated";

export default function CardiologyOverview() {
  return <OverviewScreen screen={screenById("cardiology:overview")!} />;
}
