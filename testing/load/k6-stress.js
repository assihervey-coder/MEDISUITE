/** k6 — stress progressif : charge montée en paliers (v0.12).
 *
 * Usage :
 *   k6 run -e BASE_URL=http://localhost:8000 -e TOKEN=... testing/load/k6-stress.js
 *
 * Profil : 10 → 50 → 100 VU avec paliers de 2 min ; seuils EGSP (p95 ≤ 2 s)
 * avec dégradation observée plutôt qu'abort (mesure de capacité CHU).
 * Le token optionnel permet de charger des endpoints authentifiés ; sans
 * token, la charge porte sur la santé et les routes publiques (_about,
 * registry) — jamais sur des données patient réelles.
 */
import http from "k6/http";
import { check, group, sleep } from "k6";

const BASE = __ENV.BASE_URL || "http://localhost:8000";
const TOKEN = __ENV.TOKEN || "";

export const options = {
  stages: [
    { duration: "2m", target: 10 },
    { duration: "2m", target: 50 },
    { duration: "2m", target: 100 },
    { duration: "1m", target: 10 },
  ],
  thresholds: {
    http_req_failed: ["rate<0.05"], // dégradation tolérée au pic, mesurée
    http_req_duration: ["p(95)<2000"], // EGSP dossier CE §4
  },
};

function authHeaders() {
  return TOKEN
    ? { headers: { Authorization: `Bearer ${TOKEN}`, "Content-Type": "application/json" } }
    : { headers: { "Content-Type": "application/json" } };
}

export default function () {
  group("santé — liveness sous charge", () => {
    const health = http.get(`${BASE}/health/all`);
    check(health, { "health 200": (r) => r.status === 200 });
  });

  group("lecture publique — registry services", () => {
    const reg = http.get(`${BASE}/api/v1/registry`, authHeaders());
    check(reg, {
      "registry 2xx/401/403": (r) => [200, 401, 403].includes(r.status),
    });
  });

  if (TOKEN) {
    group("lecture authentifiée — patients (page 1)", () => {
      const patients = http.get(`${BASE}/api/v1/patients?limit=20`, authHeaders());
      check(patients, {
        "patients 2xx": (r) => r.status >= 200 && r.status < 300,
        "patients p95 EGSP": (r) => r.timings.duration < 2000,
      });
    });
  }

  sleep(0.5);
}
