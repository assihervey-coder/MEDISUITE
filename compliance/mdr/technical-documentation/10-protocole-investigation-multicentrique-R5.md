# R5 — Protocole d'investigation clinique multicentrique « MEDISUITE-CI-01 »

> Document n° TD-10 · Version 1.0.0-draft · Statut : 🟠 **protocole rédigé,
> soumissions non faites** (ANOC-CI 🔴, autorisations Ministère 🔴, accords
> sites 🔴, signatures 🔴) — jalon R5 du plan `08-plan-validation-v1.0.0.md`
> (M+2 → M+6). Ce protocole précise et **supersède l'estimation
> d'effectifs** de `06-evaluation-clinique.md` §2 (voir §7.4).

## 0. Carte d'identité du protocole (ISO 14155:2020, §6)

| Champ | Valeur |
|---|---|
| Titre | Étude prospective multicentrique de la performance et de la sûreté de MEDISUITE (aide à la décision clinique assistée par IA) en contexte hospitalier ivoirien |
| Code | MEDISUITE-CI-01 |
| Version protocole | 1.0.0-draft (contrôle documentaire PROC-01) |
| Dispositif | MEDISUITE plateforme v1.0.0-candidate (tag ≥ v0.6.0, Basic UDI-DI MEDISUITE-PLTF-AIDE-DECISION, classe IIb règle 11 — voir `01-identification-classification.md`) |
| Promoteur / fabricant | ASSI Herve — Abidjan, Côte d'Ivoire |
| Investigateur coordonnateur | 🔴 à nommer (CHU de Cocody — proposition) |
| Sites | CHU Cocody (coordinateur), CHU Treichville, CHU Yopougon — extension CHU Bouaké prévue (§4.1) |
| Référentiel conduite | ISO 14155:2020 (BPC), MDR 2017/745 art. 62-80 + Annexe XV, loi ivoirienne de recherche sur la personne, protection des données loi 2013-450 (ARTCI/CGTDI) |
| Enregistrement | PACTR (Pan African Clinical Trial Registry) avant 1ʳᵉ inclusion — 🔴 |
| Comité d'éthique | ANOC-CI (Comité National d'Éthique de la Recherche) — 🔴 soumission M+3 |
| Durée | Inclusion M+6 → M+16 (10 mois), suivi 30 j, lock M+18 (aligné R6) |
| Version d'analyse statistique | SAP v1.0 figée avant lock (annexe A5) |

## 1. Contexte et justification (état de l'art)

La Côte d'Ivoire concentre une demande de soins aigus en forte croissance
avec une imagerie et un laboratoire sous-équipés en expertise d'interprétation
: délais de triage aux urgences longs, disponibilité limitée des spécialistes
(radiologues, néphrologues, oncologues) hors Abidjan, et absence d'outils
d'aide à la décision adaptés aux réalités locales (données de référence,
langues, flux patients). Les scores cliniques validés internationalement
(ESI, qSOFA, NIHSS, ASPECTS, BI-RADS, KDIGO…) sont implémentés dans
MEDISUITE avec citation de leurs référentiels primaires — leur validité
propre n'est PAS l'objet de cette investigation (`06-evaluation-clinique.md`
§6) ; ce qui est nouveau, et donc à évaluer, c'est le **dispositif complet** :
orchestration multimodale, sorties IA de fusion (cross-attention + gated,
ADR 0017-0019) et interface de validation clinique.

La littérature sur les logiciels d'aide à la décision par IA en Afrique
subsaharienne est dominée par des études rétrospectives monocentriques, sans
évaluation du flux de travail clinique ni des dégradations de modalités
(fréquentes : IRM indisponible, bilan incomplet). MEDISUITE traite
explicitement les modalités manquantes (ADR-0018) : c'est une prétention
spécifique du dispositif que seule une investigation prospective peut
prouver en conditions réelles. Aucun dispositif équivalent ne dispose d'une
équivalence démontrable pour ce contexte (Annexe XIV §1a) — l'investigation
clinique est donc requise pour la conformité aux EGSP relatives aux
caractéristiques et performances (GSPR §1, §17, §23).

## 2. Prétention clinique à démontrer (benefit-risk)

Le dispositif, utilisé par un professionnel de santé formé (IFU v1.0),
**améliore la concordance de la décision clinique avec la référence
adjudiquée et réduit les délais de priorisation**, sans événement indésirable
lié au dispositif, dans les 5 scénarios critiques suivants (issus de
`05-iec-62366-usabilite.md` S1-S5) :

1. **S1 — Code AVC** : détection LKW, NIHSS, ASPECTS, respect fenêtres
   rtPA/thrombectomie (module 13 + urgences 26) ;
2. **S2 — BI-RADS** : catégorisation mammographique et conduite (module 03) ;
3. **S3 — Triage ISS/ESI** : priorisation aux urgences (module 26) ;
4. **S4 — Validation résultats labo** : valeurs critiques, delta check
   (module 02) ;
5. **S5 — Fusion multimodale** : synthèse interprétable multi-sources avec
   modalités manquantes (multimodal-gateway).

Le dispositif est une **aide à la décision** : la décision finale reste du
professionnel ; toute sortie IA est explicite (importance des modalités,
attention — ADR-0015) et traçable (audit chaîné SHA-256, télémétrie OTel).
Bénéfice attendu vs risques documentés (FMEA RM-01…RM-10,
`03-analyse-risques-iso14971.md`) : les risques résiduels ≥12 (RM-02,
RM-05, RM-09) sont mesurés par les endpoints de sûreté et d'exactitude de
ce protocole — sauf dégradation de service (RM-07) couverte par les
exigences de continuité (GSPR §17.2) et surveillée en télémétrie.

## 3. Objectifs et endpoints

### 3.1 Objectif primaire

Démontrer que l'usage de MEDISUITE par le clinicien atteint une **concordance
(kappa de Cohen pondéré) ≥ 0,80** avec la référence adjudiquée (§3.3) sur la
décision clé des scénarios S1-S5, regroupés.

### 3.2 Endpoints primaires (co-primaires assumés, alpha réparti §8.3)

| # | Endpoint | Métrique | Critère de succès |
|---|---|---|---|
| P1 | Concordance décision vs référence adjudiquée | κ pondéré (IC 95 %) | borne inf IC > 0,72 et estimation ≥ 0,80 |
| P2 | Sûreté | incidence EI/SAE liés au dispositif à 30 j | 0 SAE grave inattendu ; EI ≤ 5 % des séquences |
| P3 | Délai priorisation (triage → orientation) | médiane, différence vs pratique standard | réduction ≥ 10 % non-infériorisée (marge −0 %, supériorité descriptive) |

### 3.3 Référence adjudiquée (gold standard)

Comité d'adjudication indépendant (2 experts par spécialité + 1 tierce en
cas de désaccord), aveugle à la sortie du dispositif, statuant sur dossier
complet (données cliniques, imagerie, laboratoire, suivi à 30 j) selon la
grille A3. Concordance inter-juges κ ≥ 0,75 exigée avant lock des verdicts.

### 3.4 Endpoints secondaires

S2.1 AUC/sensibilité/spécificité par tâche IA (S1-S5, exploratoire par
scénario) ; S2.2 taux d'erreurs d'usage (liaison usabilité formative/summative
R3 — grille passation) ; S2.3 charge de travail NASA-TLX par scénario ;
S2.4 respect fenêtres rtPA/thrombectomie en % (S1) ; S2.5 taux de
dégradations élégantes correctes (modalités manquantes — ADR-0018) ;
S2.6 satisfaction utilisateurs (échelle SUS) ; S2.7 disponibilité du
dispositif par site (télémétrie OTel — `docs/OTEL.md`).

## 4. Design et population

### 4.1 Design

Étude **prospective multicentrique, cohorte consécutive, intra-patient
appariée** : pour chaque dossier éligible, le clinicien 1) consigne sa
décision de pratique standard, 2) consulte la sortie MEDISUITE, 3) consigne
sa décision finale et son adhésion (acceptée/partiellement/refusée). La
référence adjudiquée (§3.3) évalue les deux décisions. Ce design intra-patient
évite un bras contrôle séparé (éthique : aucun retard de soin ; le dispositif
n'est jamais le seul décideur — art. 62.3 MDR, bénéfice-coût favorable).
Sites : 3 CHU Abidjan ; extension CHU Bouaké à M+9 si inclusion < 80 % du
rythme cible (décision DSMB).

### 4.2 Population

Adultes (≥ 18 ans) passant par urgences, imagerie ou laboratoire des sites,
dans un des scénarios S1-S5. Inclusion après consentement éclairé écrit
(fr ; notice orale baoulé/dioula documentée) — les dossiers « urgence vitale
immédiate » bénéficient de la procédure d'urgence (consentement différé
selon loi ivoirienne et ISO 14155 §6.7, signalé au comité). Critères
d'exclusion : mineurs (hors module pédiatrie, non couvert par ce protocole),
grossesse pour les scénarios irradiants (S2), refus, dossier techniquement
inexploitable. Aucune restriction par sexe/origine : représentativité
ivoirienne assumée et analysée (§8.4).

### 4.3 Critères de non-éligibilité du dossier (post-inclusion)

Perte > 2 modalités primaires du scénario (au-delà de la politique
ADR-0018), panne site > 24 h au moment du passage (documentée, non
retirée de l'ITT), doublon patient dans 14 j.

## 5. Dispositif étudié et gestion de configuration

Version figée **v1.0.0-candidate** (tag Git + hash, commit injecté dans
`/health` et l'écran « À propos » UDI) installée dans chaque site
(K8s ou compose minimal, montée p. 03), avec : profils FHIR IOP actifs
(ADR-0024), télémétrie OTel → collecteur site, comptes nominatifs RBAC,
formation initiale des utilisateurs (PROC-06, registre de formation) et
FusionViewer actif pour S5. **Toute correction logicielle pendant
l'inclusion** passe par l'évaluation de modification substantielle (MDR
art. 2.109, processus §1 du dossier technique) : correction non substantielle
→ version patch documentée + note aux sites ; substantielle → arrêt des
inclusions, amendement de protocole, ré-information. Le jeu de données
d'entraînement des modèles de chaque site est la configuration MLflow
déclarée (§3 de `06-evaluation-clinique.md`) — les datasets synthétiques
`datasets/` (v0.6.0) ne participent JAMAIS à l'entraînement des modèles de
l'investigation (note légale du manifest).

## 6. Sécurité des patients et gestion des événements

| Événement | Définition | Délai investigateur | Délai promoteur |
|---|---|---|---|
| EI lié au dispositif | événement indésirable dont la cause plausible est la sortie ou l'indisponibilité du dispositif | 24 h → promoteur | registre CI-01 |
| SAE | EI entraînant décès, mise en vie en jeu du pronostic, hospitalisation/prolongation, incapacité | 24 h → promoteur + DSMB | ANOC-CI + Ministère ≤ 7 j ; si incident grave impliquant le DM → **vigilance MDR art. 87-90** |
| Déviation protocole | non-respect d'une exigence du protocole | 5 j ouvrés | registre + DSMB trimestriel |

DSMB (3 membres indépendants : clinicien, statisticien, patient advocate) :
revue trimestrielle des inclusions, EI/SAE, déviations, qualité données ;
règles d'arrêt (A5) : ≥ 2 SAE liées au dispositif dans un site, mortalité
30 j > pratique standard + 3 σ, ou perte de confidentialité massive →
arrêt temporaire immédiat.

Confidentialité : pseudonymisation à l'ingestion (identifiant studie + code
site ; correspondance gardée sous scellé site), données hébergées sur
serveur site pilote (pas de transfert hors CI), accès par rôle, journal
d'accès chaîné (audit-service), DPIA par site avant démarrage (loi 2013-450,
CGTDI/ARTCI), conservation 10 ans (archives cliniques).

## 7. Statistiques (SAP v1.0 — annexe A5)

### 7.1 Population analysée

ITT : tous les dossiers inclus avec au moins une décision consignée. PP :
ITT moins déviations majeures pré-spécifiées (§4.3, panne > 24 h si le
clergement le justifie). Analyse principale : ITT ; PP en sensibilité.

### 7.2 Taille d'échantillon (endpoint P1)

Méthode de précision sur la sensibilité du couple (clinicien + dispositif)
vs référence : cible sensibilité 0,90, demi-largeur d'IC 95 % ≤ 0,05 →
n_+ = z²·p(1−p)/d² = 3,8416×0,9×0,1/0,0025 ≈ **139 événements positifs**.
Prévalence pondérée des conditions cibles (S1-S5) estimée 30 % → 463 dossiers
évaluables ; +15 % non-évaluables/déviations → **545** ; arrondi et
répartition par site : **3 × 200 = 600 dossiers inclus** (rythme ~1,9/site/j
sur 10 mois — compatible avec les flux CHU documentés).

### 7.3 Analyse primaire

κ pondéré (poids quadratiques) et son IC 95 % (bootstrap stratifié par site,
10 000 rééchantillons) ; co-endpoints P2/P3 : incidence EI (exact), délais
(Kaplan-Meier + test log-rank vs standard historique apparié, modèle mixte
avec effet aléatoire site). Répartition d'alpha : Holm sur les 3 co-primaires.

### 7.4 Écart assumé vs document antérieur

`06-evaluation-clinique.md` §2 annonçait « ordre de grandeur 300-500
patients **par site** ». Le présent protocole fixe 600 au total (200/site) :
l'estimation initiale était un ordre de grandeur pré-protocole ; le calcul
de §7.2 est la justification demandée. Ce document (TD-10 v1.0) supersedes
cette ligne ; `06-evaluation-clinique.md` sera mis à jour à la clôture R5
(contrôle documentaire PROC-01).

## 8. Organisation, monitoring, qualité

- **Rôles** : promoteur (ASSI Herve) ; investigateur coordonnateur 🔴 ;
  investigateurs sites 🔴 ; monitor indépendant 🔴 (contrat) ; data manager
  🔴 ; statisticien indépendant 🔴 ; DSMB 🔴.
- **Monitoring** : visite d'initiation par site, monitoring 100 % des
  endpoints primaires + 20 % aléatoire du reste, requêtes eCRF < 5 j ;
  rapport de monitoring par visite (annexe A4).
- **eCRF** : formulaires basés sur les profils FHIR IOP (ADR-0024) ingérés
  par le hub HAPI du site ; contrôles de cohérence à la saisie ; audit
  chaîné SHA-256 natif ; extraction verrouillée par data manager + témoins.
  > **Mise à jour v0.7.0** : l'eCRF est OPÉRATIONNEL 🟢 —
  > `services/ecrf-service` (F01-F06 validés par `medisuite_core/ecrf.py`,
  > signatures investigateur + amendements versionnés, requêtes SDV,
  > synchronisation offline idempotente, export DSMB agrégé sans PHI,
  > poussée HAPI IOP) et écran `/ecrf` du web-portal (saisie hors-ligne).
  > Voir `docs/E-CRF.md`. L'exécution (inclusions, visites de monitoring)
  > reste 🔴 jusqu'au feu vert R6.
- **Déviations et amendements** : toute modification du protocole =
  version amendée + ANOC + ré-information ; registre des déviations.
- **Audit qualité** : audit interne SMQ (PROC-08) de l'investigation à M+9 ;
  archives d'investigation (TSF) par site, inventaire tenu par le promoteur.

## 9. Calendrier R5 (vers feu vert R6)

| Jalon | Échéance | Responsable | Statut |
|---|---|---|---|
| Protocole v1.0-draft (ce document) + SAP + CRF + consentement | M+2 | promoteur | 🟠 rédigé |
| Soumission ANOC-CI + PACTR | M+3 | promoteur + coordonnateur | 🔴 |
| Autorisation Ministère (investigation DM) + DPIA sites | M+4 | promoteur | 🔴 |
| Accords sites + installations + formation | M+4 → M+5 | coordonnateur | 🔴 |
| Feu vert inclusion (R6) | M+6 | promoteur + ANOC | 🔴 |

## 10. Annexes

- **A1 — CRF maquette** : identification pseudonymisée, scénario S1-S5,
  décisions (standard / finale / adhésion), sorties dispositif (score,
  importance modalités), délais horodatés, statut 30 j.
- **A2 — Consentement éclairé** : objectifs, alternative (pratique
  standard garantie), données collectées, durée, retrait sans préjudice,
  contacts promoteur/ANOC ; notice baoulé/dioula orale certifiée.
- **A3 — Grille d'adjudication** : verdict par scénario, échelles de
  certitude, règle de désaccord → tierce arbitre.
- **A4 — Plan de monitoring** : fréquences visites, checklist, gestion des
  requêtes.
- **A5 — Plan d'analyse statistique (SAP)** : dérivations des variables,
  populations, méthodes §7, règles d'arrêt DSMB, gabarits de tables.
- **A6 — Traçabilité EGSP** : mapping endpoints ↔ exigences GSPR
  (`02-gspr-annexe-I.md`) ↔ risques FMEA mesurés.

## 11. Signatures (à obtenir — jalon R5 clôturé à ce stade)

| Rôle | Nom | Signature | Date |
|---|---|---|---|
| Promoteur / fabricant | ASSI Herve | 🔴 | — |
| Investigateur coordonnateur | 🔴 à nommer | 🔴 | — |
| Responsable réglementaire | 🔴 à désigner | 🔴 | — |
| Statisticien (SAP) | 🔴 à contractualiser | 🔴 | — |
