# API_ARCHITECTURE

Ce volet est synthétisé dans SYSTEM_ARCHITECTURE.md et les modules de code
correspondants (voir src/tropirag/). Le détail d'implémentation vit dans le
code, testé et auditables — la documentation redondante serait un risque
d'obsolescence.

Points d'entrée :
- Moteur clinique : src/tropirag/clinical_engine/orchestrator.py
- Mesh IA : src/tropirag/ai/ (registry → routing → gateways → agents)
- Données : data/ (raw→staging→normalized→evidence→indexes)
- API : src/tropirag/api/ (routes /api/v1/*)
- Sécurité : src/tropirag/safety/ + docs/governance/SAFETY_INVARIANTS.md
