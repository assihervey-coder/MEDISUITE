"""Tests de l'infra k8s + publication GHCR (chantier v0.15 —
COUVERTURE-ARBRE-INITIAL §2 bloc `infrastructure/` et `.github/`).

Propriétés verrouillées :
1. VALIDITÉ YAML — tous les manifests k8s se parsent (safe_load_all) ;
2. DEFAULT-DENY — la base impose deny ingress+egress puis allowlist ;
3. PORTES DE SORTIE — DNS kube-system + api-gateway :8000 depuis ingress-nginx ;
4. MULTI-ENV — overlays dev/staging/prod distincts, prod ≥ 2 répliques + PDB ;
5. GHCR — job docker-publish : 6 services, permissions packages:write,
   image ghcr.io/…/medisuite-<service>, tags semver+sha, build Dockerfile réel.
"""
from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
K8S = ROOT / "infrastructure" / "kubernetes"
CI = ROOT / ".github" / "workflows" / "ci.yml"


def _docs(path: Path) -> list[dict]:
    return [d for d in yaml.safe_load_all(path.read_text(encoding="utf-8")) if d]


def test_01_tous_les_manifests_k8s_sont_valides():
    for path in sorted(K8S.rglob("*.yaml")):
        docs = _docs(path)
        assert docs, f"manifest vide : {path.relative_to(ROOT)}"
        if "helm" in path.parts:
            # entrées Helm (Chart.yaml, values.yaml) : pas de kind — on
            # vérifie seulement que le graphe de valeurs est présent.
            continue
        for d in docs:
            assert "apiVersion" in d and "kind" in d, f"doc invalide : {path}"


def test_01b_helm_values_exposent_le_hook_image():
    values = yaml.safe_load(
        (K8S / "helm" / "medisuite-core" / "values.yaml").read_text(encoding="utf-8")
    )
    assert "image" in values and "repository" in values["image"], \
        "values.yaml doit exposer image.repository (cible GHCR)"


def test_02_default_deny_puis_allowlist():
    docs = _docs(K8S / "base" / "networkpolicy.yaml")
    assert len(docs) == 5, "5 politiques attendues (2 deny + 3 allow)"
    names = [d["metadata"]["name"] for d in docs]
    assert names[:2] == ["default-deny-ingress", "default-deny-egress"]
    for d in docs[:2]:
        assert d["spec"]["podSelector"] == {}
        assert "Ingress" in d["spec"]["policyTypes"] or "Egress" in d["spec"]["policyTypes"]
        assert not d["spec"].get("ingress") and not d["spec"].get("egress"), \
            "un default-deny ne doit porter AUCUNE règle allow"
    # allowlist documentée dans le même fichier
    allow = {d["metadata"]["name"]: d for d in docs[2:]}
    assert set(allow) == {"allow-in-namespace", "allow-egress-dns", "allow-ingress-gateway"}


def test_03_portes_de_sortie_minimales():
    docs = {d["metadata"]["name"]: d for d in _docs(K8S / "base" / "networkpolicy.yaml")}
    dns = docs["allow-egress-dns"]["spec"]["egress"]
    kube = dns[0]["to"][0]["namespaceSelector"]["matchLabels"]
    assert kube == {"kubernetes.io/metadata.name": "kube-system"}
    ports = {(p["protocol"], p["port"]) for p in dns[0]["ports"]}
    assert {("UDP", 53), ("TCP", 53)} <= ports
    gw = docs["allow-ingress-gateway"]["spec"]
    assert gw["podSelector"]["matchLabels"] == {"app": "api-gateway"}
    from_ns = gw["ingress"][0]["from"][0]["namespaceSelector"]["matchLabels"]
    assert from_ns == {"kubernetes.io/metadata.name": "ingress-nginx"}
    assert gw["ingress"][0]["ports"] == [{"protocol": "TCP", "port": 8000}]


def test_04_base_kustomization_inclut_la_politique():
    k = yaml.safe_load((K8S / "base" / "kustomization.yaml").read_text(encoding="utf-8"))
    assert "networkpolicy.yaml" in k["resources"]


def test_05_overlays_multi_env():
    expected = {"dev": "medisuite-dev", "staging": "medisuite-staging", "prod": "medisuite-prod"}
    seen_ns = {}
    for env, ns in expected.items():
        p = K8S / "overlays" / env / "kustomization.yaml"
        assert p.exists(), f"overlay manquant : {env}"
        k = yaml.safe_load(p.read_text(encoding="utf-8"))
        assert k["namespace"] == ns, f"{env} : namespace inattendu"
        assert "../../base" in str(k["resources"]), f"{env} doit dériver de la base"
        seen_ns[env] = k["namespace"]
    assert len(set(seen_ns.values())) == 3, "chaque env doit avoir SON namespace"
    # prod : répliques ≥ 2 + PDB passerelle
    replicas = yaml.safe_load(
        (K8S / "overlays" / "prod" / "replicas.yaml").read_text(encoding="utf-8")
    )
    assert replicas["spec"]["replicas"] >= 2
    pdb = yaml.safe_load((K8S / "overlays" / "prod" / "pdb.yaml").read_text(encoding="utf-8"))
    assert pdb["kind"] == "PodDisruptionBudget" and pdb["spec"]["minAvailable"] >= 1


def test_06_ci_publie_sur_ghcr():
    t = CI.read_text(encoding="utf-8")
    assert "docker-publish:" in t, "job docker-publish absent"
    assert "ghcr.io/${{ github.repository }}/medisuite-" in t
    assert "packages: write" in t, "permission packages:write requise"
    for svc in ("api-gateway", "auth-service", "patient-service", "imaging-service",
                "laboratory-service", "ecrf-service"):
        assert svc in t, f"{svc} absent de la matrice de publication"
    assert "SERVICE_DIR=services/${{ matrix.service }}" in t, "build arg Dockerfile"
    assert "type=semver,pattern={{version}}" in t, "épinglage semver (prod)"
    assert "needs: [clinical-rules, packages-integration]" in t, \
        "publication seulement si les suites vertes"
