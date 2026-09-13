# ADR 0023 — Fusion torch entraînable de bout en bout (attention + gated)

Statut : accepté (v0.3.0)
Date : 2026-09-13
Décideurs : plateau MEDISUITE
Décisions liées : ADR 0003 (MONAI), ADR 0016-0019 (fusion), ADR 0022 (backends
encodeurs), audit §5 (données appariées introuvables)

## Contexte

En v0.2 (ADR 0022), seul le point `BaseEncoder.project()` était entraînable :
la cross-attention, les portes sigmoid, la requête globale et les têtes de
tâche restaient des gabarits NumPy déterministes (graines fixes). Le moteur
réalisait donc de l'**inférence** résiliente, mais aucune mise à jour de
poids n'était possible : le « moteur d'IA » ne pouvait pas apprendre.

La v0.3 doit permettre l'entraînement réel (gradient descent) du tronc de
fusion complet sans casser :
- les tests de régression v0.1/0.2 (le socle NumPy reste la référence
  exécutable sans torch — exigence IEC 62304 de chaîne de test maîtrisée) ;
- l'explicabilité (importance des modalités, ADR-0015) ;
- la gestion des modalités manquantes (ADR-0018, confiance recalibrée) ;
- la reproductibilité clinique (même entrée → même sortie, zéro RNG).

## Décision

1. **`TorchFusionModel` (nn.Module) — tronc complet entraînable** :
   projections (`nn.Linear` par modalité, poids copiés de `P`), attention
   croisée **multi-têtes** (`TorchCrossAttention`, Wq/Wk/Wv/Wo en float64),
   **portes sigmoid `nn.Parameter`** par modalité, **requête globale apprise**
   (token [CLS] de fait) et **tête de tâche entraînable**
   (`TorchTaskHead` : binaire sigmoid / multiclasse softmax / régression).

2. **Équivalence numérique à l'initialisation** (extension du pattern ADR
   0022) : tous les paramètres sont copiés depuis les poids déterministes
   NumPy v0.1 — à construction, `predict()` ≡ `infer()` (Δ probabilité = 0,
   testé rtol 1e-6 au niveau du tenseur `fused`). La divergence n'arrive que
   par entraînement explicite : le backend torch est un **sur-ensemble**
   du socle, jamais un remplacement.

3. **Frontière d'apprentissage explicite** :
   - GELÉ : tokenisation (`BaseEncoder._to_tokens`) — extraction déterministe
     auditable, pré-calculée une fois dans `fit()` ;
   - ENTRAÎNABLE : projections, attention, portes, requête, tête.
   Les blocs des modalités **absentes** d'un échantillon ne reçoivent pas de
   gradient (gradient épars, cohérent avec ADR-0018).

4. **`fit()` déterministe** : Adam, ordre d'échantillons fixe (aucun shuffle),
   float64 intégral, perte par tâche (BCE-with-logits / cross-entropy / MSE),
   historique des pertes retourné. Zéro RNG : aucun paramètre initialisé
   aléatoirement — deux fits identiques donnent des historiques identiques
   (testé).

5. **Multi-têtes honnête** : avec `heads=1`, le calcul torch est
   mathématiquement identique au bloc NumPy (échelle √d). Avec `heads=h>1`,
   les scores par tête utilisent l'échelle standard √(d/h) — divergence
   voulue et documentée (valeur ajoutée du backend).

6. **Persistance native** : `save()`/`load_checkpoint()` sur `state_dict`
   torch + métadonnées (`format: medisuite-fusion-0.3`, tâche, têtes,
   modalités) — round-trip bit-à-bit testé ; prêt pour MLflow (ADR 0003).

7. **Périmètre des tâches** : `classification`, `multiclass`, `regression`
   entraînables ; `survival` / `segmentation` restent des gabarits NumPy
   (rejet `NotImplementedError` explicite) — pas de promesse non tenue.

8. **Socle NumPy inchangé** : `FusionEngine.infer()` reste la référence
   par défaut, exécutable et testable sans torch ; `torch_fusion.py` n'est
   importé que via `factory.fusion_model_from_config()` / `_for_module()`
   (import paresseux).

## Conséquences

- Le moteur peut désormais être entraîné dès qu'un jeu de données apparié
  existe — l'audit a confirmé leur absence (§5) : la démonstration
  d'apprentissage est faite sur synthétique (accuracy 100 %, perte
  décroissante, déterminisme) et le code est prêt pour les données réelles
  v0.4+.
- Les portes apprises modifient l'importance des modalités au fil de
  l'entraînement : l'explicabilité affiche des poids APPRIS (traçables par
  checkpoint) au lieu du gabarit fixe — gain clinique direct.
- Le coût : torch devient requis pour `fusion_model_*` (CPU suffit, float64 ;
  d_model 32 → quelques milliers de paramètres, entraînable sur un ordinateur
  de bureau) ; aucune dépendance ajoutée au socle.

## Alternatives écartées

- **Réécrire FusionEngine en torch uniquement** : casse la chaîne de tests
  sans dépendances et l'audit trail IEC 62304 — écarté (ADR 0022 déjà tranché).
- **Entraîner aussi les tokenizers** : les tokenizers sont des extracteurs
  déterministes documentés (hashing, patchs, z-score) ; les rendre
  paramétriques complexifierait l'auditabilité sans besoin clinique démontré
  à ce stade — reporté à la v0.4 (encoders conv/transformer MONAI).
- **Optimiseur SGD simple** : Adam requis pour la convergence stable du tronc
  attentionné en float64 (SGD testé, perte plate) — Adam retenu.
