# ADR 0022 — Backends de calcul des encodeurs : NumPy par défaut, PyTorch et MONAI optionnels

Statut : accepté (v0.2.0)
Date : 2026-09-13
Décideurs : plateau MEDISUITE
Décisions liées : ADR 0003 (MONAI pour l'IA), ADR 0016-0019 (fusion), ADR 0021 (audit chaîné)

## Contexte

Le moteur de fusion multimodale v0.1 est implémenté en NumPy pur : projection
statique déterministe des tokens (graine dérivée du nom de modalité),
cross-attention, gated fusion et têtes de tâche. Ce choix garantit une chaîne
de tests reproductible sans dépendances lourdes (373 tests verts, aucune
installation GPU), conforme à l'exigence IEC 62304 de validation sur
environnement maîtrisé.

En revanche, l'entraînement réel (v0.2+) exige des tenseurs différentsiables :
PyTorch est le standard du domaine médical et MONAI (ADR 0003) fournit les
transforms d'imagerie canoniques (EnsureChannelFirst, ScaleIntensity, Resize)
ainsi que les bundles pré-entraînés. La question était donc : basculer le
moteur entier sur PyTorch, ou conserver NumPy comme socle par défaut ?

## Décision

1. **NumPy reste le backend par défaut** du moteur de fusion : aucune
   dépendance lourde n'est requise pour exécuter le moteur, les tests ou les
   26 configurations de modules. Le comportement v0.1 est figé (régression).
2. **Point d'injection unique** : la méthode `BaseEncoder.project(tokens)`
   remplace l'expression `tokens @ P` — c'est le seul point où un backend peut
   substituer une projection entraînable. Le reste du pipeline (attention,
   fusion, têtes) reste NumPy en v0.2.
3. **Backend `torch`** : `TorchProjector` enveloppe un `torch.nn.Linear`
   (biais désactivé, float64) dont les poids sont **copiés depuis la matrice
   stable P** du socle NumPy. À l'initialisation, la sortie est numériquement
   identique au socle NumPy (tolérance 1e-6) : les tests de régression v0.1
   restent valides après branchement, et l'entraînement reprend depuis un
   état connu. Toute divergence n'apparaît qu'à la première mise à jour de
   gradient — exactement le comportement attendu.
4. **Backend `monai`** : ajoute au branchement torch un prétraitement MONAI
   canonique inséré dans la tokenisation des encodeurs `imaging_2d` /
   `imaging_3d` (EnsureChannelFirst → ScaleIntensity → Resize 64×64 ou
   32×32×32), rendant l'entrée indépendante de l'acquisition.
5. **Sélection par configuration** : clé YAML `backend: numpy|torch|monai`
   dans les 26 configurations de modules, interprétée par la factory. Import
   paresseux : torch/monai ne sont importés que si un backend explicite est
   demandé ; l'absence de dépendance produit une `ImportError` documentée avec
   la commande d'installation, jamais un crash différé.
6. **Traçabilité** : `backend_of(engine)` expose le backend branché ; le
   résultat d'inférence enregistre le backend utilisé (exigence model cards).

## Conséquences

Positives :
- La certification du socle NumPy (v0.1) reste valable : le chemin par défaut
  n'a pas changé d'un octet de sémantique.
- Passage progressif module par module : une config YAML par module décide de
  son backend — pas de big-bang.
- Équivalence numérique initiale torch/NumPy testée : filet de régression
  permanent entre les deux représentations.

Négatives / limites :
- Seule la projection est entraînable en v0.2 ; l'attention et la gated fusion
  passent à torch en v0.3 (besoin de gradients sur tout le graphe).
- float64 côté torch à l'init : coût mémoire ×2, assumé pour l'équivalence ;
  l'entraînement passera en float32 + AMP avec tests d'équivalence dédiés.
- MONAI impose une version de torch compatible : épinglage dans
  ai/requirements.txt, vérifié en CI (workflow ai-tests).

## Alternatives écartées

- **Tout-PyTorch immédiat** : casse la chaîne de tests sans dépendances,
  contredit l'exigence de validation IEC 62304 sur environnement maîtrisé, et
  rendrait le moteur inutilisable sur les postes de revue sans GPU.
- **ONNX Runtime comme backend unique** : adapté au déploiement (KServe,
  ADR 0013), inadapté à l'entraînement ; retenu pour la phase de serving,
  pas pour la fabrique de modèles.
- **Deux moteurs parallèles (numpy + torch)** : duplication de la logique de
  fusion — risque de divergence sémantique, rejeté au profit du point
  d'injection unique.
