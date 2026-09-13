/** Playwright e2e — MEDISUITE web-portal (v0.12).
 *
 * Stratégie honnête : les parcours UI sont testés avec **APIs mockées par
 * interception** (page.route) — aucun backend requis, le run est déterministe
 * et s'exécute en CI comme en local. Les intégrations réelles (JWT auth-service,
 * Orthanc, eCRF HAPI) sont couvertes par les 39 suites services + 12 tests
 * d'intégration ; le rôle des specs e2e est le PARCOURS utilisateur.
 */
import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  timeout: 30_000,
  fullyParallel: true,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? "github" : "list",
  use: {
    baseURL: "http://localhost:5173",
    trace: "retain-on-failure",
  },
  webServer: {
    command: "npm run dev -- --port 5173 --strictPort",
    url: "http://localhost:5173",
    reuseExistingServer: !process.env.CI,
    timeout: 60_000,
  },
  projects: [{ name: "chromium", use: { browserName: "chromium" } }],
});
