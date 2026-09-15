"""Registre des services MEDISUITE — source unique pour ports, lancement, tests.

Convention de ports : 800x = cœur, 81xx = spécialités (ordre MODULES.md),
82xx = transverses, 83xx = passerelles spécialisées.
"""
import os

SERVICES: list[dict] = [
    # --- passerelle principale + cœur
    {"name": "api-gateway", "dir": "services/api-gateway", "port": 8000,
     "module": "src.main:app", "group": "core"},
    {"name": "auth-service", "dir": "services/auth-service", "port": 8001,
     "module": "src.main:app", "group": "core"},
    {"name": "patient-service", "dir": "services/patient-service", "port": 8002,
     "module": "src.main:app", "group": "core"},
    {"name": "imaging-service", "dir": "services/imaging-service", "port": 8003,
     "module": "src.main:app", "group": "core"},
    {"name": "laboratory-service", "dir": "services/laboratory-service", "port": 8004,
     "module": "src.main:app", "group": "core"},
    # --- services transverses
    {"name": "reporting-service", "dir": "services/reporting-service", "port": 8200,
     "module": "src.main:app", "group": "transverse"},
    {"name": "notification-service", "dir": "services/notification-service", "port": 8201,
     "module": "src.main:app", "group": "transverse"},
    {"name": "audit-service", "dir": "services/audit-service", "port": 8202,
     "module": "src.main:app", "group": "transverse"},
    {"name": "integration-service", "dir": "services/integration-service", "port": 8203,
     "module": "src.main:app", "group": "transverse"},
    {"name": "analytics-service", "dir": "services/analytics-service", "port": 8204,
     "module": "src.main:app", "group": "transverse"},
    {"name": "ecrf-service", "dir": "services/ecrf-service", "port": 8205,
     "module": "src.main:app", "group": "transverse"},
    # --- passerelles spécialisées
    {"name": "dicom-gateway", "dir": "services/dicom-gateway", "port": 8300,
     "module": "src.main:app", "group": "gateway"},
    {"name": "hl7-gateway", "dir": "services/hl7-gateway", "port": 8301,
     "module": "src.main:app", "group": "gateway"},
    {"name": "multimodal-gateway", "dir": "services/multimodal-gateway", "port": 8302,
     "module": "src.main:app", "group": "gateway"},
    {"name": "explainability-service", "dir": "services/explainability-service",
     "port": 8303, "module": "src.main:app", "group": "gateway"},
    # --- aide à la décision clinique (TropiRAG intégré — docs/TROPIRAG-INTEGRATION.md)
    # Mesh LLM local : TROPIRAG_INFERENCE_MODE=deterministic|ollama|vllm ;
    # TROPIRAG_OLLAMA_URL = nœud unique, TROPIRAG_OLLAMA_NODES = multi-nœuds
    # (format speech=http://node1:11434,text=http://node2:11434,...).
    # Surcharges à chaud : export des variables avant `services/run_all.py --up`.
    {"name": "tropirag-service", "dir": "tropirag", "port": 8304,
     "module": "tropirag.api.app:app", "group": "gateway",
     "health_path": "/api/v1/health",
     "env": {"TROPIRAG_ROOT": "{ROOT}/tropirag",
             "TROPIRAG_DB_PATH": "{ROOT}/data/tropirag.db",
             "TROPIRAG_DATA_DIR": "{ROOT}/tropirag",
             "TROPIRAG_INFERENCE_MODE": os.environ.get(
                 "TROPIRAG_INFERENCE_MODE", "deterministic"),
             "TROPIRAG_OLLAMA_URL": os.environ.get(
                 "TROPIRAG_OLLAMA_URL", "http://127.0.0.1:11434"),
             "TROPIRAG_OLLAMA_NODES": os.environ.get("TROPIRAG_OLLAMA_NODES", "")}},
]

SPECIALTIES: list[tuple[int, str, str]] = [
    # (n° module, slug service, nom affiché) — ports 8100 à 8123
    (3, "oncology-service", "Oncologie"),
    (4, "tumor-service", "Tumeurs"),
    (5, "ophthalmology-service", "Ophtalmologie"),
    (6, "diabetes-service", "Diabétologie"),
    (7, "traumatology-service", "Traumatologie"),
    (8, "cardiology-service", "Cardiologie"),
    (9, "pneumology-service", "Pneumologie"),
    (10, "obstetrics-service", "Obstétrique"),
    (11, "gynecology-service", "Gynécologie"),
    (12, "fertility-service", "Fertilité"),
    (13, "neurology-service", "Neurologie"),
    (14, "psychiatry-service", "Psychiatrie"),
    (15, "pediatrics-service", "Pédiatrie"),
    (16, "nephrology-service", "Néphrologie"),
    (17, "gastroenterology-service", "Gastro-entérologie"),
    (18, "dermatology-service", "Dermatologie"),
    (19, "ent-service", "ORL"),
    (20, "rheumatology-service", "Rhumatologie"),
    (21, "urology-service", "Urologie"),
    (22, "nuclear-medicine-service", "Médecine nucléaire"),
    (23, "radiotherapy-service", "Radiothérapie"),
    (24, "anesthesia-service", "Anesthésie-Réanimation"),
    (25, "geriatrics-service", "Gériatrie"),
    (26, "emergency-service", "Urgences"),
]

SPECIALTY_SERVICES: list[dict] = [
    {"name": slug, "dir": f"services/{slug}", "port": 8100 + i,
     "module": "src.main:app", "group": "specialty", "module_no": n,
     "label": label}
    for i, (n, slug, label) in enumerate(SPECIALTIES)
]

ALL_SERVICES: list[dict] = SERVICES + SPECIALTY_SERVICES


def by_name(name: str) -> dict | None:
    return next((s for s in ALL_SERVICES if s["name"] == name), None)
