#!/usr/bin/env python3
"""Audit split leakage, distractor scope and construction-text leakage."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def summary_value(root: dict[str, Any], field: str) -> str:
    for table in root["tables"]:
        if table["table_type"] == "Match Summary":
            for row in table["rows"]:
                if row.get("Field") == field:
                    return str(row.get("Value", ""))
    return ""


def canonical_fact_set(root: dict[str, Any]) -> set[str]:
    facts = set()
    for table in root["tables"]:
        for row in table["rows"]:
            for column in table["columns"]:
                facts.add(
                    "|".join(
                        [
                            str(table["innings_id"]),
                            table["table_type"],
                            column,
                            str(row.get(column, "")).strip().casefold(),
                        ]
                    )
                )
    return facts


def canonical_fingerprint(root: dict[str, Any]) -> str:
    return sha256_text("\n".join(sorted(canonical_fact_set(root))))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--roots", type=Path, required=True)
    parser.add_argument("--instances", type=Path, required=True)
    parser.add_argument("--splits", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    roots = load_jsonl(args.roots)
    instances = load_jsonl(args.instances)
    root_by_id = {root["root_id"]: root for root in roots}
    split_by_root = {
        row["root_id"]: row["split"]
        for row in csv.DictReader(args.splits.open(encoding="utf-8"))
    }
    failures: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    checks = Counter()
    passes = Counter()

    def check(code: str, condition: bool, item_id: str, detail: str = "") -> None:
        checks[code] += 1
        if condition:
            passes[code] += 1
        else:
            failures.append({"code": code, "item_id": item_id, "detail": detail})

    document_hash_splits: dict[str, set[str]] = defaultdict(set)
    document_hash_examples: dict[str, list[str]] = defaultdict(list)
    distractor_use = Counter()
    leak_re = re.compile(
        r"\bsource game\b|\bscorecard fingerprint\b|\banonymi[sz]ed\b|"
        r"\bsynthetic sample\b|\bgold table\b|\bmatch_\d{4}\b|"
        r"\b(?:batting|bowling|partnerships|fall of wickets)\[\d+\]\.",
        re.I,
    )

    for instance in instances:
        if instance["release_status"] != "RELEASE_CANDIDATE":
            continue
        iid = instance["instance_id"]
        root_id = instance["root_id"]
        root = root_by_id[root_id]
        split = split_by_root[root_id]
        generator = instance["private_metadata"]["generator"]
        check("INSTANCE_SPLIT_MATCH", generator.get("split") == split, iid, str(generator.get("split")))
        visible = instance["instruction"] + "\n" + "\n".join(doc["text"] for doc in instance["documents"])
        check("NO_CONSTRUCTION_TEXT_LEAK", leak_re.search(visible) is None, iid)
        for document in instance["documents"]:
            digest = sha256_text(document["text"])
            document_hash_splits[digest].add(split)
            if len(document_hash_examples[digest]) < 4:
                document_hash_examples[digest].append(f"{iid}:{document['document_id']}")

        if instance["view"] != "V3":
            continue
        selection = generator.get("distractor_selection", {})
        distractor_id = selection.get("root_id")
        check("DISTRACTOR_ROOT_EXISTS", distractor_id in root_by_id, iid, str(distractor_id))
        if distractor_id not in root_by_id:
            continue
        distractor_use[distractor_id] += 1
        distractor = root_by_id[distractor_id]
        target_venue = summary_value(root, "Venue")
        distractor_venue = summary_value(distractor, "Venue")
        check("DISTRACTOR_NOT_TARGET", distractor_id != root_id, iid)
        check(
            "DISTRACTOR_SAME_SPLIT",
            split_by_root.get(distractor_id) == split,
            iid,
            f"target={split}, distractor={split_by_root.get(distractor_id)}",
        )
        check(
            "TARGET_DISTRACTOR_VENUE_DISTINCT",
            bool(target_venue) and bool(distractor_venue) and target_venue != distractor_venue,
            iid,
            f"{target_venue} / {distractor_venue}",
        )
        check("TARGET_VENUE_IN_INSTRUCTION", target_venue in instance["instruction"], iid)
        target_docs = [doc for doc in instance["documents"] if not doc["document_id"].startswith("distractor_")]
        distractor_docs = [doc for doc in instance["documents"] if doc["document_id"].startswith("distractor_")]
        check("TARGET_DOCS_PRESENT", bool(target_docs), iid)
        check("DISTRACTOR_DOCS_PRESENT", bool(distractor_docs), iid)
        check(
            "TARGET_LABEL_SCOPE",
            all(doc["source_label"].startswith(f"{target_venue} dossier") for doc in target_docs),
            iid,
        )
        check(
            "DISTRACTOR_LABEL_SCOPE",
            all(doc["source_label"].startswith(f"{distractor_venue} dossier") for doc in distractor_docs),
            iid,
        )
        provenance_docs = {
            span["document_id"]
            for item in instance["gold"]["cell_provenance"]
            for span in item["evidence_spans"]
        }
        check(
            "NO_DISTRACTOR_GOLD_PROVENANCE",
            all(not document_id.startswith("distractor_") for document_id in provenance_docs),
            iid,
        )

    cross_split_docs = [
        {
            "hash": digest,
            "splits": sorted(splits),
            "examples": document_hash_examples[digest],
        }
        for digest, splits in document_hash_splits.items()
        if len(splits) > 1
    ]
    check("NO_EXACT_DOCUMENT_CROSS_SPLIT", not cross_split_docs, "DATASET", str(len(cross_split_docs)))

    ready_roots = [root for root in roots if split_by_root.get(root["root_id"]) in {"train", "dev", "test"}]
    exact_groups: dict[str, list[str]] = defaultdict(list)
    for root in ready_roots:
        exact_groups[canonical_fingerprint(root)].append(root["root_id"])
    cross_split_root_duplicates = []
    for digest, root_ids in exact_groups.items():
        splits = {split_by_root[root_id] for root_id in root_ids}
        if len(root_ids) > 1 and len(splits) > 1:
            cross_split_root_duplicates.append(
                {"hash": digest, "root_ids": root_ids, "splits": sorted(splits)}
            )
    check(
        "NO_EXACT_ROOT_CROSS_SPLIT",
        not cross_split_root_duplicates,
        "DATASET",
        str(len(cross_split_root_duplicates)),
    )

    fact_sets = {root["root_id"]: canonical_fact_set(root) for root in ready_roots}
    near_duplicates = []
    root_ids = sorted(fact_sets)
    for index, left in enumerate(root_ids):
        for right in root_ids[index + 1 :]:
            if split_by_root[left] == split_by_root[right]:
                continue
            union = fact_sets[left] | fact_sets[right]
            score = len(fact_sets[left] & fact_sets[right]) / len(union) if union else 1.0
            if score >= 0.85:
                near_duplicates.append(
                    {
                        "left": left,
                        "right": right,
                        "left_split": split_by_root[left],
                        "right_split": split_by_root[right],
                        "jaccard": round(score, 6),
                    }
                )
    if near_duplicates:
        warnings.append(
            {
                "code": "HIGH_CANONICAL_JACCARD_CROSS_SPLIT",
                "count": len(near_duplicates),
                "examples": near_duplicates[:50],
            }
        )

    max_reuse = max(distractor_use.values(), default=0)
    if max_reuse > 5:
        warnings.append(
            {
                "code": "DISTRACTOR_ROOT_REUSED_FREQUENTLY",
                "max_reuse": max_reuse,
                "roots": [
                    {"root_id": root_id, "count": count}
                    for root_id, count in distractor_use.most_common(20)
                    if count > 5
                ],
            }
        )

    report = {
        "audit_version": "0.1",
        "ready_roots": len(ready_roots),
        "release_instances": sum(
            instance["release_status"] == "RELEASE_CANDIDATE" for instance in instances
        ),
        "checks_total": sum(checks.values()),
        "checks_passed": sum(passes.values()),
        "failures": len(failures),
        "warnings": len(warnings),
        "status": "PASS" if not failures else "FAIL",
        "by_check": {
            code: {
                "total": checks[code],
                "passed": passes[code],
                "failed": checks[code] - passes[code],
            }
            for code in sorted(checks)
        },
        "failure_details": failures,
        "warning_details": warnings,
        "cross_split_document_duplicates": cross_split_docs,
        "cross_split_root_duplicates": cross_split_root_duplicates,
        "near_duplicate_pairs": near_duplicates,
        "distractor_reuse": {
            "unique_distractor_roots": len(distractor_use),
            "max_reuse": max_reuse,
            "distribution": dict(sorted(Counter(distractor_use.values()).items())),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({key: report[key] for key in report if key not in {
        "by_check", "failure_details", "warning_details", "cross_split_document_duplicates",
        "cross_split_root_duplicates", "near_duplicate_pairs"
    }}, indent=2))


if __name__ == "__main__":
    main()
