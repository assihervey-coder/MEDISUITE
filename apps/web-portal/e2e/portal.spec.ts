/** e2e portal — parcours critiques (APIs mockées, aucun backend requis).
 *
 * Scénarios couverts (alignés grille sommative IEC 62366 — scénarios
 * d'interface, pas de validation clinique) :
 * E1 connexion réussie → navigation   E2 connexion refusée (401)
 * E3 dossiers patients (données mok)  E4 changement de langue + RTL arabe
 * E5 déconnexion
 */
import { expect, test, type Page } from "@playwright/test";

const TOKEN = "e2e.fake.token";

/** Routeur de mocks : /api/auth/… → auth, tout le reste → données vides. */
async function mockApis(page: Page, opts?: { loginStatus?: number }) {
  await page.route("**/api/**", async (route) => {
    const url = route.request().url();
    if (url.includes("/api/auth/") && url.includes("/auth/login")) {
      const status = opts?.loginStatus ?? 200;
      const body =
        status === 200
          ? { access_token: TOKEN, role: "medecin" }
          : { detail: "identifiants invalides" };
      return route.fulfill({ status, contentType: "application/json", body: JSON.stringify(body) });
    }
    if (route.request().method() === "GET") {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([]),
      });
    }
    return route.fulfill({ status: 200, contentType: "application/json", body: "{}" });
  });
}

async function login(page: Page) {
  await page.goto("/");
  await page.getByPlaceholder("Email professionnel").fill("medecin@chu-cocody.ci");
  await page.getByPlaceholder("Mot de passe").fill("MediSuite2026!");
  await page.getByRole("button", { name: /Se connecter/ }).click();
}

test("E1 — connexion réussie puis navigation i18n (fr par défaut)", async ({ page }) => {
  await mockApis(page);
  await login(page);
  await expect(page.locator("aside")).toContainText("Tableau de bord");
  await expect(page.locator("aside")).toContainText("Dossiers patients");
  await expect(page.locator("aside")).toContainText("Connecté");
});

test("E2 — identifiants refusés : message d'erreur affiché, pas de session", async ({ page }) => {
  await mockApis(page, { loginStatus: 401 });
  await login(page);
  await expect(page.locator(".error")).toContainText("identifiants invalides");
  await expect(page.getByPlaceholder("Email professionnel")).toBeVisible();
});

test("E3 — dossiers patients : la page charge (mock vide, pas de crash)", async ({ page }) => {
  await mockApis(page);
  await login(page);
  await page.getByRole("link", { name: /Dossiers patients/ }).click();
  await expect(page).toHaveURL(/\/patients/);
  // l'application reste interactive (aucun crash de rendu)
  await expect(page.locator("main")).toBeVisible();
});

test("E4 — changement de langue vers العربية : RTL appliqué au document", async ({ page }) => {
  await mockApis(page);
  await login(page);
  await page.getByLabel("Langue").selectOption({ label: "العربية" });
  await expect(page.locator("html")).toHaveAttribute("dir", "rtl");
  await expect(page.locator("html")).toHaveAttribute("lang", "ar");
  await expect(page.locator("aside")).toContainText("لوحة القيادة");
  // persistance : la préférence survit au rechargement
  await page.reload();
  await expect(page.locator("html")).toHaveAttribute("dir", "rtl");
});

test("E5 — déconnexion : retour à l'écran de connexion", async ({ page }) => {
  await mockApis(page);
  await login(page);
  await page.getByRole("button", { name: /Déconnexion/ }).click();
  await expect(page.getByPlaceholder("Email professionnel")).toBeVisible();
});
