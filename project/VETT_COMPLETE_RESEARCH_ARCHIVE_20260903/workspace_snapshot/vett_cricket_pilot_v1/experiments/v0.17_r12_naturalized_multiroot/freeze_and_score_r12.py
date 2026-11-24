#!/usr/bin/env python3
"""Freeze four blind R12 predictions, then score atomic facts and evidence-chain errors."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
METHODS = {
    "direct": HERE / "runs_gpt55/direct/predictions.json",
    "cot": HERE / "runs_gpt55/cot/predictions.json",
    "t3_provenance_enhanced": HERE / "runs_gpt55/t3/predictions.json",
    "mapmake_scope_version_enhanced": HERE / "runs_gpt55/mapmake/predictions.json",
}
PUBLIC = HERE / "r12_public_blind.jsonl"
GOLD = HERE / "r12_private_gold.jsonl"
EVIDENCE = HERE / "r12_private_evidence.jsonl"
EXCLUSIONS = HERE / "R12_SCORING_EXCLUSIONS.json"
FREEZE = HERE / "GPT55_R12_PREDICTION_FREEZE.json"
RESULTS = HERE / "GPT55_R12_RESULTS.json"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def flatten(tables: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, tuple[str, str]]]:
    cells, rows = {}, {}
    for table in tables:
        tid = table["table_id"]
        for current in table["rows"]:
            row_key = current["row_key"]
            for field, value in current.items():
                if field == "row_key":
                    continue
                cid = f"{tid}.{row_key}.{field}"
                cells[cid] = value
                rows[cid] = (tid, row_key)
    return cells, rows


def public_contract() -> tuple[dict[str, set[str]], dict[str, list[str]]]:
    contracts, order = {}, {}
    for instance in read_jsonl(PUBLIC):
        cells, _ = flatten(instance["target_tables"])
        contracts[instance["instance_id"]] = set(cells)
        order[instance["instance_id"]] = [t["table_id"] for t in instance["target_tables"]]
    return contracts, order


def validate_prediction(path: Path, method: str, contracts: dict[str, set[str]],
                        allowed_blank: set[tuple[str, str]]) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    instances = payload.get("instances", [])
    found = {x.get("instance_id"): x for x in instances}
    errors = []
    for iid, expected in contracts.items():
        if iid not in found:
            errors.append(f"missing instance {iid}")
            continue
        tables = found[iid].get("tables", found[iid].get("target_tables", []))
        actual, _ = flatten(tables)
        if set(actual) != expected:
            errors.append(f"{iid}: cell contract differs; missing={len(expected-set(actual))}, extra={len(set(actual)-expected)}")
        blanks = [cid for cid, value in actual.items()
                  if (value is None or value == "") and (iid, cid) not in allowed_blank]
        if blanks:
            errors.append(f"{iid}: {len(blanks)} blank cells")
    extra_instances = set(found) - set(contracts)
    if extra_instances:
        errors.append(f"extra instances: {sorted(extra_instances)}")
    return {"method": method, "json_valid": True, "contract_valid": not errors,
            "errors": errors, "instances": len(instances), "payload": payload}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_value(value: Any) -> str:
    """Normalize JSON scalar types without erasing substantive punctuation."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return unicodedata.normalize("NFKC", str(value)).strip()


def fact_content(value: Any) -> str:
    """Diagnostic content normalization: case/punctuation/spacing do not count."""
    return re.sub(r"[^0-9a-z]+", "", canonical_value(value).casefold())


def main() -> None:
    if FREEZE.exists() or RESULTS.exists():
        raise SystemExit("freeze/results already exist; refusing to overwrite")
    contracts, _ = public_contract()
    exclusions_payload = json.loads(EXCLUSIONS.read_text(encoding="utf-8"))
    excluded = {(x["instance_id"], x["cell_id"]) for x in exclusions_payload["excluded_cells"]}
    validations = {}
    for method, path in METHODS.items():
        if not path.exists():
            raise SystemExit(f"missing prediction: {path}")
        validations[method] = validate_prediction(path, method, contracts, excluded)
    bad = {m: v["errors"] for m, v in validations.items() if not v["contract_valid"]}
    if bad:
        raise SystemExit(json.dumps(bad, ensure_ascii=False, indent=2))

    # Freeze is committed before either private file is opened below.
    freeze = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "protocol": "all predictions structurally valid; hashes written before private scoring",
        "public_sha256": sha(PUBLIC),
        "predictions": {method: {"path": str(path.relative_to(HERE)), "sha256": sha(path),
                                 "bytes": path.stat().st_size}
                        for method, path in METHODS.items()},
    }
    FREEZE.write_text(json.dumps(freeze, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    gold_items = {x["instance_id"]: x for x in read_jsonl(GOLD)}
    evidence_items = {x["instance_id"]: x for x in read_jsonl(EVIDENCE)}
    output = {"freeze_sha256": sha(FREEZE), "methods": {}, "comparability": {
        "model_family": "GPT-5.5", "instances": len(contracts),
        "scoring": "canonical scalar equality after JSON-number to string conversion and outer-whitespace trim",
        "fact_content_diagnostic": "NFKC + casefold + punctuation/space removal",
        "format_only_composites": False, "raw_public_blanks": 319,
        "excluded_structural_cells": len(excluded), "official_scored_atomic_cells": 317}}

    for method, validation in validations.items():
        predictions = {x["instance_id"]: x for x in validation["payload"]["instances"]}
        aggregate = Counter()
        per_instance = []
        operator_errors = Counter(); operator_totals = Counter()
        topology_errors = Counter(); topology_totals = Counter()
        hop_errors = Counter(); hop_totals = Counter()
        error_records = []
        for iid, gold in gold_items.items():
            pred_tables = predictions[iid].get("tables", predictions[iid].get("target_tables", []))
            pred, row_map = flatten(pred_tables)
            target, _ = flatten(gold["gold_tables"])
            chains = {c["cell_id"]: c for c in evidence_items[iid]["chains"]}
            row_state = defaultdict(lambda: [0, 0])
            target = {cid: value for cid, value in target.items() if (iid, cid) not in excluded}
            local = Counter(total=len(target))
            topology = evidence_items[iid]["topology"]
            for cid, expected in target.items():
                value = pred.get(cid)
                chain = chains[cid]
                row_state[row_map[cid]][1] += 1
                operator_totals[chain["operator"]] += 1
                topology_totals[topology] += 1
                hop = str(chain["minimum_hops"])
                hop_totals[hop] += 1
                strict_equal = value == expected
                canonical_equal = canonical_value(value) == canonical_value(expected)
                fact_equal = fact_content(value) == fact_content(expected)
                if strict_equal:
                    local["strict_correct"] += 1
                else:
                    local["strict_contract_errors"] += 1
                if fact_equal:
                    local["fact_content_correct"] += 1
                else:
                    local["fact_content_errors"] += 1
                if canonical_equal:
                    local["correct"] += 1
                    row_state[row_map[cid]][0] += 1
                else:
                    local["errors"] += 1
                    operator_errors[chain["operator"]] += 1
                    topology_errors[topology] += 1
                    hop_errors[hop] += 1
                    category = "decoy_adoption" if canonical_value(value) == canonical_value(chain["decoy"]) else "other_wrong_value"
                    local[category] += 1
                    error_records.append({"instance_id": iid, "cell_id": cid, "expected": expected,
                                          "predicted": value, "decoy": chain["decoy"],
                                          "category": category, "fact_content_equal": fact_equal,
                                          "operator": chain["operator"],
                                          "topology": topology, "minimum_hops": chain["minimum_hops"]})
            local["rows_total"] = len(row_state)
            local["rows_exact"] = sum(correct == total for correct, total in row_state.values())
            local["rows_error"] = local["rows_total"] - local["rows_exact"]
            local["cell_error_rate"] = round(100 * local["errors"] / local["total"], 4)
            local["strict_contract_error_rate"] = round(100 * local["strict_contract_errors"] / local["total"], 4)
            local["fact_content_error_rate"] = round(100 * local["fact_content_errors"] / local["total"], 4)
            local["row_exact_rate"] = round(100 * local["rows_exact"] / local["rows_total"], 4)
            per_instance.append({"instance_id": iid, **dict(local)})
            aggregate.update({k: v for k, v in local.items() if isinstance(v, int)})
        aggregate["cell_error_rate"] = round(100 * aggregate["errors"] / aggregate["total"], 4)
        aggregate["cell_accuracy"] = round(100 * aggregate["correct"] / aggregate["total"], 4)
        aggregate["strict_contract_error_rate"] = round(100 * aggregate["strict_contract_errors"] / aggregate["total"], 4)
        aggregate["fact_content_error_rate"] = round(100 * aggregate["fact_content_errors"] / aggregate["total"], 4)
        aggregate["row_exact_rate"] = round(100 * aggregate["rows_exact"] / aggregate["rows_total"], 4)

        def buckets(totals: Counter, errors: Counter) -> dict[str, Any]:
            return {k: {"errors": errors[k], "total": n, "error_rate": round(100 * errors[k] / n, 4)}
                    for k, n in sorted(totals.items())}

        output["methods"][method] = {
            "prediction_sha256": sha(METHODS[method]), "aggregate": dict(aggregate),
            "per_instance": per_instance, "by_operator": buckets(operator_totals, operator_errors),
            "by_topology": buckets(topology_totals, topology_errors),
            "by_minimum_hops": buckets(hop_totals, hop_errors), "errors": error_records,
        }
    RESULTS.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
