from __future__ import annotations

import hashlib
import json
import random
import re
from collections import Counter
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from vett_r21.generator import build_instance as build_r21_instance
from vett_r21.generator import resolve as resolve_r21

from .spec import (
    COMPATIBLE_R21_MECHANISMS,
    DEFAULT_SEED,
    LEVELS,
    PROVENANCE_SHAPES,
    TARGET_FAMILIES,
    VERSION,
)


@dataclass(frozen=True)
class Bundle:
    public: dict[str, Any]
    gold: dict[str, Any]
    evidence: dict[str, Any]


IDENTITY_COLUMNS = {"Batter", "Bowler", "Player", "Partnership", "Field"}


def _digest(*parts: object) -> str:
    return hashlib.sha256("|".join(map(str, parts)).encode("utf-8")).hexdigest()


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _clone(value: Any) -> Any:
    return json.loads(json.dumps(value, ensure_ascii=False))


def _canonical_scope(target: dict[str, Any]) -> str:
    return "|".join(
        str(target.get(key) or "MATCH")
        for key in ("innings_id", "table_type", "row_id", "column")
    )


def _locator(target: dict[str, Any]) -> str:
    innings = target.get("innings_id") or "match-level"
    return (
        f"the {target['column']} field on row {target['row_id']} of the "
        f"{innings} {target['table_type']} record"
    )


def _wrong_values(value: str, count: int) -> list[str]:
    values: list[str] = []
    try:
        number = Decimal(value)
    except Exception:
        number = None
    for index in range(1, count + 4):
        if number is not None:
            if "." in value:
                candidate = str(number + Decimal(index)).rstrip("0").rstrip(".")
            else:
                candidate = str(int(number) + index)
        else:
            candidate = f"provisional-{index}:{value}"
        if candidate != value and candidate not in values:
            values.append(candidate)
        if len(values) == count:
            return values
    raise ValueError(f"cannot create alternatives for {value!r}")


def _r21_depth(target: dict[str, Any]) -> int:
    edges = target.get("required_edges", [])
    parents: dict[str, list[str]] = {}
    for edge in edges:
        parents.setdefault(edge["from_span"], []).append(edge["to_span"])

    def visit(node: str, seen: set[str]) -> int:
        if node in seen:
            raise ValueError("cycle in R21 baseline graph")
        return max((1 + visit(parent, seen | {node}) for parent in parents.get(node, [])), default=0)

    return max((visit(node, set()) for node in parents), default=0)


def _cell_index(root: dict[str, Any]) -> dict[tuple[str, str, str], dict[str, Any]]:
    return {
        (cell["table_id"], cell["row_id"], cell["column"]): cell
        for cell in root["cells"]
    }


def _leading_int(value: str) -> int | None:
    match = re.match(r"^\s*(-?\d+)", value)
    return int(match.group(1)) if match else None


def _two_dp(value: Decimal) -> str:
    return str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _derived_candidates(
    root: dict[str, Any], targets: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    cells = _cell_index(root)
    candidates: list[dict[str, Any]] = []
    for table in root["tables"]:
        for row in table["rows"]:
            def get(column: str) -> dict[str, Any] | None:
                cell = cells.get((table["table_id"], row["row_id"], column))
                if not cell or cell.get("gold_status") != "R20_VERIFIED_SOURCE":
                    return None
                if cell["cell_id"] not in targets:
                    return None
                return cell

            if table["table_type"] == "Partnerships":
                result = get("Runs")
                extras = get("Extras")
                first = get("Striker")
                second = get("Non-striker") or get("Non-Striker")
                if result and extras and first and second:
                    values = [_leading_int(str(item["value"])) for item in (first, second, extras)]
                    if all(value is not None for value in values) and sum(values) == int(result["value"]):
                        candidates.append({
                            "source_target_id": result["cell_id"],
                            "operation": "sum_int",
                            "components": [
                                {
                                    "target_id": item["cell_id"],
                                    "source_value": str(item["value"]),
                                    "extractor": "leading_int",
                                    "value": str(value),
                                }
                                for item, value in zip((first, second, extras), values)
                            ],
                            "value": str(result["value"]),
                            "rule_text": "Add the two credited partner contributions and the stand extras.",
                        })
            elif table["table_type"] == "Batting":
                fours, sixes = get("4s"), get("6s")
                if fours and sixes:
                    four_value, six_value = int(fours["value"]), int(sixes["value"])
                    common_components = [
                        {"target_id": fours["cell_id"], "source_value": str(four_value), "extractor": "exact", "value": str(four_value)},
                        {"target_id": sixes["cell_id"], "source_value": str(six_value), "extractor": "exact", "value": str(six_value)},
                    ]
                    candidates.append({
                        "source_target_id": fours["cell_id"],
                        "operation": "weighted_boundary_runs",
                        "components": common_components,
                        "value": str(4 * four_value + 6 * six_value),
                        "rule_text": "Multiply the fours count by 4, multiply the sixes count by 6, then add the products.",
                    })
                    candidates.append({
                        "source_target_id": sixes["cell_id"],
                        "operation": "sum_int",
                        "components": common_components,
                        "value": str(four_value + six_value),
                        "rule_text": "Add the fours count and sixes count to obtain the number of boundary-scoring events.",
                    })
                result, runs, balls = get("SR"), get("R"), get("B")
                if result and runs and balls and str(result["value"]) != "-" and int(balls["value"]) > 0:
                    expected = _two_dp(Decimal(runs["value"]) * Decimal(100) / Decimal(balls["value"]))
                    if expected == str(result["value"]):
                        candidates.append({
                            "source_target_id": result["cell_id"],
                            "operation": "ratio_percent_2dp",
                            "components": [
                                {"target_id": runs["cell_id"], "source_value": str(runs["value"]), "extractor": "exact", "value": str(runs["value"])},
                                {"target_id": balls["cell_id"], "source_value": str(balls["value"]), "extractor": "exact", "value": str(balls["value"])},
                            ],
                            "value": expected,
                            "rule_text": "Multiply runs by 100, divide by balls faced, and round half up to two decimals.",
                        })
            elif table["table_type"] == "Bowling":
                result, runs, overs = get("Econ"), get("R"), get("O")
                if result and runs and overs:
                    text = str(overs["value"])
                    parts = text.split(".", 1)
                    if all(part.isdigit() for part in parts):
                        balls = int(parts[0]) * 6 + (int(parts[1]) if len(parts) == 2 else 0)
                        if balls > 0:
                            expected = _two_dp(Decimal(runs["value"]) * Decimal(6) / Decimal(balls))
                            if expected == str(result["value"]):
                                candidates.append({
                                    "source_target_id": result["cell_id"],
                                    "operation": "economy_2dp",
                                    "components": [
                                        {"target_id": runs["cell_id"], "source_value": str(runs["value"]), "extractor": "exact", "value": str(runs["value"])},
                                        {"target_id": overs["cell_id"], "source_value": str(overs["value"]), "extractor": "legal_balls", "value": str(balls)},
                                    ],
                                    "value": expected,
                                    "rule_text": "Multiply conceded runs by 6, divide by legal balls, and round half up to two decimals.",
                                })
    return candidates


def _ranked(items: list[Any], *parts: object, key) -> list[Any]:
    return sorted(items, key=lambda item: _digest(*parts, key(item)))


def _select_sources(
    root: dict[str, Any], r21_targets: list[dict[str, Any]], seed: int
) -> dict[tuple[str, str], dict[str, Any]]:
    by_id = {target["target_id"]: target for target in r21_targets}
    derived = _derived_candidates(root, by_id)
    selected: dict[tuple[str, str], dict[str, Any]] = {}
    used: set[str] = set()
    for level in LEVELS:
        allowed = COMPATIBLE_R21_MECHANISMS[level]
        for family in TARGET_FAMILIES:
            if family == "derived_indicator":
                pool = [
                    item for item in derived
                    if item["source_target_id"] not in used
                    and by_id[item["source_target_id"]]["mechanism"] in allowed
                    and (level not in {"L1", "L2", "L3"} or len(item["components"]) == 2)
                    and (
                        level not in {"L1", "L2", "L3"}
                        or len({str(part["value"]) for part in item["components"]} | {str(item["value"])}) >= 2
                    )
                ]
                if level == "L5":
                    preferred = [item for item in pool if item["operation"] == "sum_int"]
                    if preferred:
                        pool = preferred
                    else:
                        pool = [item for item in pool if item["operation"] in {"ratio_percent_2dp", "economy_2dp"}]
                pool = _ranked(pool, seed, root["root_id"], level, family, key=lambda item: item["source_target_id"])
                if not pool:
                    raise ValueError(f"{root['root_id']}:{level}:{family}: no verified derivation candidate")
                choice = dict(pool[0])
                choice["target"] = by_id[choice["source_target_id"]]
            else:
                pool = [
                    target for target in r21_targets
                    if target["target_id"] not in used and target["mechanism"] in allowed
                ]
                if family == "entity_scope":
                    pool = [target for target in pool if target["column"] in IDENTITY_COLUMNS]
                elif family == "cell_value":
                    pool = [target for target in pool if target["column"] not in IDENTITY_COLUMNS]
                pool = _ranked(pool, seed, root["root_id"], level, family, key=lambda item: item["target_id"])
                if not pool:
                    raise ValueError(f"{root['root_id']}:{level}:{family}: no compatible source target")
                choice = {"source_target_id": pool[0]["target_id"], "target": pool[0]}
            used.add(choice["source_target_id"])
            selected[(level, family)] = choice
    if len(used) != 25:
        raise ValueError(f"{root['root_id']}: probe source targets are not unique")
    return selected


class _ProbeBuilder:
    def __init__(self, match_id: str, probe_id: str, seed: int) -> None:
        self.match_id = match_id
        self.probe_id = probe_id
        self.seed = seed
        self.claims: list[dict[str, Any]] = []
        self.edges: list[dict[str, str]] = []

    def add(
        self,
        relation: str,
        value: str | None,
        parents: list[dict[str, Any]],
        role: str,
        text_body: str,
        *,
        scope: str | None = None,
        operator: str | None = None,
    ) -> dict[str, Any]:
        ordinal = len(self.claims)
        token = _digest(self.seed, self.match_id, self.probe_id, ordinal, relation, role)
        docket = f"R{token[:10].upper()}"
        parent_dockets = [parent["docket"] for parent in parents]
        text = text_body.format(docket=docket, parents=", ".join(parent_dockets))
        claim = {
            "claim_id": f"r22claim_{token[10:26]}",
            "probe_id": self.probe_id,
            "docket": docket,
            "relation": relation,
            "value": value,
            "parent_claim_ids": [parent["claim_id"] for parent in parents],
            "span_id": f"r22span_{token[26:46]}",
            "role": role,
            "scope": scope,
            "operator": operator,
            "text": f"Docket {docket}. {text}",
        }
        claim["span_sha256"] = _hash(claim["text"])
        self.claims.append(claim)
        for parent in parents:
            self.edges.append({
                "from_span": claim["span_id"],
                "relation": relation,
                "to_span": parent["span_id"],
            })
        return claim


def _normal_probe_graph(
    source: dict[str, Any], level: str, family: str, builder: _ProbeBuilder
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, str]], list[dict[str, Any]], list[dict[str, str]]]:
    target = source["target"]
    answer = str(target["value"])
    wrong = _wrong_values(answer, 8)
    scope = _canonical_scope(target)
    locator = _locator(target)

    def root(value: str, role: str) -> dict[str, Any]:
        return builder.add(
            "asserts", value, [], role,
            f"{{docket}} assigns {json.dumps(value)} to {locator}; this is the only span that states the full semantic coordinate.",
            scope=scope,
        )

    def replace(parent: dict[str, Any], value: str, role: str) -> dict[str, Any]:
        return builder.add(
            "supersedes", value, [parent], role,
            f"{{docket}} explicitly supersedes {{parents}} for its referenced item and supplies {json.dumps(value)}; it does not broaden the scope.",
        )

    def inherit(parent: dict[str, Any], relation: str, role: str) -> dict[str, Any]:
        verb = "copies the still-operative entry from" if relation == "copies_from" else "confines the inherited entry to the same named scope as"
        return builder.add(
            relation, None, [parent], role,
            f"{{docket}} {verb} {{parents}} and carries no independent value.",
        )

    def retract(parent: dict[str, Any], role: str) -> dict[str, Any]:
        return builder.add(
            "retracts", None, [parent], role,
            "{docket} explicitly retracts {parents} for its referenced scope and supplies no replacement value.",
        )

    decisive: list[dict[str, Any]] = []
    if level == "L1":
        a = root(wrong[0], "anchor")
        terminal = replace(a, answer, "active_replacement")
        decisive = [a, terminal]
    elif level == "L2":
        a = root(wrong[0], "anchor")
        b = replace(a, wrong[1], "intermediate_replacement")
        terminal = replace(b, answer, "active_replacement")
        decisive = [a, b, terminal]
    elif level == "L3":
        a = root(wrong[0], "anchor")
        b = replace(a, wrong[1], "intermediate_replacement")
        c = replace(b, answer, "active_replacement")
        terminal = inherit(c, "copies_from", "query_copy")
        decisive = [a, b, c, terminal]
    elif level == "L4":
        a1 = root(wrong[0], "anchor_a")
        a2 = replace(a1, answer, "active_replacement_a")
        a3 = inherit(a2, "copies_from", "copy_a")
        b1 = root(wrong[1], "anchor_b")
        b2 = retract(b1, "retraction_b")
        b3 = root(answer, "independent_replacement_b")
        terminal = builder.add(
            "computed_from", None, [a3, b2, b3], "reconciliation",
            "{docket} applies the public active-value rule to {parents}: ignore an explicitly retracted branch, then require every remaining active lineage to agree.",
            operator="reconcile_active",
        )
        decisive = [a1, a2, a3, b1, b2, b3, terminal]
    else:
        a1 = root(wrong[0], "anchor_a")
        a2 = replace(a1, answer, "active_replacement_a")
        a3 = inherit(a2, "copies_from", "copy_a")
        a4 = inherit(a3, "qualifies", "scope_a")
        b1 = root(wrong[1], "anchor_b")
        b2 = retract(b1, "retraction_b")
        b3 = root(wrong[2], "independent_replacement_b")
        b4 = replace(b3, answer, "active_replacement_b")
        b5 = inherit(b4, "copies_from", "copy_b")
        merged = builder.add(
            "computed_from", None, [a4, b2, b5], "reconciliation",
            "{docket} applies the public active-value rule to {parents}: the retracted branch is excluded and the two remaining scoped lineages must agree.",
            operator="reconcile_active",
        )
        terminal = builder.add(
            "computed_from", None, [merged], "query_reconciliation",
            "{docket} certifies the reconciled value from {parents}; the one-input public rule preserves that value only after the upstream two-lineage check succeeds.",
            operator="reconcile_equal",
        )
        decisive = [a1, a2, a3, a4, b1, b2, b3, b4, b5, merged, terminal]

    decisive_ids = {claim["claim_id"] for claim in decisive}
    decisive_edges = [
        edge for edge in builder.edges
        if any(claim["span_id"] == edge["from_span"] for claim in decisive)
        and any(claim["span_id"] == edge["to_span"] for claim in decisive)
    ]
    provenance: list[dict[str, Any]] = []
    provenance_edges: list[dict[str, str]] = []
    prov_count, _ = PROVENANCE_SHAPES[level]
    anchors = [claim for claim in decisive if claim["role"].startswith("anchor")]
    for index in range(prov_count):
        parent = anchors[index % len(anchors)]
        before = len(builder.edges)
        if level == "L3" or (level == "L5" and index == 0):
            item = builder.add(
                "copies_from", None, [parent], "stale_copy_decoy",
                "{docket} copied the provisional value from {parents}; it inherits that source's later invalidity and is not independent support.",
            )
        else:
            alternative_index = 3 + index if level == "L5" else 2 + index
            item = builder.add(
                "qualifies", wrong[alternative_index], [parent], "scope_decoy",
                f"{{docket}} records {json.dumps(wrong[alternative_index])} for a similarly numbered entry in a different scope and qualifies {{parents}} only as the contrast source.",
                scope=f"contrast-{index}",
            )
        provenance.append(item)
        provenance_edges.extend(builder.edges[before:])
    assert decisive_ids.isdisjoint({claim["claim_id"] for claim in provenance})
    return terminal, decisive, decisive_edges, provenance, provenance_edges


def _apply_operator(operator: str, values: list[str]) -> str:
    if operator == "sum_int":
        return str(sum(int(value) for value in values))
    if operator == "ratio_percent_2dp":
        return _two_dp(Decimal(values[0]) * Decimal(100) / Decimal(values[1]))
    if operator == "economy_2dp":
        return _two_dp(Decimal(values[0]) * Decimal(6) / Decimal(values[1]))
    if operator == "weighted_boundary_runs":
        return str(int(values[0]) * 4 + int(values[1]) * 6)
    if operator == "multiply_100":
        return str(Decimal(values[0]) * Decimal(100))
    if operator == "multiply_6":
        return str(Decimal(values[0]) * Decimal(6))
    if operator == "divide_2dp":
        return _two_dp(Decimal(values[0]) / Decimal(values[1]))
    if operator == "reconcile_equal":
        if not values or len(set(values)) != 1:
            raise ValueError("reconciliation inputs do not agree")
        return values[0]
    if operator == "reconcile_active":
        active = [value for value in values if not value.startswith("__RETRACTED__:")]
        if not active or len(active) == len(values) or len(set(active)) != 1:
            raise ValueError("active-value reconciliation failed")
        return active[0]
    raise ValueError(f"unknown operator: {operator}")


def _derived_probe_graph(
    source: dict[str, Any], level: str, builder: _ProbeBuilder
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, str]], list[dict[str, Any]], list[dict[str, str]]]:
    target = source["target"]
    components = source["components"]
    component_targets = {item["target_id"]: item for item in components}
    scope = _canonical_scope(target)

    used_wrong: set[str] = set()

    def component_claim(component: dict[str, Any], index: int, corrected: bool, copied: bool) -> list[dict[str, Any]]:
        value = str(component["value"])
        source_target = component_targets[component["target_id"]]
        occupied = {str(item["value"]) for item in components} | {str(source["value"])}
        wrong = next(candidate for candidate in _wrong_values(value, 12) if candidate not in occupied | used_wrong)
        used_wrong.add(wrong)
        locator = f"component {index + 1} ({source_target['target_id'].split('.')[-1]}) for the rule attached to {scope}"
        first = builder.add(
            "asserts", wrong if corrected else value, [], f"component_{index}_anchor",
            f"{{docket}} records {json.dumps(wrong if corrected else value)} as {locator}.",
            scope=scope,
        )
        chain = [first]
        if corrected:
            second = builder.add(
                "supersedes", value, [first], f"component_{index}_replacement",
                f"{{docket}} supersedes {{parents}} for that component and supplies {json.dumps(value)}.",
            )
            chain.append(second)
        if copied:
            third = builder.add(
                "copies_from", None, [chain[-1]], f"component_{index}_copy",
                "{docket} carries the component forward from {parents} without an independent value.",
            )
            chain.append(third)
        return chain

    chains: list[list[dict[str, Any]]] = []
    for index, component in enumerate(components):
        corrected = level in {"L2", "L3", "L4", "L5"} and (level in {"L4", "L5"} or index == 0)
        copied = level == "L5"
        chains.append(component_claim(component, index, corrected, copied))
    parents = [chain[-1] for chain in chains]
    operation = source["operation"]
    if level == "L5":
        if operation == "sum_int":
            inner = builder.add(
                "computed_from", None, parents[:2], "inner_derivation",
                "{docket} applies the public integer-sum rule to {parents}.", operator="sum_int",
            )
            if len(parents) == 2:
                final_parents = [inner]
                final_operator = "reconcile_equal"
            else:
                final_parents = [inner, parents[2]]
                final_operator = "sum_int"
        else:
            multiplier = "multiply_100" if operation == "ratio_percent_2dp" else "multiply_6"
            scale = "100" if multiplier == "multiply_100" else "6"
            inner = builder.add(
                "computed_from", None, [parents[0]], "inner_derivation",
                f"{{docket}} multiplies the resolved value from {{parents}} by {scale}.", operator=multiplier,
            )
            final_parents = [inner, parents[1]]
            final_operator = "divide_2dp"
        computed = builder.add(
            "computed_from", None, final_parents, "outer_derivation",
            "{docket} completes the stated rule using {parents} and rounds half up to two decimals only when division is used.",
            operator=final_operator,
        )
        terminal = builder.add(
            "copies_from", None, [computed], "query_copy",
            "{docket} publishes the derived indicator from {parents} without restating its value.",
        )
    else:
        computed = builder.add(
            "computed_from", None, parents, "derivation",
            f"{{docket}} uses {{parents}}. Public rule: {source['rule_text']}", operator=operation,
        )
        if level in {"L3", "L4"}:
            terminal = builder.add(
                "copies_from", None, [computed], "query_copy",
                "{docket} publishes the derived indicator from {parents} without restating its value.",
            )
        else:
            terminal = computed

    decisive = list(builder.claims)
    decisive_edges = list(builder.edges)
    provenance: list[dict[str, Any]] = []
    provenance_edges: list[dict[str, str]] = []
    prov_count, _ = PROVENANCE_SHAPES[level]
    for index in range(prov_count):
        parent = chains[index % len(chains)][0]
        before = len(builder.edges)
        occupied_values = {str(claim["value"]) for claim in builder.claims if claim.get("value") is not None}
        alternative = next(
            value for value in _wrong_values(str(parent.get("value") or index), 12)
            if value not in occupied_values
        )
        if level == "L3" or (level == "L5" and index == 0):
            item = builder.add(
                "copies_from", None, [parent], "stale_component_copy",
                "{docket} copied the provisional component from {parents}; it inherits any later invalidity and is not an independent measurement.",
            )
        else:
            item = builder.add(
                "qualifies", alternative, [parent], "scope_component_decoy",
                f"{{docket}} records {json.dumps(alternative)} for a similarly named component in another scope; it qualifies {{parents}} only as a contrast.",
                scope=f"derived-contrast-{index}",
            )
        provenance.append(item)
        provenance_edges.extend(builder.edges[before:])
    return terminal, decisive, decisive_edges, provenance, provenance_edges


def _edge_tuple(edge: dict[str, Any]) -> tuple[str, str, str]:
    return (edge["from_span"], edge["relation"], edge["to_span"])


def _graph_depth(edges: list[dict[str, str]]) -> int:
    parents: dict[str, list[str]] = {}
    for edge in edges:
        parents.setdefault(edge["from_span"], []).append(edge["to_span"])

    def visit(node: str, seen: set[str]) -> int:
        if node in seen:
            raise ValueError("cycle in probe graph")
        return max((1 + visit(parent, seen | {node}) for parent in parents.get(node, [])), default=0)

    return max((visit(node, set()) for node in parents), default=0)


def _roots(query: dict[str, Any], claims: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []

    def walk(claim: dict[str, Any]) -> None:
        parents = claim.get("parent_claim_ids", [])
        if not parents:
            found.append(claim)
        for parent_id in parents:
            walk(claims[parent_id])

    walk(query)
    return found


def resolve_probe(
    probe: dict[str, Any],
    claims_list: list[dict[str, Any]],
    *,
    available_spans: set[str] | None = None,
    available_edges: set[tuple[str, str, str]] | None = None,
) -> str:
    claims = {claim["claim_id"]: claim for claim in claims_list if claim["probe_id"] == probe["probe_id"]}
    spans = available_spans if available_spans is not None else {claim["span_id"] for claim in claims.values()}
    edges = available_edges if available_edges is not None else {
        (claim["span_id"], claim["relation"], claims[parent]["span_id"])
        for claim in claims.values()
        for parent in claim.get("parent_claim_ids", [])
    }
    memo: dict[str, str] = {}

    def evaluate(claim_id: str, stack: set[str]) -> str:
        if claim_id in memo:
            return memo[claim_id]
        if claim_id in stack:
            raise ValueError("cycle")
        claim = claims.get(claim_id)
        if claim is None or claim["span_id"] not in spans:
            raise ValueError("missing decisive span")
        parent_values: list[str] = []
        for parent_id in claim.get("parent_claim_ids", []):
            parent = claims.get(parent_id)
            if parent is None:
                raise ValueError("missing parent claim")
            edge = (claim["span_id"], claim["relation"], parent["span_id"])
            if edge not in edges:
                raise ValueError("missing decisive edge")
            parent_values.append(evaluate(parent_id, stack | {claim_id}))
        relation = claim["relation"]
        if relation == "asserts":
            result = str(claim["value"])
        elif relation == "supersedes":
            if not parent_values:
                raise ValueError("orphan supersession")
            result = str(claim["value"])
        elif relation in {"copies_from", "qualifies"}:
            if len(parent_values) != 1:
                raise ValueError("inheritance arity")
            result = parent_values[0]
        elif relation == "retracts":
            if len(parent_values) != 1:
                raise ValueError("retraction arity")
            result = f"__RETRACTED__:{parent_values[0]}"
        elif relation == "computed_from":
            result = _apply_operator(str(claim["operator"]), parent_values)
        else:
            raise ValueError(f"unsupported relation {relation}")
        memo[claim_id] = result
        return result

    query = claims[probe["query_claim_id"]]
    resolved_value = evaluate(query["claim_id"], set())
    family = probe["target_family"]
    if family in {"cell_value", "derived_indicator"}:
        return resolved_value
    root_claims = _roots(query, claims)
    if family == "entity_scope":
        scopes = {root.get("scope") for root in root_claims}
        if len(scopes) != 1 or None in scopes:
            raise ValueError("scope roots do not agree")
        return str(next(iter(scopes)))
    decisive_edges = probe["decisive_evidence"]["edges"]
    if family == "event_state":
        counts = Counter(edge["relation"] for edge in decisive_edges)
        return "|".join(f"{name}:{counts[name]}" for name in sorted(counts))
    if family == "consistency_provenance":
        return "+".join(sorted({root["docket"] for root in root_claims}))
    raise ValueError(f"unknown target family: {family}")


def _question(family: str, query_docket: str) -> tuple[str, str]:
    if family == "cell_value":
        return (f"Resolve the exact active value carried by query docket {query_docket}.", "exact_string")
    if family == "entity_scope":
        return (
            f"Resolve every parent of query docket {query_docket}, then return its semantic coordinate as innings|table_type|row_id|column.",
            "semantic_coordinate",
        )
    if family == "event_state":
        return (
            f"For the decisive graph ending at {query_docket}, return the sorted relation-count signature name:count joined by |.",
            "transition_signature",
        )
    if family == "derived_indicator":
        return (f"Compute the exact public-rule result published through query docket {query_docket}.", "exact_numeric_string")
    return (
        f"Resolve query docket {query_docket} and return the sorted set of root dockets joined by +.",
        "provenance_root_set",
    )


def build_instance(root: dict[str, Any], seed: int = DEFAULT_SEED) -> Bundle:
    match_id = root["root_id"]
    baseline = build_r21_instance(root, seed=21031)
    baseline_resolved = resolve_r21(baseline.evidence)
    baseline_expected = {target["target_id"]: target["value"] for target in baseline.gold["targets"]}
    if baseline_resolved != baseline_expected:
        raise ValueError(f"{match_id}: R21 baseline does not resolve")
    baseline_words = sum(
        len(re.findall(r"\b\w+\b", span["text"]))
        for document in baseline.public["documents"]
        for span in document["spans"]
    )
    sources = _select_sources(root, baseline.gold["targets"], seed)
    probe_claims: list[dict[str, Any]] = []
    probes: list[dict[str, Any]] = []
    public_probes: list[dict[str, Any]] = []
    for level_index, level in enumerate(LEVELS, 1):
        for family_index, family in enumerate(TARGET_FAMILIES, 1):
            probe_id = f"probe_{_digest(seed, match_id, level, family)[:18]}"
            source = sources[(level, family)]
            builder = _ProbeBuilder(match_id, probe_id, seed)
            if family == "derived_indicator":
                terminal, decisive, decisive_edges, provenance, provenance_edges = _derived_probe_graph(source, level, builder)
            else:
                terminal, decisive, decisive_edges, provenance, provenance_edges = _normal_probe_graph(source, level, family, builder)
            all_claims = decisive + provenance
            probe_claims.extend(all_claims)
            baseline_target = source["target"]
            candidate_values = {str(claim["value"]) for claim in all_claims if claim.get("value") is not None}
            if family == "derived_indicator":
                candidate_values.add(str(source["value"]))
            metadata = {
                "probe_id": probe_id,
                "level": level,
                "target_family": family,
                "source_target_id": source["source_target_id"],
                "query_claim_id": terminal["claim_id"],
                "query_docket": terminal["docket"],
                "decisive_evidence": {
                    "spans": [claim["span_id"] for claim in decisive],
                    "edges": decisive_edges,
                },
                "provenance_context": {
                    "spans": [claim["span_id"] for claim in provenance],
                    "edges": provenance_edges,
                },
                "complexity": {
                    "decisive_spans": len(decisive),
                    "decisive_edges": len(decisive_edges),
                    "provenance_spans": len(provenance),
                    "provenance_edges": len(provenance_edges),
                    "depth": _graph_depth(decisive_edges),
                    "candidate_values": len(candidate_values),
                    "derivation_hops": sum(claim["relation"] == "computed_from" for claim in decisive),
                },
                "r21_baseline": {
                    "mechanism": baseline_target["mechanism"],
                    "required_spans": len(baseline_target["required_evidence_spans"]),
                    "required_edges": len(baseline_target["required_edges"]),
                    "depth": _r21_depth(baseline_target),
                },
            }
            if family == "derived_indicator":
                metadata["derivation"] = {
                    key: _clone(source[key]) for key in ("operation", "components", "rule_text")
                }
            metadata["value"] = resolve_probe(metadata, all_claims)
            if family in {"cell_value", "derived_indicator"}:
                expected_value = str(source.get("value", baseline_target["value"]))
                if metadata["value"] != expected_value:
                    raise ValueError(f"{match_id}:{probe_id}: derived answer mismatch")
            probes.append(metadata)
            question, answer_type = _question(family, terminal["docket"])
            public_probes.append({
                "probe_id": probe_id,
                "target_family": family,
                "question": question,
                "answer_type": answer_type,
                "query_docket": terminal["docket"],
            })

    public = _clone(baseline.public)
    public["dataset_version"] = VERSION
    public["task"] = (
        "Track A: reconstruct every requested exact-string table cell. Track B: answer all evidence probes. "
        "Use only explicit supersedes, retracts, copies_from, qualifies and computed_from relations. "
        "Later relation spans may omit coordinates, so follow docket references. A copied claim inherits source status. "
        "For computed_from, apply only the stated public rule. Document order, genre and frequency are not authority signals."
    )
    public["output_contract"] = {
        "table_predictions": ["target_id", "value"],
        "probe_predictions": ["probe_id", "value", "decisive_spans", "decisive_edges", "provenance_spans", "provenance_edges", "confidence"],
        "edge_fields": ["from_span", "relation", "to_span"],
    }
    public["probe_schema"] = public_probes
    rng = random.Random(f"R22|{seed}|{match_id}")
    documents = public["documents"]
    for claim in probe_claims:
        index = int(_digest(seed, match_id, claim["span_id"], "document")[:12], 16) % len(documents)
        document = documents[index]
        document["spans"].append({"span_id": claim["span_id"], "text": claim["text"]})
        claim["document_id"] = document["document_id"]
    for document in documents:
        rng.shuffle(document["spans"])
        document["text"] = "\n".join(span["text"] for span in document["spans"])
    rng.shuffle(documents)

    gold = {
        "dataset_version": VERSION,
        "instance_id": match_id,
        "table_targets": _clone(baseline.gold["targets"]),
        "probes": probes,
        "masked_source_conflict_cell_ids": _clone(baseline.gold["masked_source_conflict_cell_ids"]),
        "baseline": {
            "dataset_version": baseline.gold["dataset_version"],
            "table_target_count": len(baseline.gold["targets"]),
            "table_target_digest": _hash(json.dumps(baseline_expected, sort_keys=True, ensure_ascii=False)),
            "public_words": baseline_words,
            "document_count": len(baseline.public["documents"]),
        },
    }
    evidence = {
        "dataset_version": VERSION,
        "instance_id": match_id,
        "policy": "R21_table_graph_plus_R22_minimal_decisive_probe_graph",
        "table_claims": _clone(baseline.evidence["claims"]),
        "probe_claims": probe_claims,
    }
    return Bundle(public=public, gold=gold, evidence=evidence)


__all__ = ["Bundle", "build_instance", "resolve_probe"]
