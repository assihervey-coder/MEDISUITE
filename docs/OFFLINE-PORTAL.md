# Mode offline du web-portal (v0.7.0)

> Objectif : la saisie clinique ne doit JAMAIS être bloquée par une coupure
> réseau — réalité opérationnelle des sites CHU (§8 protocole CI-01 :
> « panne site > 24 h » est un critère pré-spécifié du protocole).

## Architecture

```
web-portal
├─ public/sw.js                    service worker (build PROD uniquement)
│   ├─ navigations SPA             : réseau d'abord → repli cache shell
│   ├─ GET /api/*                  : réseau d'abord → cache runtime (repli
│   │                                lecture hors-ligne des dernières réponses)
│   └─ autres GET (assets)         : stale-while-revalidate
│   ⚠ non-GET jamais interceptés : les mutations passent par la file
│
└─ src/offline/
    ├─ rules.ts        règles pures (back-off 1 s→30 s, 4xx définitifs,
    │                   clé d'idempotence) — testées (vitest)
    ├─ db.ts           IndexedDB : store "pending" (FIFO) + "dead" (rejets)
    ├─ queue.ts        empilement + rejeu idempotent (Idempotency-Key)
    ├─ offlineStore.ts état zustand (online, pending, dead, syncing)
    └─ sync.ts         boucle : événements online/offline + rejeu 30 s
```

## Flux d'une saisie hors-ligne

1. L'utilisateur soumet un formulaire eCRF (`submitWithQueue` dans
   `services/api.ts`) ; `navigator.onLine === false`.
2. L'opération est persistée dans IndexedDB avec une clé d'idempotence
   client (UUID) et un reçu s'affiche immédiatement (« empilée hors-ligne »).
3. La bannière (`OfflineBanner`, fixe en haut) montre l'état :
   hors-ligne (ambre), N saisies en attente (bleu), bouton « Synchroniser
   maintenant », rejets à inspecter.
4. Au retour du réseau (événement `online` ou cycle de 30 s), `replayAll()`
   rejoue chaque opération avec `Idempotency-Key` ; le serveur eCRF
   dédoublonne AUSSI par clé calculée (SHA-256 du payload canonique —
   `medisuite_core/ecrf.py`), donc **aucun doublon possible**, même si la
   clé client était perdue.
5. Sorties par opération : succès → retirée de la file ; 4xx hors 408/429
   → « dead letter » inspectable ; erreur réseau/5xx → conservée, back-off
   exponentiel plafonné à 30 s.

## Ce que le mode offline NE couvre PAS (honnêteté)

- La **lecture** hors-ligne ne sert que ce qui a déjà été consulté en ligne
  (cache HTTP du service worker) — pas de synchronisation complète des
  sujets/entrées en local.
- La création de sujets hors-ligne est possible via la file, mais la
  numérotation séquentielle est assignée par le serveur au rejeu (pas de
  réservation locale de numéro — évite les collisions entre sites).
- Le service worker n'est actif qu'en build de production (`import.meta.env.PROD`)
  pour ne pas perturber le HMR Vite en développement ; la file IndexedDB,
  elle, fonctionne aussi en dev.
- Pas de chiffrement local de la file : IndexedDB est lisible par toute
  page du même origine. Le contenu est pseudonymisé par construction
  (codes CI01-…, jamais de nom) — cohérent avec §6 du protocole. Un
  chiffrement local (WebCrypto + clé session) est un renforcement
  envisagé avant R6 si le DPIA site l'exige.

## Vérifications

- `tsc -b` strict + build Vite : verts.
- `npm test` (vitest) : 5 tests sur les règles pures (back-off, rejets
  4xx, unicité des clés).
- Le rejeu de bout en bout est testé côté serveur
  (`services/ecrf-service/tests/test_ecrf_service.py::test_sync_lot_mixte_et_rejeu`)
  : rejeu intégral d'un lot → `created: 0, duplicate: 2`.
