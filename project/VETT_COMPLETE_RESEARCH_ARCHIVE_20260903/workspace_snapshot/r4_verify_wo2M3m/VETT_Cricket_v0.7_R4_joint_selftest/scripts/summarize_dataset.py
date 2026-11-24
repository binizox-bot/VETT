#!/usr/bin/env python3
"""Summarize VETT-Cricket composition and difficulty operators."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--roots", type=Path, required=True)
    parser.add_argument("--instances", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    roots = load_jsonl(args.roots)
    instances = load_jsonl(args.instances)
    release = [x for x in instances if x["release_status"] == "RELEASE_CANDIDATE"]
    by_view: dict[str, dict[str, Any]] = {}
    for view in ("V0", "V1", "V2", "V3"):
        subset = [x for x in release if x["view"] == view]
        supports = Counter(
            item["support_type"]
            for instance in subset
            for item in instance["gold"]["cell_provenance"]
            if item["cell_id"] in set(instance["gold"]["scored_cell_ids"])
        )
        derivations = Counter(
            item["derivation"]
            for instance in subset
            for item in instance["gold"]["cell_provenance"]
            if item.get("derivation")
        )
        by_view[view] = {
            "instances": len(subset),
            "scored_cells": sum(len(x["gold"]["scored_cell_ids"]) for x in subset),
            "documents": {
                "min": min((len(x["documents"]) for x in subset), default=0),
                "mean": round(mean([len(x["documents"]) for x in subset]), 3) if subset else 0,
                "max": max((len(x["documents"]) for x in subset), default=0),
            },
            "input_characters": {
                "min": min((sum(len(d["text"]) for d in x["documents"]) for x in subset), default=0),
                "mean": round(
                    mean([sum(len(d["text"]) for d in x["documents"]) for x in subset]),
                    3,
                )
                if subset
                else 0,
                "max": max((sum(len(d["text"]) for d in x["documents"]) for x in subset), default=0),
            },
            "support_types": dict(sorted(supports.items())),
            "derivation_operators": dict(sorted(derivations.items())),
            "revision_claims": sum(
                len(x["private_metadata"].get("revision_claims", [])) for x in subset
            ),
            "distractor_documents": sum(
                d["document_id"].startswith("distractor_")
                for x in subset
                for d in x["documents"]
            ),
            "mean_shared_distractor_names": round(
                mean(
                    [
                        len(
                            x["private_metadata"]
                            .get("generator", {})
                            .get("distractor_selection", {})
                            .get("shared_normalized_names", [])
                        )
                        for x in subset
                    ]
                ),
                3,
            )
            if subset
            else 0,
        }

    report = {
        "root_count": len(roots),
        "root_statuses": dict(sorted(Counter(x["curation_status"] for x in roots).items())),
        "instance_count": len(instances),
        "release_statuses": dict(sorted(Counter(x["release_status"] for x in instances).items())),
        "views": dict(sorted(Counter(x["view"] for x in instances).items())),
        "release_candidate_count": len(release),
        "release_scored_cells": sum(len(x["gold"]["scored_cell_ids"]) for x in release),
        "by_view": by_view,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
