# ADR-0011 — Kubernetes + Helm + ArgoCD (GitOps)

**Statut :** accepté · **Date :** 2026-09-13 · **Décideurs :** architecture MEDISUITE

## Contexte
38 services déployés à la main = dérive de config garantie.

## Décision
Kustomize base/overlays, 5 charts Helm (core/ai/multimodal/monitoring/security), ArgoCD app-of-apps.

## Conséquences
- Positive : cohérence globale, auditabilité, coût de possession réduit.
- Vigilance : chaque écart à cette décision exige un nouvel ADR (processus documenté).
- Traçabilité : décision alignée avec l'audit d'architecture du 2026-09 (risques R1-R10).
