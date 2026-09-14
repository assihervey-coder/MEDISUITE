# TropiRAG Terrain — Interface mobile de saisie clinique

PWA **offline-first** (Progressive Web App) conçue pour le terrain ouest-africain :
réseau intermittent, chaleur, une main parfois occupée, batteries faibles.

## Accès

L'interface est servie par l'API TropiRAG :

```
http://<serveur>:8000/mobile/
```

Aucune clé API n'est requise pour charger la page ; la clé (header `X-API-Key`)
se configure dans ⚙ Paramètres et reste **sur l'appareil** (localStorage).

## Installation sur téléphone

1. Ouvrir `/mobile/` dans Chrome / Safari Android ou iOS.
2. Menu → « Ajouter à l'écran d'accueil ».
3. L'app s'ouvre en plein écran (mode standalone), icône TropiRAG.

## Conception terrain

| Contrainte | Réponse |
|---|---|
| Réseau intermittent | File d'attente locale (localStorage) + synchronisation automatique au retour du réseau (badge jaune « OFFLINE — N cas en attente ») |
| Frappe difficile | Puces tactiles × 58 symptômes (grandes cibles), dictée vocale Web Speech (fr-FR), texte libre normalisé côté API |
| Urgences visibles | Rappel hors-ligne : transférer immédiatement si coma / convulsions / saignements / enfant pâle et mou |
| Batterie | Thème sombre natif, zéro framework, zéro build (HTML/CSS/JS purs) |
| Vie privée | Aucune donnée ne quitte l'appareil sans action explicite ; le dernier cas est conservé localement |

## Parcours de saisie (4 étapes)

1. **Patient** — âge, sexe, poids, **grossesse + terme (SA)**,
   comorbidités (drépanocytose, VIH, diabète, **déficit G6PD**…), constantes.
2. **Symptômes** — texte libre + dictée, puces par système
   (dont groupe « Drépanocytose / grossesse » : douleurs osseuses, MAF↓…).
3. **Voyage** — 16 pays d'Afrique de l'Ouest, séjour rural, funérailles,
   contact malade, chimioprophylaxie, **photo clinique** (capture caméra,
   analysée par MedGemma si le mesh IA est branché).
4. **Biologie** — TDR palu, Hb, plaquettes, glycémie, créatinine → **Analyser**.

## Résultat affiché

Verdict (IMMÉDIAT / URGENCE / PRIORITAIRE / ROUTINE), signes d'alerte,
différentiel hiérarchisé, examens requis, **contre-indications médicamenteuses**
(ex. primaquine interdite chez la femme enceinte), orientation, citations sources.

## Architecture

```
frontend/mobile/
├── index.html      # coquille UI (4 étapes + résultat + paramètres)
├── app.js          # logique : état, file offline, API, rendu
├── sw.js           # service worker (cache coquille, jamais l'API)
├── manifest.json   # PWA manifest (installable)
└── icon.svg        # icône adaptative
```

- **Aucune décision clinique côté client** : l'analyse provient toujours du
  pipeline serveur (Rule Engine → Safety Gate → citations).
- Le repli local hors-ligne ne **prédit rien** : détection lexicale minimale
  uniquement pour pré-remplir les puces ; le cas part en file d'attente.
- Compatible avec `TROPIRAG_INFERENCE_MODE=deterministic|ollama|vllm` —
  l'interface ne change pas, seul le serveur change de mode.
