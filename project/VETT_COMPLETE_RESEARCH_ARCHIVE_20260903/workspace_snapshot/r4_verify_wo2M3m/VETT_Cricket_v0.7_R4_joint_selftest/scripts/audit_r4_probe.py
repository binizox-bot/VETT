#!/usr/bin/env python3
"""Audit R4 structure, symbolic uniqueness, leakage and oracle round-trip."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


FORBIDDEN_PUBLIC_KEYS = {
    "gold", "gold_value", "alternate_value", "delta", "cell_id", "table_id",
    "row_id", "scored_cell_ids", "private_metadata", "joint_constraint_blocks",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def walk_keys(value: Any) -> set[str]:
    result: set[str] = set()
    if isinstance(value, dict):
        result.update(value)
        for child in value.values():
            result.update(walk_keys(child))
    elif isinstance(value, list):
        for child in value:
            result.update(walk_keys(child))
    return result


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def flatten_gold(instance: dict[str, Any]) -> dict[str, Any]:
    cells = {}
    for table in instance["gold"]["tables"]:
        for row in table["rows"]:
            for column in table["columns"]:
                if column not in row:
                    continue
                suffix = re.sub(r"[^a-z0-9]+", "_", column.lower()).strip("_")
                cells[f"{table['table_id']}.{row['row_id']}.{suffix}"] = row[column]
    return cells


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--blind", type=Path, required=True)
    parser.add_argument("--scoring", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--oracle-score", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    blind = load_jsonl(args.blind)
    scoring = load_jsonl(args.scoring)
    scoring_by_root = {
        row["root_id"]: row for row in scoring if row["view"] == "R4S"
    }
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    failures: list[dict[str, Any]] = []
    details: list[dict[str, Any]] = []

    forbidden = sorted(walk_keys(blind) & FORBIDDEN_PUBLIC_KEYS)
    if forbidden:
        failures.append({"check": "blind_private_key_leakage", "observed": forbidden})
    if (len(blind), len(scoring), len(manifest)) != (6, 6, 3):
        failures.append({"check": "counts", "blind": len(blind), "scoring": len(scoring), "manifest": len(manifest)})

    for root in manifest:
        canonical_cells = flatten_gold(scoring_by_root[root["root_id"]])
        scalar_ids = set(next(x for x in root["instances"] if x["track"] == "scalar")["challenge_cell_ids"])
        root_row = {"root_id": root["root_id"], "blocks": len(root["joint_constraint_blocks"]), "block_checks": []}
        if len(root["joint_constraint_blocks"]) != 2:
            failures.append({"check": "block_count", "root_id": root["root_id"]})
        for block in root["joint_constraint_blocks"]:
            targets = block["targets"]
            changed = sum(t["gold_value"] != t["alternate_value"] for t in targets)
            target_ids = {t["cell_id"] for t in targets}
            canonical_matches = all(
                str(canonical_cells[t["cell_id"]]).strip() == str(t["gold_value"]).strip()
                for t in targets
            )
            alternate_matches = all(
                str(canonical_cells[t["cell_id"]]).strip() == str(t["alternate_value"]).strip()
                for t in targets
            )
            check = {
                "block_id": block["block_id"],
                "targets": len(targets),
                "changed_targets": changed,
                "constraint_types": len(set(block["constraint_types"])),
                "evidence_sources": len({ref.split(":", 1)[0] for ref in block["evidence_refs"]}),
                "canonical_candidate_matches_gold": canonical_matches,
                "alternate_candidate_matches_gold": alternate_matches,
            }
            root_row["block_checks"].append(check)
            if len(targets) < 6 or changed < 4 or len(set(block["constraint_types"])) < 3:
                failures.append({"check": "joint_block_shape", "root_id": root["root_id"], **check})
            if not canonical_matches or alternate_matches:
                failures.append({"check": "candidate_gold_compatibility", "root_id": root["root_id"], **check})
            if not target_ids <= scalar_ids:
                failures.append({"check": "non_scalar_block_target", "root_id": root["root_id"], "block_id": block["block_id"]})
            if check["evidence_sources"] < 3:
                failures.append({"check": "evidence_source_spread", "root_id": root["root_id"], **check})
            # Full constraints select canonical; dropping the global selection leaves both declared candidates.
            full_survivors = [block["globally_accepted_state"]]
            leave_one_out_survivors = block["candidate_states"]
            if full_survivors != ["canonical"] or len(leave_one_out_survivors) != 2:
                failures.append({"check": "symbolic_uniqueness", "root_id": root["root_id"], "block_id": block["block_id"]})
        details.append(root_row)

    # Overlay must not introduce explicit arithmetic equations or answer meta-language.
    overlay_docs = [doc for row in blind if row["instance_id"].endswith("R4S") for doc in row["documents"][1:]]
    overlay_text = "\n".join(doc["text"] for doc in overlay_docs)
    bad_patterns = {
        "visible_equation": r"\b\d+\s*[+*/=]\s*\d+\b",
        "answer_meta": r"\b(?:the answer is|corrected total is|therefore the value)\b",
    }
    for name, pattern in bad_patterns.items():
        hits = re.findall(pattern, overlay_text, flags=re.I)
        if hits:
            failures.append({"check": name, "hits": hits[:10]})

    oracle = json.loads(args.oracle_score.read_text(encoding="utf-8"))["groups"]["overall"]
    if not (oracle["gold"] == 48 and oracle["correct"] == 48 and oracle["missing"] == 0 and oracle["incorrect"] == 0):
        failures.append({"check": "semantic_oracle", "observed": oracle})

    report = {
        "audit_version": "0.1",
        "status": "PASS" if not failures else "FAIL",
        "blind_sha256": sha256(args.blind),
        "scoring_sha256": sha256(args.scoring),
        "forbidden_public_keys": forbidden,
        "details": details,
        "oracle": oracle,
        "failures": failures,
        "limitations": [
            "The symbolic audit verifies declared candidate-state uniqueness, not an independent semantic proof.",
            "Construction-context self-tests cannot estimate model population performance.",
            "Human double annotation and isolated blind model evaluation remain required before release.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "failures": len(failures)}, indent=2))
    raise SystemExit(0 if not failures else 1)


if __name__ == "__main__":
    main()
