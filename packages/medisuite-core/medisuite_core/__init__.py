"""medisuite-core : noyau transverse de la plateforme MEDISUITE.

Modules :
- security     : mots de passe scrypt, JWT HS256 (stdlib), TOTP RFC 6238
- rbac         : matrice de rôles et permissions cliniques
- audit_chain  : registre d'audit à chaîne de hachage (IEC 81001-5-1)
- db           : base SQLAlchemy (SQLite dev / PostgreSQL prod)
- http         : fabrique d'applications FastAPI homogènes pour les 38 services
- fhir         : mapping FHIR R4 (Patient, Observation, Condition, Encounter)
- hapi_client  : client REST serveur HAPI FHIR R4 (metadata, create, search, transaction)
- observability: télémétrie OpenTelemetry (W3C traceparent, spans, export OTLP/HTTP)
- hl7          : HL7 v2.5 (parse/build MSH, ORM^O01, ORU^R01, ADT^A08, SIU^S12, ACK)
- events       : bus d'événements interne (topics, sink JSONL)
- seed         : données de démonstration ivoiriennes (CNAM, FCFA, Abidjan)
"""
__version__ = "0.4.0"
