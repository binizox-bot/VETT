#!/usr/bin/env python3
"""Validate VETT-Cricket candidate roots and instances.

The validator checks structural identity, release gating, gold/root equality,
cell coverage, evidence offsets and hashes, revision semantics, and obvious
construction leakage. It produces a machine-readable certificate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def legal_balls(overs: str) -> int:
    if "." not in str(overs):
        return int(overs) * 6
    whole, rem = str(overs).split(".", 1)
    return int(whole) * 6 + int(rem)


def same_value(expected: Any, actual: Any) -> bool:
    if str(expected).strip() == str(actual).strip():
        return True
    try:
        return abs(float(expected) - float(actual)) <= 1e-9
    except (TypeError, ValueError):
        return False


def rounded_rate(numerator: int, denominator: int) -> str:
    value = Decimal(numerator) / Decimal(denominator)
    return format(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), "f")


def match_summary_value(root: dict[str, Any], field: str) -> str:
    for table in root["tables"]:
        if table.get("table_type") != "Match Summary":
            continue
        for row in table.get("rows", []):
            if row.get("Field") == field:
                return str(row.get("Value", ""))
    return ""


def evaluate_derivation(
    provenance: dict[str, Any],
    root_cells: dict[str, dict[str, Any]],
    root: dict[str, Any],
) -> tuple[bool, str]:
    expression = provenance.get("derivation") or ""
    deps = [root_cells[x]["value"] for x in provenance.get("dependencies", []) if x in root_cells]
    target = root_cells[provenance["cell_id"]]["value"]
    try:
        if expression.startswith("round(100 * R / B"):
            runs, balls = int(deps[0]), int(deps[1])
            expected = "-" if balls == 0 else rounded_rate(100 * runs, balls)
        elif expression.startswith("round(6 * R / legal_balls"):
            runs, overs = int(deps[0]), str(deps[1])
            expected = rounded_rate(6 * runs, legal_balls(overs))
        elif expression.startswith("sum(Byes"):
            expected = str(sum(int(x) for x in deps))
        elif expression.startswith("round(6 * innings_runs"):
            m = re.search(r"(\d+)(?:/\d+)?\s*\((\d+\.\d+)", str(deps[0]))
            if not m:
                return False, f"cannot parse total {deps[0]}"
            expected = rounded_rate(6 * int(m.group(1)), legal_balls(m.group(2)))
        elif expression.startswith("max(partnership_runs)"):
            expected = str(max(int(x) for x in deps))
        elif expression.startswith("sum(partnership_contribution_runs)"):
            expected = str(sum(int(re.match(r"^(\d+)\(", str(x)).group(1)) for x in deps))
        elif expression.startswith("sum(partnership_contribution_balls)"):
            expected = str(sum(int(re.match(r"^\d+\((\d+)\)", str(x)).group(1)) for x in deps))
        elif expression.startswith("count(dismissals_credited_to_bowler)"):
            expected = str(len(deps))
        else:
            return False, f"unknown derivation: {expression}"
        return same_value(expected, target), f"expected={expected}, target={target}"
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--roots", type=Path, required=True)
    parser.add_argument("--instances", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    roots = load_jsonl(args.roots)
    instances = load_jsonl(args.instances)
    root_by_id = {r["root_id"]: r for r in roots}
    failures: list[dict[str, Any]] = []
    checks = Counter()
    passes = Counter()

    def check(code: str, condition: bool, instance_id: str, detail: str = "") -> None:
        checks[code] += 1
        if condition:
            passes[code] += 1
        else:
            failures.append({"code": code, "instance_id": instance_id, "detail": detail})

    check("ROOT_ID_UNIQUE", len(root_by_id) == len(roots), "DATASET", f"{len(root_by_id)}/{len(roots)}")
    inst_ids = [x["instance_id"] for x in instances]
    check("INSTANCE_ID_UNIQUE", len(set(inst_ids)) == len(inst_ids), "DATASET", f"{len(set(inst_ids))}/{len(inst_ids)}")

    by_root_view = Counter((x["root_id"], x["view"]) for x in instances)
    for key, count in by_root_view.items():
        check("ONE_INSTANCE_PER_ROOT_VIEW", count == 1, f"{key[0]}.{key[1]}", str(count))

    leak_re = re.compile(r"\bsource game\b|\bscorecard fingerprint\b|\banonymized\b", re.I)
    for instance in instances:
        iid = instance["instance_id"]
        root = root_by_id.get(instance["root_id"])
        check("ROOT_EXISTS", root is not None, iid)
        if root is None:
            continue
        ready = root["curation_status"] == "READY_FOR_GENERATED_VIEWS"
        if instance["release_status"] == "RELEASE_CANDIDATE":
            check("RELEASE_ROOT_READY", ready, iid, root["curation_status"])
            check("RELEASE_VIEW_NOT_V0", instance["view"] in {"V1", "V2", "V3"}, iid, instance["view"])
            check("GOLD_TABLES_EQUAL_ROOT", instance["gold"]["tables"] == root["tables"], iid)

        docs = {d["document_id"]: d for d in instance["documents"]}
        check("DOCUMENT_ID_UNIQUE", len(docs) == len(instance["documents"]), iid)
        arrivals = [d["arrival_index"] for d in instance["documents"]]
        check("ARRIVAL_INDEX_UNIQUE", len(set(arrivals)) == len(arrivals), iid, str(arrivals))
        if instance["view"] == "V3" and instance["release_status"] == "RELEASE_CANDIDATE":
            distractor_docs = [doc_id for doc_id in docs if doc_id.startswith("distractor_")]
            target_venue = match_summary_value(root, "Venue")
            generator = instance["private_metadata"].get("generator", {})
            distractor_split = generator.get("distractor_selection", {}).get("same_split")
            check("DISTRACTOR_PRESENT", bool(distractor_docs), iid)
            check("TARGET_SCOPE_IN_INSTRUCTION", bool(target_venue) and target_venue in instance["instruction"], iid)
            check(
                "DISTRACTOR_SAME_SPLIT",
                bool(distractor_split) and distractor_split == generator.get("split"),
                iid,
            )

        if instance["release_status"] == "RELEASE_CANDIDATE":
            combined = "\n".join(d["text"] for d in instance["documents"])
            check("NO_CONSTRUCTION_LEAK", not leak_re.search(combined), iid)
            root_cells = {c["cell_id"]: c for c in root["cells"]}
            scored = instance["gold"]["scored_cell_ids"]
            check("SCORED_CELL_ID_UNIQUE", len(set(scored)) == len(scored), iid)
            check("SCORED_CELLS_EXIST", all(c in root_cells for c in scored), iid)
            provenance = {p["cell_id"]: p for p in instance["gold"]["cell_provenance"]}
            check("PROVENANCE_CELL_ID_UNIQUE", len(provenance) == len(instance["gold"]["cell_provenance"]), iid)
            check("PROVENANCE_COVERS_SCORED", all(c in provenance for c in scored), iid)
            for cell_id in scored:
                prov = provenance.get(cell_id)
                if not prov:
                    continue
                check("SCORED_CELL_HAS_EVIDENCE", bool(prov["evidence_spans"]) or bool(prov["derivation"]), iid, cell_id)
                if prov.get("derivation"):
                    dependencies = prov.get("dependencies", [])
                    check("DERIVATION_DEPENDENCIES_EXIST", bool(dependencies) and all(d in root_cells for d in dependencies), iid, cell_id)
                    ok, detail = evaluate_derivation(prov, root_cells, root)
                    check("DERIVATION_EXECUTES_TO_GOLD", ok, iid, f"{cell_id}: {detail}")
                for span in prov["evidence_spans"]:
                    if instance["view"] == "V3":
                        check(
                            "DISTRACTOR_NOT_IN_GOLD_PROVENANCE",
                            not span["document_id"].startswith("distractor_"),
                            iid,
                            cell_id,
                        )
                    doc = docs.get(span["document_id"])
                    check("SPAN_DOCUMENT_EXISTS", doc is not None, iid, cell_id)
                    if doc is None:
                        continue
                    start, end = span["start"], span["end"]
                    valid_offsets = 0 <= start < end <= len(doc["text"])
                    check("SPAN_OFFSETS_VALID", valid_offsets, iid, f"{cell_id}:{start}-{end}/{len(doc['text'])}")
                    if valid_offsets:
                        quote = doc["text"][start:end]
                        check("SPAN_HASH_VALID", sha256_text(quote) == span["quote_hash"], iid, cell_id)

            claims = instance["private_metadata"].get("revision_claims", [])
            if instance["view"] in {"V2", "V3"}:
                check("REVISION_CHAIN_PRESENT", bool(claims), iid)
                grouped = defaultdict(list)
                for claim in claims:
                    grouped[claim["cell_id"]].append(claim)
                for cell_id, chain in grouped.items():
                    canonical = root_cells[cell_id]["value"]
                    valid = [c for c in chain if c["status"] == "valid"]
                    stale = [c for c in chain if c["status"] in {"retracted", "stale"}]
                    check("ONE_VALID_REVISION", len(valid) == 1, iid, cell_id)
                    if valid:
                        check("VALID_REVISION_EQUALS_GOLD", str(valid[0]["value"]) == str(canonical), iid, cell_id)
                    check("STALE_REVISION_DIFFERS", bool(stale) and all(str(c["value"]) != str(canonical) for c in stale), iid, cell_id)

        if instance["release_status"].startswith("BLOCKED"):
            check("BLOCKED_HAS_NO_SCORED_CELLS", not instance["gold"]["scored_cell_ids"], iid)

    summary = {
        "validator_version": "0.1",
        "root_count": len(roots),
        "instance_count": len(instances),
        "checks_total": sum(checks.values()),
        "checks_passed": sum(passes.values()),
        "checks_failed": len(failures),
        "status": "PASS" if not failures else "FAIL",
        "by_check": {
            code: {
                "total": checks[code],
                "passed": passes[code],
                "failed": checks[code] - passes[code],
            }
            for code in sorted(checks)
        },
        "failures": failures[:500],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
