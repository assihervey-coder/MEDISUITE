"""Télémétrie OpenTelemetry — observabilité native des 38 services. v0.4.

Implémentation stdlib d'un sous-ensemble OTel suffisamment complet pour la
production hospitalière (contrainte « stdlib d'abord » du repo) :

1. **Propagation W3C Trace Context** (`traceparent`) — interopérable avec
   l'écosystème OTel standard (SDK Java/Node/Python, Envoy, NGINX OTel).
2. **Spans serveur** créés par le middleware de `medisuite_core.http` pour
   chaque requête HTTP : méthode, route, statut, durée.
3. **Export OTLP/HTTP JSON** vers un collecteur OpenTelemetry
   (endpoint `MEDISUITE_OTEL_ENDPOINT`, ex. http://otel-collector:4318/v1/traces)
   via un thread d'arrière-plan par lots (batch), non bloquant.
4. **Dégradation gracieuse** : sans endpoint configuré, les spans restent
   visibles dans le tampon local (diagnostic `__main__`/tests) et l'export
   est un no-op — jamais d'exception, jamais de ralentissement du service.
5. **Échantillonnage (ADR-0025, v0.8)** : head sampling déterministe
   parent-based — la décision suit le parent W3C s'il existe, sinon un
   ratio déterministe sur le trace_id (env `MEDISUITE_OTEL_SAMPLING_RATIO`,
   défaut 1.0) ; les spans en erreur sont TOUJOURS conservés ; les routes
   de bruit (probes /health, /ready, /metrics) ne produisent pas de span.

Format d'export : OTLP traces v1 (protobuf JSON mapping) tel qu'attendu par
`otel/opentelemetry-collector-contrib` sur le receiver `otlp/http`.
"""
from __future__ import annotations

import json
import os
import threading
import time
import urllib.request
from collections import deque
from typing import Any

TRACEPARENT_VERSION = "00"
_RANDOM_FLAGS = "01"  # sampled

# Routes de bruit (ADR-0025) : sondes K8s/compose tirées quelques fois par
# minute par service — tracer des spans pour elles noierait les traces
# métier sans aucune valeur diagnostique.
NOISE_ROUTES = frozenset({"/health", "/ready", "/metrics"})

# Tailles W3C : trace-id 32 hex, span-id 16 hex
_HEX = "0123456789abcdef"


def _hex_random(n: int, rng=None) -> str:
    import random as _r
    r = rng or _r.SystemRandom()
    return "".join(r.choice(_HEX) for _ in range(n))


# ── W3C Trace Context ─────────────────────────────────────────────────────────
def parse_traceparent(value: str | None) -> dict | None:
    """Parse un header traceparent W3C → {trace_id, parent_span_id, flags}.

    Format : `00-<32 hex trace-id>-<16 hex span-id>-<2 hex flags>`.
    Retourne None pour tout header invalide (résilience W3C §3.2.2).
    """
    if not value:
        return None
    parts = value.strip().split("-")
    if len(parts) != 4 or parts[0] != TRACEPARENT_VERSION:
        return None
    trace_id, span_id, flags = parts[1], parts[2], parts[3]
    if len(trace_id) != 32 or len(span_id) != 16 or len(flags) != 2:
        return None
    if not all(c in _HEX for c in trace_id + span_id + flags):
        return None
    if all(c == "0" for c in trace_id) or all(c == "0" for c in span_id):
        return None  # interdit par W3C
    return {"trace_id": trace_id, "parent_span_id": span_id, "flags": flags}


def format_traceparent(trace_id: str, span_id: str, flags: str = "01") -> str:
    """Construit un header traceparent W3C valide."""
    return f"{TRACEPARENT_VERSION}-{trace_id}-{span_id}-{flags}"


# ── Spans ─────────────────────────────────────────────────────────────────────
class Span:
    """Span OTel minimal (attributs, statut, horodatage ns)."""

    __slots__ = ("trace_id", "span_id", "parent_span_id", "name", "kind",
                 "start_ns", "end_ns", "attributes", "status", "error",
                 "sampled")

    def __init__(self, trace_id: str, span_id: str, name: str,
                 parent_span_id: str = "", kind: str = "SPAN_KIND_SERVER",
                 sampled: bool = True) -> None:
        self.trace_id = trace_id
        self.span_id = span_id
        self.parent_span_id = parent_span_id
        self.name = name
        self.kind = kind
        self.start_ns = time.time_ns()
        self.end_ns = 0
        self.attributes: dict[str, Any] = {}
        self.status = "STATUS_CODE_OK"
        self.error = False
        self.sampled = sampled  # décision ADR-0025

    def set_attribute(self, key: str, value: Any) -> None:
        self.attributes[key] = value

    def end(self, ok: bool = True) -> None:
        self.end_ns = time.time_ns()
        self.status = "STATUS_CODE_OK" if ok else "STATUS_CODE_ERROR"
        self.error = not ok

    def to_otlp(self, service_name: str) -> dict:
        attrs = [{"key": k, "value": ({"intValue": v} if isinstance(v, int)
                                      else {"doubleValue": v} if isinstance(v, float)
                                      else {"boolValue": v} if isinstance(v, bool)
                                      else {"stringValue": str(v)})}
                 for k, v in self.attributes.items()]
        span: dict[str, Any] = {
            "traceId": self.trace_id,
            "spanId": self.span_id,
            "name": self.name,
            "kind": self.kind,
            "startTimeUnixNano": str(self.start_ns),
            "endTimeUnixNano": str(self.end_ns or time.time_ns()),
            "status": {"code": self.status},
        }
        if self.parent_span_id:
            span["parentSpanId"] = self.parent_span_id
        if attrs:
            span["attributes"] = attrs
        return span


class Tracer:
    """Tracer par service : spans en mémoire + export OTLP/HTTP par lots."""

    def __init__(self, service_name: str, endpoint: str | None = None,
                 batch_size: int = 64, flush_interval_s: float = 2.0,
                 sampling_ratio: float | None = None) -> None:
        self.service_name = service_name
        self.endpoint = (endpoint or os.environ.get(
            "MEDISUITE_OTEL_ENDPOINT", "")).strip()
        self.batch_size = batch_size
        self.flush_interval_s = flush_interval_s
        self.noise_routes: frozenset[str] = NOISE_ROUTES
        self.sampling_ratio = _resolve_ratio(sampling_ratio)
        self._buffer: deque[Span] = deque(maxlen=2048)
        self._lock = threading.Lock()
        self._opener = None  # injection pour tests
        self.exported_batches = 0
        self.dropped = 0
        self.sampling_dropped = 0
        if self.endpoint:
            t = threading.Thread(target=self._worker, daemon=True)
            t.name = f"otel-export-{service_name}"
            t.start()

    # ── échantillonnage (ADR-0025) ───────────────────────────────────
    def should_sample(self, trace_id: str,
                      parent_flags: str | None = None) -> tuple[bool, str]:
        """Décision head-sampling déterministe.

        - parent W3C présent : sa décision prévaut (ParentBased) — bit 0 des
          flags (les autres bits sont réservés) ;
        - racine : ratio appliqué de façon DÉTERMINISTE sur le trace_id
          (16 premiers hex < ratio × 2^64) — tous les spans d'une même trace
          prennent la même décision sans coordination inter-services.
        """
        if parent_flags is not None:
            sampled = (int(parent_flags, 16) & 1) == 1
            return sampled, "parent_sampled" if sampled else "parent_unsampled"
        threshold = int(self.sampling_ratio * (1 << 64))
        if int(trace_id[:16], 16) < threshold:
            return True, "ratio_sampled"
        return False, "ratio_dropped"

    # ── création de spans ────────────────────────────────────────────────────
    def start_server_span(self, name: str, traceparent: str | None = None) -> Span:
        """Crée un span serveur en poursuivant (ou initiant) une trace W3C.

        La décision d'échantillonnage est prise ICI (head sampling) et
        tracée dans l'attribut `otel.sampling.decision`.
        """
        ctx = parse_traceparent(traceparent)
        if ctx:
            sampled, decision = self.should_sample(ctx["trace_id"],
                                                   ctx["flags"])
            span = Span(ctx["trace_id"], _hex_random(16), name,
                        parent_span_id=ctx["parent_span_id"],
                        sampled=sampled)
        else:
            trace_id = _hex_random(32)
            sampled, decision = self.should_sample(trace_id, None)
            span = Span(trace_id, _hex_random(16), name, sampled=sampled)
        span.set_attribute("otel.sampling.decision", decision)
        return span

    def record(self, span: Span) -> None:
        """Conserve le span terminé dans le tampon (overflow → drop compté).

        ADR-0025 : un span non échantillonné n'est PAS enregistré — sauf en
        erreur (always-on errors : un incident n'est jamais échantillonné
        hors des données de télémétrie).
        """
        if not span.sampled and not span.error:
            with self._lock:
                self.sampling_dropped += 1
            return
        with self._lock:
            if len(self._buffer) == self._buffer.maxlen:
                self.dropped += 1
            self._buffer.append(span)

    # ── export OTLP/HTTP JSON ────────────────────────────────────────────────
    def _otlp_payload(self, spans: list[Span]) -> dict:
        spans_json = [s.to_otlp(self.service_name) for s in spans]
        return {"resourceSpans": [{
            "resource": {"attributes": [
                {"key": "service.name",
                 "value": {"stringValue": self.service_name}},
                {"key": "service.namespace", "value": {"stringValue": "medisuite"}},
                {"key": "telemetry.sdk.name", "value": {"stringValue": "medisuite-core"}},
            ]},
            "scopeSpans": [{"scope": {"name": "medisuite-core.observability",
                                      "version": "0.4.0"},
                            "spans": spans_json}],
        }]}

    def export_now(self, limit: int = 0) -> int:
        """Export synchrone (tests / arrêt propre) : renvoie le nb de spans envoyés."""
        with self._lock:
            if not self._buffer:
                return 0
            items: list[Span] = []
            while self._buffer and (limit == 0 or len(items) < limit):
                items.append(self._buffer.popleft())
        payload = self._otlp_payload(items)
        req = urllib.request.Request(self.endpoint, method="POST")
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps(payload).encode("utf-8")
        urlopen = self._opener or urllib.request.urlopen
        with urlopen(req, timeout=2.0) as resp:
            resp.read()
        self.exported_batches += 1
        return len(items)

    def _worker(self) -> None:
        """Thread d'arrière-plan : export par lots, silencieux en cas d'erreur."""
        while True:
            time.sleep(self.flush_interval_s)
            try:
                with self._lock:
                    pending = len(self._buffer)
                if pending >= self.batch_size:
                    self.export_now(limit=max(self.batch_size, pending))
            except Exception:
                # Pas d'exception fatale : la télémétrie ne doit jamais
                # dégrader le service (réseau collecteur instable, redéploiement…)
                with self._lock:
                    if len(self._buffer) == self._buffer.maxlen:
                        self._buffer.popleft()
                time.sleep(self.flush_interval_s * 4)

    def snapshot(self) -> dict:
        """Diagnostic : état du tampon et de l'export (exposé sur /health étendu)."""
        with self._lock:
            pending = len(self._buffer)
        return {"service": self.service_name, "endpoint": self.endpoint or None,
                "pending_spans": pending, "exported_batches": self.exported_batches,
                "dropped": self.dropped,
                "sampling_ratio": self.sampling_ratio,
                "sampling_dropped": self.sampling_dropped}


# ── Résolution du ratio (ADR-0025) ───────────────────────────────────────
def _resolve_ratio(value: float | None) -> float:
    """Ratio ∈ [0,1] ; défaut env MEDISUITE_OTEL_SAMPLING_RATIO sinon 1.0.

    Valeur invalide → 1.0 : en télémétrie, une mauvaise configuration ne
    doit pas SUPPRIMER les données (fail-open observability, assumé ADR).
    """
    if value is not None:
        raw = str(value).strip() or "1.0"
    else:
        raw = os.environ.get("MEDISUITE_OTEL_SAMPLING_RATIO", "1.0").strip() or "1.0"
    try:
        return min(1.0, max(0.0, float(raw)))
    except ValueError:
        return 1.0


# ── Singleton par service (configuré par env) ─────────────────────────────────
_default: Tracer | None = None
_default_lock = threading.Lock()


def get_tracer(service_name: str) -> Tracer:
    """Tracer partagé du process — no-op d'export sans MEDISUITE_OTEL_ENDPOINT."""
    global _default
    with _default_lock:
        if _default is None:
            _default = Tracer(service_name)
        return _default
