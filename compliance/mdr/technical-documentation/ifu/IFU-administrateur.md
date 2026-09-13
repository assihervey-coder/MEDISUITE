# Notice d'utilisation (IFU) — Profil ADMINISTRATEUR

> MEDISUITE v0.5 — à valider par l'usabilité sommative. Formation 4 h +
> quiz ≥ 80 % (PROC-06). Toute action d'administration est journalisée
> dans la chaîne d'audit (IEC 81001-5-1).

## 1. Périmètre

Comptes utilisateurs, rôles et permissions (RBAC), consentements RGPD,
consultation de l'audit, configuration de site. **Ne pas** confondre avec
l'exploitation technique (IFU Technicien) ; le rôle `administrateur` ne
donne PAS accès aux données cliniques complètes (principe du moindre
privilège — voir matrice ci-dessous).

## 2. Gestion des comptes et rôles

- Création via auth-service (nom, rôle, MFA TOTP obligatoire à
  l'activation) ; remise du secret TOTP en main propre uniquement.
- Matrice des rôles (résumé — source de vérité : `medisuite_core/rbac.py`) :

| Rôle | Accès notable |
|---|---|
| medecin | patient read/write, imagerie, prescription, IA (infer/explain) |
| radiologue | imagerie upload/report, patient read/export |
| biologiste | labo order/validate/qc |
| infirmier | patient read/write, imagerie read |
| pharmacien | prescription/dispense |
| urgentiste | urgences (patient, imagerie, labo, IA) |
| administrateur | comptes, config, audit — **patient read seulement** |
| auditeur | audit read/verify — **aucune donnée clinique** |
| patient | portail consentements uniquement |

- **Fail-closed** : tout rôle inconnu se voit refuser toute action — ne créez
  jamais un rôle libre à la main, utilisez la liste ci-dessus.
- Révocation immédiate à la sortie d'un agent (désactivation + rotations si
  compte à privilèges) ; revue trimestrielle des comptes inactifs.

## 3. Consentements RGPD (art. 7)

- Le portail patient permet au patient d'accorder et **révoquer** ses
  consentements ; la révocation est effective immédiatement dans les
  traitements applicatifs et tracée (chaîne d'audit).
- En cas de demande d'accès/rectification : procédure qualité (archive
  qualité) — toute rectification est traçée, jamais écrasante.

## 4. Consultation de l'audit

AuditLog : requêtes par patient/service/période ; bouton « Vérifier la
chaîne » recalcule les hachages SHA-256 (toute rupture = altération →
incident S2, PROC-04). L'administrateur consulte mais ne modifie jamais
l'audit (immutabilité technique).

## 5. Incidents et escalade

Toute suspicion de fuite, accès anormal, ou demande externe (justice,
assureur) → arrêt des actions et escalade immédiate fabricant + délégué à
la protection des données du CHU. Ne jamais traiter seul une demande
légale d'accès aux données.

## 6. Limites

Aucune extraction de données nominatives hors plateforme ; aucune
désactivation de l'audit, du MFA ou de la chaîne de hachage (ce sont des
garanties du dispositif) ; les configurations dangereuses sont refusées
par le système (fail-closed).
