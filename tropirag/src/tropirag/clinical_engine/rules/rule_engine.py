"""Moteur de règles cliniques déterministe — le cœur de l'autorité TropiRAG.

DSL de conditions (YAML) :

    when:
      all:                       # ET
        - symptom: fever
        - any:                   # OU
            - symptom: headache
            - symptom: myalgia
      not: {exposure: malaria_exposure}

Feuilles supportées :
    symptom / symptom_any / exposure / vital (gte/lte/gt/lt/eq)
    lab / lab_numeric / patient / incubation / travel / not / all / any / n_of

Aucune IA n'intervient ici. Chaque règle porte ses références de preuve.
"""
from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from typing import Any

import yaml

from tropirag.core.constants import INCUBATION_WINDOWS_DAYS
from tropirag.core.enums import RuleActionType
from tropirag.core.errors import RuleEvaluationError, RuleLoadError
from tropirag.core.identifiers import fingerprint
from tropirag.domain.clinical_case.entities import ClinicalCase
from tropirag.core.datetime import days_between


# ---------------------------------------------------------------------------
# Contexte d'évaluation
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class EvalContext:
    case: ClinicalCase
    suspected: set[str] = field(default_factory=set)      # maladies suspectées (passe 1)
    red_flag_codes: set[str] = field(default_factory=set)  # red flags posés (passe 2)

    @property
    def symptoms(self) -> set[str]:
        return self.case.symptom_codes()

    @property
    def severe_symptoms(self) -> set[str]:
        return {s.code for s in self.case.severe_symptoms()}


# ---------------------------------------------------------------------------
# Évaluation des conditions
# ---------------------------------------------------------------------------

_COMPARATORS = ("gte", "lte", "gt", "lt", "eq")


def _num(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _match_scalar(actual: str | None, expected: str) -> bool:
    """Valeur attendue : exacte, liste, ou joker ('positive|reactive')."""
    if actual is None:
        return False
    if "|" in expected:
        return any(_match_scalar(actual, p) for p in expected.split("|"))
    if expected.startswith("~"):
        return fnmatch.fnmatch(actual.lower(), expected[1:].lower())
    return actual.lower() == expected.lower()


def evaluate_condition(cond: Any, ctx: EvalContext) -> bool:  # noqa: C901
    """Évalue récursivement l'arbre de conditions — purement déterministe."""
    if cond is None:
        return True
    if isinstance(cond, bool):
        return cond

    if not isinstance(cond, dict):
        raise RuleEvaluationError(f"Condition invalide (attendu dict): {cond!r}")

    # --- combinateurs -------------------------------------------------------
    if "all" in cond:
        return all(evaluate_condition(c, ctx) for c in cond["all"])
    if "any" in cond:
        return any(evaluate_condition(c, ctx) for c in cond["any"])
    if "n_of" in cond:
        spec = cond["n_of"]
        n, of = spec.get("n", 1), spec.get("of", [])
        return sum(1 for c in of if evaluate_condition(c, ctx)) >= n
    if "not" in cond:
        return not evaluate_condition(cond["not"], ctx)

    # --- symptômes ------------------------------------------------------------
    if "symptom" in cond:
        code = str(cond["symptom"])
        if not ctx.symptoms.__contains__(code):
            return False
        want_sev = cond.get("severity")
        if want_sev == "severe":
            return code in ctx.severe_symptoms
        return True
    if "symptom_any" in cond:
        return any(str(c) in ctx.symptoms for c in cond["symptom_any"])
    if "symptom_count_gte" in cond:
        return len(ctx.symptoms) >= int(cond["symptom_count_gte"])

    # --- expositions (résumé voyage) -------------------------------------------
    if "exposure" in cond:
        return bool(getattr(ctx.case.exposures, str(cond["exposure"]), False))
    if "exposure_risk_gte" in cond:
        spec = cond["exposure_risk_gte"]
        disease, level = spec.get("disease"), spec.get("level", "moderate")
        rank = {"none": 0, "low": 1, "moderate": 2, "high": 3, "outbreak": 4}
        actual = getattr(ctx.case.exposures, f"{disease}_exposure", "none")
        if disease == "malaria":
            actual = getattr(ctx.case.exposures, "malaria_intensity", "none")
        return rank.get(actual, 0) >= rank.get(level, 2)

    # --- constantes --------------------------------------------------------------
    if "vital" in cond:
        vital = str(cond["vital"])
        actual = getattr(ctx.case.vitals, vital, None)
        if actual is None:
            return False
        for comp in _COMPARATORS:
            if comp in cond:
                n = _num(cond[comp])
                a = _num(actual)
                if a is None or n is None:
                    return False
                return {"gte": a >= n, "lte": a <= n, "gt": a > n, "lt": a < n, "eq": a == n}[comp]
        return False

    # --- biologie ---------------------------------------------------------------
    if "lab" in cond:
        spec = cond
        code = str(spec.get("lab"))
        comp = spec.get("component")
        result = None
        for r in ctx.case.lab_results:
            if r.test_code == code and (comp is None or comp in (r.raw.get("component") or "").lower()):
                result = r
                break
        if result is None:
            expected = spec.get("value")
            return False if expected else False
        if "value" in spec:
            return _match_scalar(result.value, str(spec["value"]))
        for op in _COMPARATORS:
            if op in spec:
                a, n = _num(result.numeric), _num(spec[op])
                if a is None or n is None:
                    return False
                return {"gte": a >= n, "lte": a <= n, "gt": a > n, "lt": a < n, "eq": a == n}[op]
        return False
    if "lab_missing" in cond:
        return ctx.case.test(str(cond["lab_missing"])) is None
    if "lab_numeric" in cond:
        spec = cond["lab_numeric"]
        code = str(spec.get("test", spec.get("code")))
        comp = spec.get("component")
        val = ctx.case.lab_value(code, comp)
        if val is None:
            return False
        for op in _COMPARATORS:
            if op in spec:
                n = _num(spec[op])
                if n is None:
                    return False
                return {"gte": val >= n, "lte": val <= n, "gt": val > n, "lt": val < n, "eq": val == n}[op]
        return False

    # --- patient ------------------------------------------------------------------
    if "patient" in cond:
        flag = str(cond["patient"])
        p = ctx.case.patient
        return {
            "child": p.is_child(),
            "infant": p.is_infant(),
            "pregnant": p.is_pregnant_or_possible(),
            "female_childbearing": p.is_female_childbearing(),
            "adult_male": p.sex == "male" and (p.age_years or 30) >= 15,
            "elderly": (p.age_years or 0) >= 65,
            "sickle_cell": p.has_sickle_cell_disease(),
            "immunocompromised": p.has_condition("viH") or p.has_condition("immuno") or p.has_condition("cancer"),
            "diabetes": p.has_condition("diab"),
            # V1.1 — grossesse fine / drépanocytose / G6PD
            "first_trimester": p.is_first_trimester(),
            "second_trimester": p.is_second_trimester(),
            "third_trimester": p.is_third_trimester(),
            "g6pd_deficient": p.has_condition("g6pd") or p.has_condition("deficit en g6pd")
                              or p.has_condition("glucose-6-phosphate"),
        }.get(flag, False)
    if "condition" in cond:
        return ctx.case.patient.has_condition(str(cond["condition"]))
    # V1.3 — âge fin (pédiatrie) : patient_age: {lt: 5} / {gte: 65}...
    # Nourrissons : age_months/12 utilisé quand age_years est absent.
    if "patient_age" in cond:
        spec = cond["patient_age"]
        p = ctx.case.patient
        a = p.age_years
        if a is None and p.age_months is not None:
            a = p.age_months / 12.0
        if a is None:
            return False  # âge inconnu → ne pas déclencher une règle âge-dépendante
        for op in _COMPARATORS:
            if op in spec:
                n = _num(spec[op])
                if n is None:
                    return False
                return {"gte": a >= n, "lte": a <= n, "gt": a > n, "lt": a < n, "eq": a == n}[op]
        return False

    # --- temporel --------------------------------------------------------------------
    if "incubation" in cond:
        key = str(cond["incubation"])
        window = INCUBATION_WINDOWS_DAYS.get(key)
        if not window or ctx.case.timeline is None:
            return True  # pas d'info → ne pas exclure
        compatible = ctx.case.timeline.in_incubation_context(window)
        return compatible if cond.get("compatible", True) else not compatible
    if "days_since_return" in cond:
        spec = cond["days_since_return"]
        if ctx.case.timeline is None:
            return False
        d = ctx.case.timeline.days_since_return()
        if d is None:
            return False
        for op in _COMPARATORS:
            if op in spec:
                n = _num(spec[op])
                if n is None:
                    return False
                return {"gte": d >= n, "lte": d <= n, "gt": d > n, "lt": d < n, "eq": d == n}[op]
        return False
    if "symptom_duration_days" in cond:
        spec = cond["symptom_duration_days"]
        durs = [s.duration_days for s in ctx.case.symptoms if s.duration_days is not None]
        if not durs:
            onset = ctx.case.timeline.anchor.symptom_onset if ctx.case.timeline else None
            d = days_between(onset, ctx.case.consultation_date)
            durs = [d] if d is not None else []
        if not durs:
            return False
        dmax = max(durs)
        for op in _COMPARATORS:
            if op in spec:
                n = _num(spec[op])
                if n is None:
                    return False
                return {"gte": dmax >= n, "lte": dmax <= n, "gt": dmax > n, "lt": dmax < n, "eq": dmax == n}[op]
        return False
    if "fever_duration_days" in cond:
        # durée de fièvre : onset → consultation
        spec = cond["fever_duration_days"]
        tl = ctx.case.timeline
        if tl is None:
            return False
        d = tl.anchor.days_since_onset
        if d is None:
            return False
        for op in _COMPARATORS:
            if op in spec:
                n = _num(spec[op])
                if n is None:
                    return False
                return {"gte": d >= n, "lte": d <= n, "gt": d > n, "lt": d < n, "eq": d == n}[op]
        return False

    # --- dépendances entre règles -------------------------------------------------
    if "disease" in cond:
        # vrai si la maladie est déjà suspectée (passe raise_suspicion déjà exécutée)
        return str(cond["disease"]) in ctx.suspected
    if "red_flag_code" in cond:
        return str(cond["red_flag_code"]) in ctx.red_flag_codes

    # --- voyage brut --------------------------------------------------------------
    if "travel" in cond:
        flag = str(cond["travel"])
        s = ctx.case.exposures
        return bool(getattr(s, flag, False))

    raise RuleEvaluationError(f"Condition inconnue: {list(cond.keys())}")


# ---------------------------------------------------------------------------
# Règles
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class Rule:
    id: str
    action: str                      # RuleActionType value
    priority: int = 50
    weight: float = 0.5
    disease: str | None = None
    description: str = ""
    when: Any = None
    then: dict = field(default_factory=dict)
    evidence: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        try:
            RuleActionType(self.action)
        except ValueError as e:
            raise RuleLoadError(f"Action inconnue '{self.action}' dans règle {self.id}") from e

    def evaluate(self, ctx: EvalContext) -> bool:
        return evaluate_condition(self.when, ctx)

    def key(self) -> str:
        return f"{self.id}:{fingerprint(self.id, self.action, self.priority, self.weight)}"


@dataclass(slots=True)
class RuleOutcome:
    rule: Rule
    matched: bool

    def action_type(self) -> RuleActionType:
        return RuleActionType(self.rule.action)


class RuleEngine:
    """Charge les règles YAML et les évalue contre un cas — ordre déterministe."""

    def __init__(self) -> None:
        self._rules: list[Rule] = []
        self._by_id: dict[str, Rule] = {}
        self._sources: list[str] = []

    # --- chargement -----------------------------------------------------------
    def load_yaml(self, path: str | object) -> int:
        import pathlib

        p = pathlib.Path(path)
        with open(p, encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        n = 0
        for raw in data.get("rules", []):
            rule = Rule(
                id=str(raw["id"]),
                action=str(raw.get("action", "inform")),
                priority=int(raw.get("priority", 50)),
                weight=float(raw.get("weight", 0.5)),
                disease=raw.get("disease"),
                description=str(raw.get("description", "")),
                when=raw.get("when"),
                then=dict(raw.get("then") or {}),
                evidence=[str(e) for e in raw.get("evidence", [])],
                tags=[str(t) for t in raw.get("tags", [])],
            )
            if rule.id in self._by_id:
                raise RuleLoadError(f"ID de règle dupliqué: {rule.id}")
            self._rules.append(rule)
            self._by_id[rule.id] = rule
            n += 1
        self._sources.append(str(p))
        return n

    def load_directory(self, dirpath: str | object) -> int:
        import pathlib

        total = 0
        for p in sorted(pathlib.Path(dirpath).rglob("*.yaml")):
            if "tests" in p.parts:  # les fixtures de tests ne sont pas des règles actives
                continue
            total += self.load_yaml(p)
        return total

    # --- introspection ------------------------------------------------------------
    @property
    def rules(self) -> list[Rule]:
        return sorted(self._rules, key=lambda r: (-r.priority, r.id))

    def count(self) -> int:
        return len(self._rules)

    def get(self, rule_id: str) -> Rule | None:
        return self._by_id.get(rule_id)

    def ids(self) -> list[str]:
        return sorted(self._by_id)

    def fingerprint(self) -> str:
        return fingerprint(*sorted(self._by_id))

    # --- exécution ----------------------------------------------------------------
    def execute(self, case: ClinicalCase) -> list[RuleOutcome]:
        """Évaluation déterministe en 3 passes :

        1. raise_suspicion — alimente ctx.suspected (le différentiel)
        2. red_flag       — alimente ctx.red_flag_codes
        3. toutes les autres actions, par priorité décroissante

        Les passes garantissent que `disease:`/`red_flag_code:` dans les
        conditions voient toujours l'état consolidé des passes précédentes.
        """
        ctx = EvalContext(case=case)
        outcomes: list[RuleOutcome] = []

        def _run(rules: list[Rule]) -> None:
            for rule in rules:
                matched = rule.evaluate(ctx)
                if not matched:
                    continue
                outcomes.append(RuleOutcome(rule=rule, matched=True))
                at = RuleActionType(rule.action)
                if at is RuleActionType.RAISE_SUSPICION:
                    disease = (rule.then or {}).get("disease") or rule.disease
                    if disease:
                        ctx.suspected.add(str(disease))
                elif at is RuleActionType.RED_FLAG:
                    code = (rule.then or {}).get("code")
                    if code:
                        ctx.red_flag_codes.add(str(code))

        ordered = self.rules
        _run([r for r in ordered if r.action == RuleActionType.RAISE_SUSPICION.value])
        _run([r for r in ordered if r.action == RuleActionType.RED_FLAG.value])
        _run([r for r in ordered if r.action not in
              (RuleActionType.RAISE_SUSPICION.value, RuleActionType.RED_FLAG.value)])
        return outcomes

    def matched(self, case: ClinicalCase) -> list[RuleOutcome]:
        return [o for o in self.execute(case) if o.matched]
