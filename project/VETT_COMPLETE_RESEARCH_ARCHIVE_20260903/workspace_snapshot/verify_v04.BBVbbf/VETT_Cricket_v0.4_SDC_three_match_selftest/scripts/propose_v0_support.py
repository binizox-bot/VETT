#!/usr/bin/env python3
"""Create conservative annotation proposals for V0 natural reports.

These proposals reduce annotation effort. They are never promoted to gold
without human verification.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sentences(text: str) -> list[tuple[int, int, str]]:
    out = []
    for match in re.finditer(r"[^.!?]+(?:[.!?]+|$)", text):
        segment = match.group(0)
        if segment.strip():
            out.append((match.start(), match.end(), segment))
    return out


def value_forms(value: Any, number_forms) -> set[str]:
    text = str(value).strip()
    forms = {text.casefold()}
    if re.fullmatch(r"\d+", text):
        forms.update(x.casefold() for x in number_forms(int(text)))
    return {x for x in forms if x}


def find_support(text: str, anchor: str, forms: set[str]) -> tuple[dict[str, Any] | None, str]:
    anchor_low = anchor.casefold()
    for start, end, sentence in sentences(text):
        low = sentence.casefold()
        if anchor_low and anchor_low not in low:
            continue
        for form in sorted(forms, key=len, reverse=True):
            if re.search(rf"(?<![\w]){re.escape(form)}(?![\w])", low):
                quote = text[start:end]
                return (
                    {
                        "document_id": "natural_report",
                        "start": start,
                        "end": end,
                        "quote_hash": hashlib.sha256(quote.encode("utf-8")).hexdigest(),
                    },
                    "anchor_and_value_same_sentence",
                )
    return None, "no_same_sentence_anchor_value"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--roots", type=Path, required=True)
    parser.add_argument("--instances", type=Path, required=True)
    parser.add_argument("--audit-module-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.audit_module_dir.resolve()))
    from audit_dataset import number_forms  # type: ignore

    roots = {x["root_id"]: x for x in load_jsonl(args.roots)}
    v0_instances = [
        x
        for x in load_jsonl(args.instances)
        if x["view"] == "V0" and x["release_status"] == "NEEDS_SUPPORT_ANNOTATION"
    ]
    output = []
    for instance in v0_instances:
        root = roots[instance["root_id"]]
        text = instance["documents"][0]["text"]
        table_by_id = {t["table_id"]: t for t in root["tables"]}
        row_by_key = {
            (t["table_id"], row["row_id"]): row
            for t in root["tables"]
            for row in t["rows"]
        }
        proposals = []
        for cell in root["cells"]:
            table = table_by_id[cell["table_id"]]
            row = row_by_key[(cell["table_id"], cell["row_id"])]
            anchor = ""
            for key in ("Batter", "Bowler", "Partnership", "Batter", "Field"):
                if row.get(key):
                    anchor = str(row[key])
                    break
            if cell["column"] in {"Batter", "Bowler", "Partnership"}:
                anchor = str(cell["value"])
                forms = {anchor.casefold()}
            elif cell["column"] == "Field":
                # Schema labels are handled separately from value provenance.
                proposals.append(
                    {
                        "cell_id": cell["cell_id"],
                        "proposal": "NOT_SCORED_SCHEMA_LABEL",
                        "confidence": 1.0,
                        "evidence_spans": [],
                        "reason": "summary field label",
                    }
                )
                continue
            else:
                forms = value_forms(cell["value"], number_forms)
            span, reason = find_support(text, anchor, forms)
            proposal = "DIRECT_CANDIDATE" if span else "TABLE_ONLY_CANDIDATE"
            confidence = 0.88 if span and str(cell["value"]).casefold() in text.casefold() else 0.68 if span else 0.45
            proposals.append(
                {
                    "cell_id": cell["cell_id"],
                    "proposal": proposal,
                    "confidence": confidence,
                    "evidence_spans": [span] if span else [],
                    "reason": reason,
                }
            )
        output.append(
            {
                "instance_id": instance["instance_id"],
                "root_id": root["root_id"],
                "annotation_status": "MODEL_OR_HUMAN_REVIEW_REQUIRED",
                "proposals": proposals,
            }
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "".join(json.dumps(x, ensure_ascii=False, sort_keys=True) + "\n" for x in output),
        encoding="utf-8",
    )
    direct = sum(p["proposal"] == "DIRECT_CANDIDATE" for x in output for p in x["proposals"])
    table_only = sum(p["proposal"] == "TABLE_ONLY_CANDIDATE" for x in output for p in x["proposals"])
    print(json.dumps({"instances": len(output), "direct_candidates": direct, "table_only_candidates": table_only}, indent=2))


if __name__ == "__main__":
    main()
