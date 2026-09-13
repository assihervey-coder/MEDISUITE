/* Service worker MEDISUITE (v0.7) — mode offline du web-portal.
 *
 * Stratégies :
 * - navigations (SPA)          : réseau d'abord, repli cache "/" (shell)
 * - GET /api/*                 : réseau d'abord, copie en cache RUNTIME,
 *                                repli cache (consultation hors-ligne)
 * - autres GET same-origin     : stale-while-revalidate (assets hashés)
 * - non-GET (POST/PATCH…)      : JAMAIS interceptés ici — la file d'attente
 *                                applicative (src/offline/queue.ts) les gère
 *                                avec clé d'idempotence côté eCRF.
 * L'installation est volontairement réservée au build de production
 * (main.tsx) pour ne pas gêner le HMR en développement.
 */
const SHELL_CACHE = "medisuite-shell-v0.7.0";
const RUNTIME_CACHE = "medisuite-runtime-v0.7.0";
const SHELL_ASSETS = ["/", "/index.html"];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(SHELL_CACHE).then((cache) => cache.addAll(SHELL_ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(
          keys
            .filter((k) => k !== SHELL_CACHE && k !== RUNTIME_CACHE)
            .map((k) => caches.delete(k))
        )
      )
      .then(() => self.clients.claim())
  );
});

async function networkFirst(request, runtimeOnly) {
  const cache = await caches.open(runtimeOnly ? RUNTIME_CACHE : SHELL_CACHE);
  try {
    const fresh = await fetch(request);
    if (fresh && fresh.ok && fresh.type === "basic") {
      cache.put(request, fresh.clone());
    }
    return fresh;
  } catch (err) {
    const cached = await cache.match(request);
    if (cached) return cached;
    throw err;
  }
}

async function staleWhileRevalidate(request) {
  const cache = await caches.open(RUNTIME_CACHE);
  const cached = await cache.match(request);
  const refresh = fetch(request)
    .then((fresh) => {
      if (fresh && fresh.ok && fresh.type === "basic") cache.put(request, fresh.clone());
      return fresh;
    })
    .catch(() => cached);
  return cached || refresh;
}

self.addEventListener("fetch", (event) => {
  const { request } = event;
  if (request.method !== "GET") return; // mutations : file applicative
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  if (request.mode === "navigate") {
    event.respondWith(
      networkFirst(request, false).catch(() => caches.match("/index.html"))
    );
    return;
  }
  if (url.pathname.startsWith("/api/")) {
    event.respondWith(networkFirst(request, true));
    return;
  }
  event.respondWith(staleWhileRevalidate(request));
});
