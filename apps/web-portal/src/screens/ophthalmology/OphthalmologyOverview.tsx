/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Ophtalmologie · Vue d'ensemble du module.
 *  Route : /module/ophthalmology · service : ophthalmology-service (module 05).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import OverviewScreen from "../templates/OverviewScreen";
import { screenById } from "../registry.generated";

export default function OphthalmologyOverview() {
  return <OverviewScreen screen={screenById("ophthalmology:overview")!} />;
}
