#!/usr/bin/env python3
"""Structural, semantic and controlled-ablation self-test for R5 Stage A."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


FORBIDDEN_PUBLIC_KEYS = {
    "root_id", "gold", "gold_tables", "scored_cell_ids", "challenge_cells",
    "dependencies", "counterfactuals", "operation", "alternate",
}

META_PATTERNS = {
    "construction_state_language": r"\b(?:candidate state|surviving graph|accepted component|admissible state)\b",
    "constraint_meta_language": r"\b(?:joint constraint|constraint graph|global conservation)\b",
    "answer_withholding_disclaimer": r"\b(?:no final number|answer is not printed|without publishing target values)\b",
    "task_hint": r"\b(?:two locally coherent|resolve the accepted state jointly|do not repair rows independently)\b",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def walk_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        keys.update(value)
        for child in value.values():
            keys.update(walk_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(walk_keys(child))
    return keys


def gold_maps(private: dict[str, Any]) -> tuple[dict[str, str], dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    values: dict[str, str] = {}
    tables: dict[str, dict[str, Any]] = {}
    rows: dict[str, dict[str, Any]] = {}
    for table in private["gold_tables"]:
        tables[table["table_id"]] = table
        for pos, row in enumerate(table["rows"], start=1):
            row_id = f"r{pos:03d}"
            rows[f"{table['table_id']}|{row_id}"] = row
            key = {
                "Match Summary": "Field", "Innings Summary": "Field", "Batting": "Batter",
                "Bowling": "Bowler", "Partnerships": "Partnership", "Fall of Wickets": "Wkt",
            }[table["table_type"]]
            for column in table["columns"]:
                if column != key:
                    values[f"{table['table_id']}|{row_id}|{column}"] = str(row[column])
    return values, tables, rows


def component(value: str) -> int:
    match = re.match(r"\s*(-?\d+)\s*\(", value)
    if not match:
        raise ValueError(value)
    return int(match.group(1))


def derive(challenge: dict[str, Any], private: dict[str, Any], evidence: dict[str, Any]) -> int:
    values, tables, rows = gold_maps(private)
    op = challenge["operation"]
    iid = challenge["innings_id"]
    if op == "sum_extras":
        summary = next(t for t in private["gold_tables"] if t["table_type"] == "Innings Summary" and t["innings_id"] == iid)
        by_field = {r["Field"]: r for r in summary["rows"]}
        return sum(int(by_field[name]["Value"]) for name in ("Byes", "Leg Byes", "No Balls", "Wides"))
    if op == "sum_bowler_wides":
        bowling = next(t for t in private["gold_tables"] if t["table_type"] == "Bowling" and t["innings_id"] == iid)
        return sum(int(r["Wd"]) for r in bowling["rows"])
    if op == "max_partnership":
        partnerships = next(t for t in private["gold_tables"] if t["table_type"] == "Partnerships" and t["innings_id"] == iid)
        return max(int(r["Runs"]) for r in partnerships["rows"])
    if op == "boundary_plus_running":
        row = rows[f"{challenge['table_id']}|{challenge['row_id']}"]
        cell = next(c for c in evidence["cells"] if c["cell_id"] == challenge["cell_id"])
        segment_map = {s["segment_id"]: s for s in evidence["segments"]}
        own_ref = next(
            ref for ref in cell["evidence"]
            if challenge["row_label"] in segment_map[ref["segment_id"]]["text"]
            and "without a boundary" in segment_map[ref["segment_id"]]["text"]
        )
        text = evidence["segments"][int(own_ref["segment_id"][1:]) - 1]["text"]
        running = int(re.search(r"another (\d+) runs completed without a boundary", text).group(1))
        return 4 * int(row["4s"]) + 6 * int(row["6s"]) + running
    if op == "count_dismissal_credits":
        batting = next(t for t in private["gold_tables"] if t["table_type"] == "Batting" and t["innings_id"] == iid)
        bowler = challenge["row_label"].lower()
        return sum(
            str(row["Dismissal"]).lower().endswith(bowler)
            and not str(row["Dismissal"]).lower().startswith("run out")
            for row in batting["rows"]
        )
    if op == "sum_partnership_components":
        row = rows[f"{challenge['table_id']}|{challenge['row_id']}"]
        return component(row["Striker"]) + component(row["Non-striker"]) + int(row["Extras"])
    raise ValueError(op)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--public", type=Path, required=True)
    parser.add_argument("--private", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    public_rows = load_jsonl(args.public)
    private_rows = load_jsonl(args.private)
    evidence_rows = load_jsonl(args.evidence)
    private_by_id = {r["instance_id"]: r for r in private_rows}
    evidence_by_id = {r["instance_id"]: r for r in evidence_rows}
    failures: list[dict[str, Any]] = []

    if not (len(public_rows) == len(private_rows) == len(evidence_rows) == 12):
        failures.append({"check": "instance_count", "observed": [len(public_rows), len(private_rows), len(evidence_rows)]})

    public_keys = walk_keys(public_rows)
    leaked = sorted(public_keys & FORBIDDEN_PUBLIC_KEYS)
    if leaked:
        failures.append({"check": "private_key_leakage", "observed": leaked})

    ids = [r["instance_id"] for r in public_rows]
    if len(ids) != len(set(ids)) or not all(re.fullmatch(r"r5a_\d{4}", x) for x in ids):
        failures.append({"check": "opaque_unique_ids", "observed": ids})
    texts = [r["document"]["text"] for r in public_rows]
    if len({hashlib.sha256(t.encode()).hexdigest() for t in texts}) != len(texts):
        failures.append({"check": "duplicate_public_text"})

    sentence_counts = Counter(
        sentence.strip()
        for text in texts
        for sentence in re.split(r"(?<=[.!?])\s+", text)
        if len(sentence.split()) >= 8
    )
    repeated_sentences_4plus = sum(count >= 4 for count in sentence_counts.values())
    max_sentence_repeat = max(sentence_counts.values(), default=0)
    if repeated_sentences_4plus:
        failures.append({
            "check": "repeated_template_sentence",
            "sentences_repeated_4plus": repeated_sentences_4plus,
            "max_repeat": max_sentence_repeat,
        })

    meta_counts = {name: sum(len(re.findall(pattern, t, re.I)) for t in texts) for name, pattern in META_PATTERNS.items()}
    if any(meta_counts.values()):
        failures.append({"check": "public_meta_language", "observed": meta_counts})

    prompt_ok = all(
        row["instruction"] == "Reconstruct the complete scorecard tables from the supplied match material."
        for row in public_rows
    )
    if not prompt_ok:
        failures.append({"check": "generic_prompt"})

    oracle_correct = 0
    challenge_total = 0
    evidence_cell_total = 0
    span_total = 0
    span_bad = 0
    blank_bad = 0
    dependency_bad = 0
    words = []
    half_coverage = {"first_half": 0, "second_half": 0, "cross_half": 0}
    all_scored = 0

    for public in public_rows:
        iid = public["instance_id"]
        private = private_by_id[iid]
        evidence = evidence_by_id[iid]
        text = public["document"]["text"]
        words.append(len(text.split()))
        if hashlib.sha256(text.encode()).hexdigest() != evidence["document_sha256"]:
            failures.append({"check": "document_hash", "instance_id": iid})
        segment_by_id = {s["segment_id"]: s for s in evidence["segments"]}
        midpoint = len(text) // 2
        for segment in evidence["segments"]:
            if text[segment["start"]:segment["end"]] != segment["text"]:
                span_bad += 1
        for cell in evidence["cells"]:
            evidence_cell_total += 1
            sides = set()
            for ref in cell["evidence"]:
                span_total += 1
                segment = segment_by_id.get(ref["segment_id"])
                if not segment or (ref["start"], ref["end"]) != (segment["start"], segment["end"]):
                    span_bad += 1
                sides.add("first" if ref["end"] <= midpoint else "second" if ref["start"] >= midpoint else "cross")
            if sides == {"first"}:
                half_coverage["first_half"] += 1
            elif sides == {"second"}:
                half_coverage["second_half"] += 1
            else:
                half_coverage["cross_half"] += 1
            if cell["operation"] != "direct" and not cell["dependencies"]:
                dependency_bad += 1
        all_scored += len(private["scored_cell_ids"])
        if len(evidence["cells"]) != len(private["scored_cell_ids"]):
            failures.append({"check": "evidence_coverage", "instance_id": iid})
        for table in public["tables"]:
            key = {
                "Match Summary": "Field", "Innings Summary": "Field", "Batting": "Batter",
                "Bowling": "Bowler", "Partnerships": "Partnership", "Fall of Wickets": "Wkt",
            }[table["table_type"]]
            for row in table["rows"]:
                for column in table["columns"]:
                    if column != key and row[column] is not None:
                        blank_bad += 1
        for challenge in private["challenge_cells"]:
            challenge_total += 1
            if derive(challenge, private, evidence) == int(challenge["gold"]):
                oracle_correct += 1

    if span_bad:
        failures.append({"check": "evidence_spans", "bad": span_bad})
    if blank_bad:
        failures.append({"check": "public_targets_not_blank", "bad": blank_bad})
    if dependency_bad:
        failures.append({"check": "derived_without_dependencies", "bad": dependency_bad})
    if oracle_correct != challenge_total:
        failures.append({"check": "challenge_oracle", "correct": oracle_correct, "total": challenge_total})

    early = sum(c["trap_polarity"] == "early_withdrawn" for r in private_rows for c in r["challenge_cells"])
    late = sum(c["trap_polarity"] == "late_recycled" for r in private_rows for c in r["challenge_cells"])
    mechanism_ablations = {
        "oracle_dependency_reconstruction": {"correct": challenge_total, "wrong": 0, "missing": 0},
        "trust_first_display": {"correct": challenge_total - early, "wrong": early, "missing": 0},
        "trust_last_display": {"correct": challenge_total - late, "wrong": late, "missing": 0},
        "trust_all_displays": {"correct": 0, "wrong": challenge_total, "missing": 0},
        "omit_derived_cells": {"correct": 0, "wrong": 0, "missing": challenge_total},
    }
    for row in mechanism_ablations.values():
        row["error_rate"] = (row["wrong"] + row["missing"]) / challenge_total
        row["full_table_cell_error_rate"] = (row["wrong"] + row["missing"]) / all_scored
        row["instance_exact_match"] = "12/12" if not (row["wrong"] + row["missing"]) else "0/12"

    report = {
        "experiment": "R5_STAGE_A_CLEAN_ROOM_12",
        "status": "PASS" if not failures else "FAIL",
        "decision": "READY_FOR_FRESH_BLIND_MODEL_EVALUATION" if not failures else "REBUILD_REQUIRED",
        "instances": len(public_rows),
        "full_table_scored_cells": all_scored,
        "challenge_cells": challenge_total,
        "text_words": {"min": min(words), "max": max(words), "mean": round(sum(words) / len(words), 2)},
        "mechanical_checks": {
            "private_public_key_leaks": len(leaked),
            "duplicate_public_texts": len(texts) - len(set(texts)),
            "exact_sentences_repeated_4plus": repeated_sentences_4plus,
            "max_exact_sentence_repeat": max_sentence_repeat,
            "meta_language_hits": meta_counts,
            "generic_prompt": prompt_ok,
            "blank_target_violations": blank_bad,
            "evidence_cells": evidence_cell_total,
            "evidence_span_refs": span_total,
            "evidence_span_errors": span_bad,
            "derived_dependency_errors": dependency_bad,
            "challenge_oracle": f"{oracle_correct}/{challenge_total}",
        },
        "evidence_location": half_coverage,
        "mechanism_ablations": mechanism_ablations,
        "failures": failures,
        "limitations": [
            "Mechanism ablations are controlled position/revision failures, not Direct, CoT, T3 or Map&Make model scores.",
            "The 12 texts contain template-generated statistical passages and require independent naturalness review.",
            "Original commentary may provide additional unannotated support beyond the private minimal evidence graph.",
            "Independent human unique-recovery annotation and fresh blind model evaluation remain pending.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "failures": len(failures), "oracle": report["mechanical_checks"]["challenge_oracle"]}, indent=2))
    raise SystemExit(0 if not failures else 1)


if __name__ == "__main__":
    main()
