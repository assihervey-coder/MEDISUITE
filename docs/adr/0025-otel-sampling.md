# ADR-0025 — Échantillonnage OTel (head sampling déterministe parent-based)

**Statut** : accepté (v0.8) · **Date** : 2026-09-14 · **Décideurs** : ingénierie + direction
**Supersede** : complète ADR-0012 (observabilité native) et la v0.4 du middleware OTel

## Contexte

La v0.4 instrumente les 38 services (spans serveur W3C, export OTLP/HTTP
JSON vers le collecteur). Trois constats de production hospitalière :

1. **Volume** : chaque service émet un span par requête HTTP. Les sondes
   K8s/compose (`/health`, `/ready`) tirent à haute fréquence sur 39
   services : elles écrasent le tampon (2 048 spans) de traces métier
   sans aucune valeur diagnostique.
2. **Coût d'ingestion** : le collecteur OTLP → Prometheus ; à l'échelle
   (600 sujets × 6 formulaires × 2×3 CHU + trafic clinique de 26 modules),
   tout garder 100 % du temps est inutile : 99 % des requêtes nominales se
   ressemblent, l'incident est rare mais précieux.
3. **Cohérence de trace** : un échantillonnage aléatoire indépendant par
   service casserait les traces distribuées (moitié d'une trace ici, moitié
   là) — la valeur première du tracing est justement la trace complète.

## Décision

**Head sampling déterministe, parent-based, always-on errors** — implémenté
dans `medisuite_core.observability` (aucune dépendance ajoutée) :

1. **Décision à la création du span** (`Tracer.start_server_span`) :
   - parent W3C valide → sa décision prévaut (bit 0 des flags, autres bits
     réservés) : `parent_sampled` / `parent_unsampled` (sémantique
     `ParentBased` standard OTel — pas d'implémentation maison divergente) ;
   - racine → ratio déterministe sur le trace_id : les 16 premiers hex
     comparés à `ratio × 2^64`. Même trace_id ⇒ même décision **sans
     coordination inter-services** : les traces restent complètes ou
     absentes, jamais coupées.
2. **Ratio** : env `MEDISUITE_OTEL_SAMPLING_RATIO` (défaut **1.0** — en
   investigation clinique, la télémétrie complète est requise ; 0.1 est
   recommandé en production courante après R6). Valeur invalide → 1.0
   (fail-open assumé : une erreur de config ne doit pas supprimer la
   télémétrie).
3. **Always-on errors** : un span terminé en erreur (5xx/exception) est
   TOUJOURS enregistré et exporté, même non échantillonné. Un incident
   n'est jamais « échantillonné hors » des données.
4. **Routes de bruit** : `/health`, `/ready`, `/metrics` ne créent plus de
   span (constantes `NOISE_ROUTES`) ; les headers de corrélation
   `X-Request-ID`/`X-Service-Name` restent émis.
5. **Propagation honnête** : la réponse réémet `traceparent` avec flags
   `01`/`00` selon la décision — les services aval ne rééchantillonnent pas
   contre la décision amont.
6. **Observabilité du sampler lui-même** : attribut `otel.sampling.decision`
   sur chaque span créé, champs `sampling_ratio`/`sampling_dropped` dans
   `snapshot()` — le taux réel d'échantillonnage est mesurable, pas supposé.

## Alternatives écartées

- **Tail sampling au collecteur** (décision après la trace complète,
  garder les traces lentes/erronées) : supérieure en théorie, mais exige
  de bufferiser 100 % du trafic dans le collecteur + un fichier de
  politiques — complexité opérationnelle injustifiée avant R6 ; réévaluable
  dans l'ADR quand le volume réel (campagne GPU CHU) sera mesuré.
- **SDK OTel Python officiel** : déjà écarté en ADR-0012 (contrainte
  stdlib d'abord, empreinte d'exécution) — le sampling parent-based est un
  algorithme de 15 lignes, pas une raison de revenir sur cette décision.
- **Ratio aléatoire non déterministe** : casse la complétude des traces
  distribuées (raison 3 du contexte).
- **Pas de sampling** (garder 1.0) : viable en investigation, insoutenable
  en production courante multi-CHU ( raison 2).

## Conséquences

- ✔ Traces distribuées complètes (décision unique par trace_id, propagée).
- ✔ Erreurs toujours visibles (always-on) — le diagnostic d'incident ne
  dépend pas du hasard.
- ✔ Probes exclues : le tampon 2 048 reste disponible pour le métier.
- ⚠ Les traces non échantillonnées ne sont **nulle part** (ni tampon, ni
  collecteur) : c'est le but, mais le ratio doit rester 1.0 pendant
  l'investigation R6 (validité clinique) — règle d'exploitation notée dans
  `docs/OTEL.md`.
- ⚠ Les spans mémoire créés puis non enregistrés coûtent une allocation
  triviale (decisión head) — négligeable, mesuré à < 1 µs en banc interne.
- Testé : 8 cas (décision parent bit 0, ratio 0.0/1.0, déterminisme,
  always-on error, routes de bruit, propagation flags, fail-open env).
