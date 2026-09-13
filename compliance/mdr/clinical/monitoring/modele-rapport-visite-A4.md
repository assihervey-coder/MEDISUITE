# RAPPORT DE VISITE DE MONITORING — Modèle A4

> **Format** : A4 portrait, marges 2 cm — impression directe navigateur/Word
> depuis ce modèle. Une visite = un rapport. Numérotation `MV-<ANNEE>-<NNN>`.
> Remplir **pendant** la visite, signé sous 5 jours ouvrés (plan-monitoring §4).
> Champs ⟦…⟧ à compléter ; cases A/C = Atteint / Constat.

```
┌─ PAGE 1 ─────────────────────────────────────────────────────────────┐

  MEDISUITE-CI-01 — Investigation clinique multicentrique (ISO 14155)
  RAPPORT DE VISITE DE MONITORING            N° : MV-⟦2026⟧-⟦NNN⟧

  TYPE            □ initiation (V0)  □ intermédiaire (V1-V6)  □ clôture (VC)  □ ad hoc
  SITE            □ CHU-COCODY   □ CHU-TREICHVILLE   □ CHU-BOUAKÉ
  DATE DE VISITE  ⟦AAAA-MM-JJ⟧        MONITEUR : ⟦Nom, qualité⟧
  PARTICIPANTS    ⟦coordonnateur site, investigateur principal, ARC…⟧
  PÉRIODE COUVERTE depuis ⟦date⟧  —  inclusions cumulées site : ⟦N⟧ / étude : ⟦N⟧

  A. ÉTAT SYSTÈME (preuves numériques, copie d'écran horodatée en annexe)
     /health version=logicielle ⟦v0.x⟧  = version protocole □ A □ C ⟦écart⟧
     /api/v1/ecrf/audit/verify integre=true            □ A □ C
     Requêtes SDV ouvertes : ⟦N⟧   résolues dans les délais : ⟦N/N⟧

  B. CONSENTEMENTS (échantillon ⟦N⟧ dossiers)
     Original signé daté avant inclusion              □ A □ C ⟦réfs⟧
     Version d'information en vigueur                 □ A □ C
     Différé d'urgence : ré-information ≤ 24 h        □ A □ C □ S/O

  C. ÉLIGIBILITÉ & DONNÉES (SDV ⟦N⟧ entrées / ⟦total⟧ — plan §2 : 20 %)
     F01 vs sources (âge, grossesse, modalités, doublons)   □ A □ C ⟦écarts⟧
     F03 horodatages P3 vs sources                          □ A □ C
     F06 sortie 30 j concordante                            □ A □ C

  D. SÛRETÉ — 100 % des F04 vérifiés à chaque visite
     EI/SAE reportés conformes, délais respectés            □ A □ C ⟦détails⟧
     SAE : 24 h DSMB ; ≤ 7 j ANOC-CI/Ministère ; MDR 87-90  □ A □ C
     Registre EI site ↔ eCRF cohérents                      □ A □ C

└──────────────────────────────────────────────────────────────────────┘

┌─ PAGE 2 ─────────────────────────────────────────────────────────────┐

  E. DÉVIATIONS DE PROTOCOLE constatées (à doubler dans registre-deviations)
     ┌────┬───────────────┬───────────────┬───────────────────────────┐
     │ N° │ Description   │ Majeure/min.  │ Action corrective (CAL)   │
     ├────┼───────────────┼───────────────┼───────────────────────────┤
     │ DEV│ ⟦…⟧           │ □ majeure □min│ ⟦…⟧ — échéance ⟦date⟧     │
     └────┴───────────────┴───────────────┴───────────────────────────┘

  F. MATÉRIEL / UDI
     Basic UDI-DI en service : ⟦MEDISUITE-PLTF-AIDE-DECISION⟧
     Journal pannes site 24 h (F01) à jour                    □ A □ C

  G. REQUÊTES DE MONITORING ouvertes en séance (le site clôt sous 10 j o.)
     ┌──────┬────────────┬─────────────┬──────────────────────────────┐
     │ Q-ID │ Sujet/code │ Champ       │ Question                     │
     ├──────┼────────────┼─────────────┼──────────────────────────────┤
     │ Q-   │ CI01-      │ ⟦F03.delai⟧ │ ⟦justifier par la source⟧    │
     └──────┴────────────┴─────────────┴──────────────────────────────┘

└──────────────────────────────────────────────────────────────────────┘

┌─ PAGE 3 ─────────────────────────────────────────────────────────────┐

  H. ACTIONS ET ÉCHÉANCES (suivi de la lettre de relance J+11, escalade J+21)
     ┌────┬──────────────────────────────┬──────────┬──────────┬────────┐
     │ N° │ Action                       │ Respons. │ Échéance │ Statut │
     ├────┼──────────────────────────────┼──────────┼──────────┼────────┤
     │ AC-│                              │          │          │ □ouvert│
     └────┴──────────────────────────────┴──────────┴──────────┴────────┘

  I. OPINION DU MONITEUR
     Site conforme au protocole :  □ oui  □ oui avec réserves  □ non
     Impact sûreté participant :   □ aucun □ à évaluer        □ immédiat →
     promoteur sous 24 h + DSMB.
     Commentaire ⟦…⟧

  SIGNATURES
     Le moniteur  :  ⟦Nom, date, signature⟧
     Le promoteur (prise de connaissance) : ⟦Nom, date⟧
     Coordonnateur site (réception) : ⟦Nom, date⟧

  ANNEXES  □ captures /health + audit/verify  □ liste SDV détaillée
           □ extraits sources pseudonymisés (cote dossier site)
└──────────────────────────────────────────────────────────────────────┘
```

**Conservation** : original signé → registre promoteur (25 ans) ; copie →
dossier site ; écarts → `registre-deviations.md`. Ce rapport est un
enregistrement qualité au sens PROC-01 (SMQ ISO 13485).
