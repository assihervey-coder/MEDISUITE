"""Analyseur API — endpoints FHIR/DICOMweb/HL7/REST touchés."""
from __future__ import annotations

API_KINDS = {
    "/fhir": "fhir", "dicomweb": "dicomweb", "ORM^": "hl7", "ORU^": "hl7",
    "/api/": "rest", "/scores": "rest",
}


def analyze_apis(changed_paths: list[str], declared_apis: list[str] | None = None) -> dict:
    touched: set[str] = set()
    for path in changed_paths:
        p = path.lower()
        if "integration-service" in p or "fhir" in p:
            touched.add("fhir-r4")
        if "ecrf" in p:
            touched.add("fhir-r6-ecrf")
        if "dicom" in p or "imaging" in p:
            touched.add("dicomweb-ps318")
        if "hl7" in p or "laboratory" in p:
            touched.add("hl7v2-mllp")
        if "api-gateway" in p:
            touched.add("gateway-http")
        if "multimodal" in p:
            touched.add("fusion-inference")
    return {"apis_touched": sorted(touched), "count": len(touched)}
