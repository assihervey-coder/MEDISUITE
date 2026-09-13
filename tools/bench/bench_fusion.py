#!/usr/bin/env python3
"""Banc de performance d'inférence — fusion multimodale MEDISUITE (v0.5).

Mesure la latence de bout en bout d'une requête d'inférence (payload
synthétique représentatif : imagerie 2D 32×32 + tabulaire 6 paramètres)
pour les deux backends supportés (ADR 0022/0023) :

- numpy  : FusionEngine déterministe (socle, toute installation) ;
- torch  : TorchFusionModel entraînable (predict après fit court).

Métriques produites : p50/p95/p99, moyenne, min/max, throughput req/s,
verdict EGSP (p95 ≤ 2000 ms — dossier CE §4 performance).

Usage :
    python3 tools/bench/bench_fusion.py --backend numpy --requests 500
    python3 tools/bench/bench_fusion.py --backend torch --requests 300 \
        --module 8 --missing-ratio 0.3 -o bench_gpu.json
"""
from __future__ import annotations

import argparse
import json
import pathlib
import statistics
import sys
import time
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[2]
for p in ("ai", "packages/medisuite-core"):
    sys.path.insert(0, str(ROOT / p))

from multimodal.factory import engine_for_module  # noqa: E402

CRITIQUE_P95_MS = 2000.0  # EGSP dossier CE §4 : latence inférence ≤ 2 s


def make_payload(rng, size: int = 32, missing_ratio: float = 0.0) -> dict:
    """Requête synthétique représentative (2 modalités, 1 manquante p fois)."""
    payload = {"tabulaire": {"features": [55.0, 1, 9.8, 132.0, 88.0, 24.5]}}
    if rng.random() >= missing_ratio:
        payload["imaging_2d"] = {
            "tensor": rng.normal(0.5, 0.2, (size, size)).tolist()}
    return payload


def percentile(sorted_vals: list[float], p: float) -> float:
    if not sorted_vals:
        return 0.0
    k = max(0, min(len(sorted_vals) - 1,
                   round((len(sorted_vals) - 1) * p / 100.0)))
    return sorted_vals[k]


def bench(args) -> dict:
    import numpy as np
    rng = np.random.default_rng(args.seed)

    model = None
    if args.backend == "torch":
        torch = __import__("torch")
        from multimodal.factory import fusion_model_for_module
        model = fusion_model_for_module(args.module)
        # fit court pour une performance représentative d'un modèle déployé
        samples = []
        for _ in range(24):
            payload = make_payload(rng)
            label = 1 if payload["tabulaire"]["features"][0] > 60 else 0
            samples.append((payload, label))
        model.fit(samples, epochs=args.fit_epochs, lr=2e-2)

    engine = engine_for_module(args.module)
    if model is None:
        infer_once = engine.infer
    else:
        def infer_once(modalities, _m=model):
            return _m.predict(modalities)

    # réchauffement (JIT, caches, allocation)
    for _ in range(args.warmup):
        infer_once(make_payload(rng, missing_ratio=args.missing_ratio))

    durations_ms: list[float] = []
    payload_bytes = 0
    for _ in range(args.requests):
        modalities = make_payload(rng, missing_ratio=args.missing_ratio)
        payload_bytes = len(json.dumps(modalities).encode())
        t0 = time.perf_counter_ns()
        infer_once(dict(modalities))
        durations_ms.append((time.perf_counter_ns() - t0) / 1e6)

    s = sorted(durations_ms)
    p50, p95, p99 = percentile(s, 50), percentile(s, 95), percentile(s, 99)
    mean = statistics.fmean(durations_ms)
    total_s = sum(durations_ms) / 1000.0
    verdict = "PASS" if p95 <= CRITIQUE_P95_MS else "FAIL"

    torch_version = None
    torch_device = None
    if args.backend == "torch":
        torch = __import__("torch")
        torch_version = torch.__version__
        torch_device = "cuda" if torch.cuda.is_available() else "cpu"

    return {
        "date": datetime.now(timezone.utc).isoformat(),
        "module": args.module,
        "backend": args.backend,
        "torch_version": torch_version,
        "device": torch_device,
        "requests": args.requests,
        "warmup": args.warmup,
        "missing_ratio": args.missing_ratio,
        "fit_epochs": args.fit_epochs if args.backend == "torch" else None,
        "payload_bytes_mean": payload_bytes,
        "latency_ms": {
            "p50": round(p50, 3), "p95": round(p95, 3), "p99": round(p99, 3),
            "mean": round(mean, 3), "min": round(s[0], 3),
            "max": round(s[-1], 3),
        },
        "throughput_req_per_s": round(args.requests / max(total_s, 1e-9), 1),
        "critique": {"p95_max_ms": CRITIQUE_P95_MS, "verdict": verdict},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--backend", choices=("numpy", "torch"), default="numpy")
    ap.add_argument("--module", type=int, default=8,
                    help="module 8 = cardiology (config de référence)")
    ap.add_argument("--requests", type=int, default=500)
    ap.add_argument("--warmup", type=int, default=20)
    ap.add_argument("--missing-ratio", type=float, default=0.0,
                    help="part de requêtes avec modalité imagerie absente")
    ap.add_argument("--fit-epochs", type=int, default=30)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("-o", "--output", default="",
                    help="écrire le résultat JSON dans ce fichier")
    args = ap.parse_args()

    result = bench(args)
    lat = result["latency_ms"]
    print(f"MEDISUITE banc d'inférence — module {args.module} "
          f"[{args.backend}"
          + (f" / {result['device']}" if result["device"] else "")
          + "]")
    print(f"  requêtes : {args.requests} (+{args.warmup} warm-up, "
          f"missing_ratio={args.missing_ratio})")
    print(f"  p50={lat['p50']:.2f} ms  p95={lat['p95']:.2f} ms  "
          f"p99={lat['p99']:.2f} ms")
    print(f"  mean={lat['mean']:.2f} ms  min={lat['min']:.2f} ms  "
          f"max={lat['max']:.2f} ms")
    print(f"  débit : {result['throughput_req_per_s']} req/s")
    ok = result["critique"]["verdict"] == "PASS"
    print(f"  critère EGSP p95 ≤ {CRITIQUE_P95_MS:.0f} ms : "
          f"{'PASS ✓' if ok else 'FAIL ✗'}")
    if args.output:
        pathlib.Path(args.output).write_text(
            json.dumps(result, indent=2, ensure_ascii=False))
        print(f"  JSON → {args.output}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
