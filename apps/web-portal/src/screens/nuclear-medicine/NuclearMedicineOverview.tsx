/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Médecine nucléaire · Vue d'ensemble du module.
 *  Route : /module/nuclear-medicine · service : nuclear-medicine-service (module 22).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import OverviewScreen from "../templates/OverviewScreen";
import { screenById } from "../registry.generated";

export default function NuclearMedicineOverview() {
  return <OverviewScreen screen={screenById("nuclear-medicine:overview")!} />;
}
