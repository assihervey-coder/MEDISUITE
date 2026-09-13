# Architecture Diff

Répond à : « Qu'est-ce qui change exactement si j'accepte cette proposition ? »

1. snapshot de la baseline avant (`snapshots/<date>-before.yaml`)
2. application des modifications déclarées par le change set
3. snapshot après + diff (composants ajoutés/modifiés/retirés, dépendances, contrats)
4. rapport signé dans `reports/`, rattaché au dossier de preuve
