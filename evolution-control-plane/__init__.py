"""MEDISUITE Evolution Control Plane V1 — package racine.

L'alias d'importation `ecp` (nécessaire car ce répertoire contient des
tirets) est enregistré par `_bridge.register()` — appelé par les conftest
pytest et les points d'entrée :

    from ecp.domain.proposal.enums import ProposalState

Ce module reste volontairement SANS import relatif : il peut être chargé
par pytest avec une identité de module quelconque.
"""
