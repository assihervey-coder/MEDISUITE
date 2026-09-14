"""Export DHIS2 pour le MSP-CI — indicateurs de surveillance agrégés (V1.2).

Chaîne déterministe :
    analyses persistées → Dhis2Mapper (compteurs) → DataValue(s)
    → Exporter (JSON dataValueSets / CSV / ADX 2.0 XML)
    → OfflineQueue (runtime/state) → Transport (envoi httpx optionnel)

Aucun envoi réseau sans configuration explicite du serveur : le mode par
défaut est ``offline_queue`` (file d'attente locale jusqu'à ce que le MSP-CI
 fournisse base_url + identifiants).

IA ≠ autorité clinique — et l'export l'est tout autant : chaque valeur
dériverait exclusivement des analyses déterministes persistées.
"""
from tropirag.integrations.dhis2.exporter import Dhis2Exporter
from tropirag.integrations.dhis2.mapper import Dhis2Mapper
from tropirag.integrations.dhis2.models import DataValue, DataValueSet
from tropirag.integrations.dhis2.queue import OfflineQueue
from tropirag.integrations.dhis2.settings import Dhis2Config, load_dhis2_config

__all__ = [
    "DataValue", "DataValueSet", "Dhis2Mapper", "Dhis2Exporter",
    "OfflineQueue", "Dhis2Config", "load_dhis2_config",
]
