/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Psychiatrie · Vue d'ensemble du module.
 *  Route : /module/psychiatry · service : psychiatry-service (module 14).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import OverviewScreen from "../templates/OverviewScreen";
import { screenById } from "../registry.generated";

export default function PsychiatryOverview() {
  return <OverviewScreen screen={screenById("psychiatry:overview")!} />;
}
