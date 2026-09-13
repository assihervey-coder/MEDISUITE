"""Fusion torch ENTRAÎNABLE de bout en bout (v0.3, ADR 0023).

Extension de l'ADR 0022 : en v0.2 seules les projections des encodeurs étaient
des ``nn.Linear`` (poids copiés depuis le socle NumPy stable). En v0.3, le
TRONC complet devient un ``torch.nn.Module`` entraînable :

- ``TorchCrossAttention`` : attention croisée multi-têtes (Wq/Wk/Wv/Wo) ;
- ``TorchTaskHead``       : tête de tâche entraînable (binaire / multiclasse /
  régression) ;
- ``TorchFusionModel``    : assemblage complet (projections + attention +
  portes sigmoid + requête globale + tête) avec ``fit()`` (Adam, ordre fixe),
  ``predict()`` (sortie structurée identique à ``FusionEngine.infer``) et
  checkpoints natifs ``state_dict`` (save/load).

Garantie de continuité (pattern ADR 0022 étendu au tronc) : à
l'INITIALISATION, tous les paramètres sont copiés depuis les poids
déterministes NumPy v0.1 — la sortie torch est numériquement identique au
socle (au flottement matriciel), et les tests de régression v0.1 restent la
référence. Le modèle diverge du socle uniquement dès la première mise à jour
de gradient — c'est un SUR-ENSEMBLE entraînable du moteur NumPy.

Frontière d'apprentissage (honnêteté IEC 62304) :
- GELÉ        : la tokenisation des encodeurs (``BaseEncoder._to_tokens``),
  extraction déterministe auditable, sans paramètre ;
- ENTRAÎNABLE : projections, attention (multi-têtes), portes, requête
  globale, tête de tâche.

Zéro RNG : AUCUN paramètre n'est initialisé aléatoirement (tout est copié
depuis les graines fixées v0.1) → reproductibilité clinique préservée.

NB : ce module requiert PyTorch (import explicite, message d'installation
claire). Le socle NumPy reste importable et testable SANS torch — ce module
n'est jamais importé par le cœur (cf. factory, import paresseux).
"""
from __future__ import annotations

import numpy as np

from .backends import _require_torch
from .cross_attention import CrossAttentionBlock
from .modality_encoder import BaseEncoder
from ..heads.heads import BinaryHead, MulticlassHead, RegressionHead

torch = _require_torch()          # échec précoce avec message d'installation
nn = torch.nn

TRAINABLE_TASKS = {"classification", "multiclass", "regression"}


# ── Blocs entraînables ────────────────────────────────────────────────────────

class TorchCrossAttention(nn.Module):
    """Attention croisée multi-têtes entraînable, initialisée depuis NumPy.

    Math (h têtes, dh = d/h) :
        q_h = Wq_h(query) ; k_h, v_h = Wk_h / Wv_h (kv_seq)
        scores_h = k_h · q_h / √dh ; attn_h = softmax ; ctx = ⊕_h(attn_h · v_h)
        out = LayerNorm(query + ctx @ Wo)   (LN sans affine, eps 1e-6 — = NumPy)
    Avec h=1 (dh = d) : EXACTEMENT le calcul de ``CrossAttentionBlock`` —
    équivalence numérique vérifiée par test (rtol 1e-6).
    """

    def __init__(self, block: CrossAttentionBlock, heads: int = 1) -> None:
        super().__init__()
        d = block.d_model
        if not (1 <= heads <= d and d % heads == 0):
            raise ValueError(f"heads={heads} doit diviser d_model={d} et "
                             "être dans [1, d_model]")
        self.h, self.d, self.dh = heads, d, d // heads
        # nn.Linear calcule x @ W.T → poids = W_numPy.T (copie exacte)
        self.Wq = nn.Linear(d, d, bias=False, dtype=torch.float64)
        self.Wk = nn.Linear(d, d, bias=False, dtype=torch.float64)
        self.Wv = nn.Linear(d, d, bias=False, dtype=torch.float64)
        self.Wo = nn.Linear(d, d, bias=False, dtype=torch.float64)
        with torch.no_grad():
            self.Wq.weight.copy_(torch.from_numpy(block.Wq.T))
            self.Wk.weight.copy_(torch.from_numpy(block.Wk.T))
            self.Wv.weight.copy_(torch.from_numpy(block.Wv.T))
            self.Wo.weight.copy_(torch.from_numpy(block.Wo.T))

    def forward(self, query, kv_seq):
        """query (d,) ; kv_seq (T, d) → (out (d,), attn (h, T))."""
        h, dh = self.h, self.dh
        q = self.Wq(query).view(h, dh)                        # (h, dh)
        k = self.Wk(kv_seq).view(-1, h, dh).transpose(0, 1)   # (h, T, dh)
        v = self.Wv(kv_seq).view(-1, h, dh).transpose(0, 1)   # (h, T, dh)
        scores = torch.einsum("htd,hd->ht", k, q) / (dh ** 0.5)
        attn = torch.softmax(scores, dim=-1)                  # (h, T)
        ctx = torch.einsum("ht,htd->hd", attn, v).reshape(-1)  # (d,)
        out = nn.functional.layer_norm(
            query + self.Wo(ctx), (self.d,), eps=1e-6)
        return out, attn


class TorchTaskHead(nn.Module):
    """Tête de tâche entraînable : binaire (sigmoid), multiclasse (softmax),
    régression (scalaire). survival/segmentation restent des gabarits NumPy."""

    _EXPECTED = {"classification": BinaryHead, "multiclass": MulticlassHead,
                 "regression": RegressionHead}

    def __init__(self, task: str, source) -> None:
        super().__init__()
        expected = self._EXPECTED.get(task)
        if expected is not None and not isinstance(source, expected):
            raise ValueError(f"incohérence tâche '{task}' / tête "
                             f"'{type(source).__name__}'")
        if isinstance(source, BinaryHead):
            self.w = nn.Parameter(torch.tensor(np.asarray(source.w),
                                               dtype=torch.float64))
            self.b = nn.Parameter(torch.tensor(float(source.b),
                                               dtype=torch.float64))
            self.out = "binaire"
        elif isinstance(source, MulticlassHead):
            self.W = nn.Parameter(torch.tensor(np.asarray(source.W),
                                               dtype=torch.float64))
            self.out = "multiclasse"
        elif isinstance(source, RegressionHead):
            self.w = nn.Parameter(torch.tensor(np.asarray(source.w),
                                               dtype=torch.float64))
            self.out = "regression"
        else:
            raise NotImplementedError(
                f"tête '{type(source).__name__}' non entraînable en v0.3 — "
                "tâches entraînables : classification|multiclass|regression")

    def forward(self, fused):
        if self.out == "binaire":
            logit = fused @ self.w + self.b
            return {"logit": logit, "probs": torch.sigmoid(logit)}
        if self.out == "multiclasse":
            logits = fused @ self.W
            return {"logits": logits, "probs": torch.softmax(logits, dim=-1)}
        return {"valeur": fused @ self.w}


# ── Modèle complet ────────────────────────────────────────────────────────────

class TorchFusionModel(nn.Module):
    """Fusion multimodale torch entraînable de bout en bout (nn.Module).

    Usage :
        model = TorchFusionModel(engine)             # poids copiés du socle
        history = model.fit(samples, epochs=50)      # [(payloads, y), …]
        out = model.predict({"tabulaire": {...}, "imaging_2d": {...}})
        model.save("fusion.pt") ; model.load_checkpoint("fusion.pt")
    """

    def __init__(self, engine, heads: int = 1) -> None:
        super().__init__()
        if engine.task not in TRAINABLE_TASKS:
            raise NotImplementedError(
                f"tâche '{engine.task}' non entraînable en v0.3 — attendues : "
                f"{sorted(TRAINABLE_TASKS)} (socle NumPy inchangé sinon)")
        self.engine = engine
        self.task = engine.task
        self.d_model = engine.d_model
        self.modalities = list(engine.dims)            # ordre canonique
        self._idx = {m: i for i, m in enumerate(self.modalities)}
        self.heads = heads

        # projections ENTRAÎNABLES, initialisées depuis P stable des encodeurs
        self.projectors = nn.ModuleDict({
            m: nn.Linear(enc.feature_dim, enc.d_model, bias=False,
                         dtype=torch.float64)
            for m, enc in engine.encoders.items()})

        # attention multi-têtes (poids copiés des blocs NumPy)
        self.attention = nn.ModuleDict({
            m: TorchCrossAttention(engine.attention[m], heads)
            for m in self.modalities})

        # portes sigmoid APPRISES + requête globale APPRISE (copiées du socle)
        init_gates = [float(engine.gated.gates[m]) for m in self.modalities]
        self.gates = nn.Parameter(torch.tensor(init_gates, dtype=torch.float64))
        self.global_query = nn.Parameter(
            torch.tensor(np.asarray(engine.global_query), dtype=torch.float64))

        # tête de tâche entraînable (copiée du socle)
        self.head = TorchTaskHead(self.task, engine.head)

        with torch.no_grad():
            for m, enc in engine.encoders.items():
                self.projectors[m].weight.copy_(torch.from_numpy(enc.P.T))

    # ── pipeline partagé train / inférence ───────────────────────────────────
    def _tokenize(self, m: str, payload) -> np.ndarray:
        """Tokenisation NumPy GELÉE (réplique exacte de BaseEncoder.encode)."""
        enc: BaseEncoder = self.engine.encoders[m]
        target = enc.seq_len * enc.feature_dim
        tokens = np.asarray(enc._to_tokens(payload),
                            dtype=np.float64).reshape(-1)[:target]
        tokens = np.pad(tokens, (0, target - len(tokens)))
        return tokens.reshape(enc.seq_len, enc.feature_dim)

    def _fuse(self, present: list[str], token_cache: dict):
        """token_cache {m: (T, feature_dim)} → (fused, poids_t, imp_t, attns)."""
        summaries, attns = {}, {}
        for m in present:
            proj = self.projectors[m](token_cache[m])     # (T, d) ENTRAÎNABLE
            ctx, attn = self.attention[m](self.global_query, proj)
            summaries[m], attns[m] = ctx, attn
        order = [m for m in self.modalities if m in summaries]
        sel = torch.stack([self.gates[self._idx[m]] for m in order])
        w = torch.sigmoid(sel)                            # (P,)
        fused = sum(w[i] * summaries[m] for i, m in enumerate(order))
        imp = w / w.sum()
        return fused, w, imp, attns

    # ── entraînement ─────────────────────────────────────────────────────────
    def fit(self, samples: list, epochs: int = 50, lr: float = 1e-2,
            verbose: bool = False) -> list[float]:
        """Boucle d'entraînement déterministe (Adam, ordre fixe, float64).

        samples : [(payloads {modalité: payload}, y)] — y : 0/1 (binaire),
        0..K-1 (multiclasse), float (régression). Tokenisation (gelée)
        pré-calculée UNE fois. Retourne la perte moyenne par epoch.
        """
        if not samples:
            raise ValueError("aucun échantillon d'entraînement")
        tokenized = [({m: torch.tensor(self._tokenize(m, pl[m]),
                                       dtype=torch.float64) for m in pl}, y)
                     for pl, y in samples]
        targets = torch.tensor([float(y) for _, y in tokenized],
                               dtype=torch.float64)
        fnl = nn.functional
        if self.head.out == "binaire":
            loss_fn = fnl.binary_cross_entropy_with_logits
        elif self.head.out == "multiclasse":
            loss_fn = lambda logits, t: fnl.cross_entropy(      # noqa: E731
                logits.unsqueeze(0), t.long().unsqueeze(0))
        else:
            loss_fn = lambda valeur, t: (valeur - t) ** 2       # noqa: E731
        opt = torch.optim.Adam(self.parameters(), lr=lr)
        history: list[float] = []
        self.train()
        for _epoch in range(int(epochs)):
            losses = []
            for (tok, _), t in zip(tokenized, targets):
                opt.zero_grad()
                present = [m for m in self.modalities if m in tok]
                fused, _w, _imp, _attns = self._fuse(present, tok)
                out = self.head(fused)
                pred = (out["logit"] if self.head.out == "binaire"
                        else out.get("logits", out.get("valeur")))
                loss = loss_fn(pred, t)
                loss.backward()
                opt.step()
                losses.append(float(loss.detach()))
            history.append(sum(losses) / len(losses))
            if verbose:
                print(f"epoch {_epoch + 1:3d}/{epochs} — perte "
                      f"{history[-1]:.6f}")
        self.eval()
        return history

    # ── inférence structurée (drop-in du socle) ──────────────────────────────
    def predict(self, modalities: dict) -> dict:
        """Sortie structurée aux CLÉS IDENTIQUES à ``FusionEngine.infer``."""
        engine = self.engine
        unknown = [m for m in modalities if m not in self._idx]
        if unknown:
            raise ValueError(f"modalités inconnues : {unknown} — "
                             f"connues : {sorted(self._idx)}")
        provided = [m for m in self.modalities if m in modalities]
        if not provided:
            raise ValueError("aucune modalité exploitable")
        report = engine.handler.analyze(provided)
        with torch.no_grad():
            token_cache = {m: torch.tensor(self._tokenize(m, modalities[m]),
                                           dtype=torch.float64)
                           for m in report.modalites_presentes}
            fused, w, imp, _attns = self._fuse(report.modalites_presentes,
                                               token_cache)
            out = self.head(fused)
            # recalibrage de confiance (ADR-0018) — portes courantes, TOUTES mod.
            all_w = {m: float(torch.sigmoid(self.gates[self._idx[m]]))
                     for m in self.modalities}
            adj = engine.handler.confidence_adjustment(
                report.modalites_presentes, all_w)
            if self.head.out == "binaire":
                prob = float(out["probs"])
                prediction = {"classe": 1 if prob >= 0.5 else 0,
                              "probabilite": round(prob, 4), "seuil": 0.5}
            elif self.head.out == "multiclasse":
                probs = [round(float(x), 4) for x in out["probs"]]
                prediction = {"classe": int(torch.argmax(out["logits"])),
                              "probabilites": probs}
            else:
                prediction = {"valeur": round(float(out["valeur"]), 4)}
            importance = {m: round(100 * float(imp[i]), 1)
                          for i, m in enumerate(provided)}
            gates_round = {m: round(float(w[i]), 3)
                           for i, m in enumerate(provided)}
        return {
            "task": self.task,
            "prediction": prediction,
            "confiance": round(min(1.0, 0.5 + 0.5 * adj), 3),
            "modalites_manquantes": report.to_dict(),
            "modality_importance_pct": importance,
            "detail": {"d_model": self.d_model,
                       "modalites_encodees": len(provided),
                       "gates": gates_round,
                       "backend": "torch_fusion",
                       "heads": self.heads},
        }

    # ── persistance (checkpoints natifs + métadonnées) ───────────────────────
    def save(self, path: str) -> None:
        """Checkpoint : state_dict natif + métadonnées (traçabilité IEC 62304)."""
        torch.save(
            {"state_dict": self.state_dict(),
             "meta": {"format": "medisuite-fusion-0.3", "task": self.task,
                      "d_model": self.d_model, "heads": self.heads,
                      "modalities": self.modalities}}, path)

    def load_checkpoint(self, path: str) -> dict:
        """Restaure les tenseurs (in-place) ; retourne les métadonnées."""
        blob = torch.load(path, weights_only=True)
        self.load_state_dict(blob["state_dict"])
        return blob.get("meta", {})
