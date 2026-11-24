#!/usr/bin/env python3
"""Structural, contract and oracle audit for the R3 probe."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


FORBIDDEN_PUBLIC_KEYS = {
    "gold",
    "gold_value",
    "cell_id",
    "scored_cell_ids",
    "cell_provenance",
    "private_metadata",
    "table_id",
    "row_id",
}
META_SHORTCUTS = (
    r"\btherefore the answer is\b",
    r"\bdrops? by (?:one|two|three|\d+)\b",
    r"\bsubtract(?:s|ed|ing)?\b",
    r"\badd(?:s|ed|ing)?\s+(?:one|two|three|\d+)\b",
    r"\bleav(?:e|es|ing)\s+exactly\b",
    r"\bcorrected total is\b",
)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def walk_keys(value: Any) -> set[str]:
    keys = set()
    if isinstance(value, dict):
        keys.update(value)
        for child in value.values():
            keys.update(walk_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(walk_keys(child))
    return keys


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--blind", type=Path, required=True)
    parser.add_argument("--scoring", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--construction-dir", type=Path, required=True)
    parser.add_argument("--oracle-score", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    blind = load_jsonl(args.blind)
    scoring = load_jsonl(args.scoring)
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    failures = []
    details = []
    forbidden = sorted(walk_keys(blind) & FORBIDDEN_PUBLIC_KEYS)
    if forbidden:
        failures.append({"check": "public_forbidden_keys", "observed": forbidden})
    if (len(blind), len(scoring), len(manifest)) != (6, 6, 3):
        failures.append(
            {
                "check": "counts",
                "blind": len(blind),
                "scoring": len(scoring),
                "manifest": len(manifest),
            }
        )

    for item in manifest:
        root_id = item["root_id"]
        candidate = json.loads(
            (args.construction_dir / f"{root_id}.r3.json").read_text(encoding="utf-8")
        )
        commentary = candidate["commentary_text"]
        paragraphs = [p for p in commentary.split("\n\n") if p.strip()]
        words = len(commentary.split())
        shortcut_hits = [
            pattern for pattern in META_SHORTCUTS if re.search(pattern, commentary, re.I)
        ]
        scalar_records = candidate["scalar_target_records"]
        graph = candidate["shared_event_graph"]
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])
        connected_targets = set(graph.get("connected_primary_targets", []))
        scalar_ids = {record["cell_id"] for record in scalar_records}
        composite_ids = {
            record["cell_id"] for record in candidate["composite_target_records"]
        }
        valid_graph_targets = scalar_ids | composite_ids
        root_detail = {
            "root_id": root_id,
            "words": words,
            "paragraphs": len(paragraphs),
            "scalar_records": len(scalar_records),
            "composite_records": len(candidate["composite_target_records"]),
            "graph_nodes": len(nodes),
            "graph_edges": len(edges),
            "connected_primary_targets": len(connected_targets & scalar_ids),
            "meta_shortcut_hits": shortcut_hits,
        }
        details.append(root_detail)
        if not 2800 <= words <= 3600:
            failures.append({"check": "commentary_length", **root_detail})
        if len(paragraphs) < 24:
            failures.append({"check": "paragraph_count", **root_detail})
        if shortcut_hits:
            failures.append({"check": "meta_shortcuts", **root_detail})
        if len(connected_targets & scalar_ids) < 8:
            failures.append({"check": "shared_graph_coverage", **root_detail})
        node_ids = {node.get("node_id") for node in nodes}
        malformed_nodes = [
            node.get("node_id")
            for node in nodes
            if not all(
                key in node
                for key in (
                    "node_id",
                    "event_id",
                    "event_type",
                    "status",
                    "paragraph_id",
                    "affected_ledgers",
                )
            )
            or not isinstance(node.get("affected_ledgers"), list)
        ]
        malformed_edges = [
            edge
            for edge in edges
            if not all(key in edge for key in ("from", "to", "relation"))
            or edge.get("from") not in node_ids
            or (
                edge.get("to") not in node_ids
                and edge.get("to") not in valid_graph_targets
            )
        ]
        if malformed_nodes:
            failures.append(
                {"check": "malformed_graph_nodes", "root_id": root_id, "nodes": malformed_nodes}
            )
        if malformed_edges:
            failures.append(
                {"check": "malformed_graph_edges", "root_id": root_id, "edges": malformed_edges}
            )
        for record in scalar_records:
            check = {
                "root_id": root_id,
                "cell_id": record.get("cell_id"),
                "dependency_depth": record.get("dependency_depth"),
                "state_nodes": len(record.get("state_nodes", [])),
                "paragraph_ids": len(set(record.get("paragraph_ids", []))),
                "ledgers": len(set(record.get("ledgers", []))),
                "solution_steps": len(record.get("solution_chain", [])),
                "direct_final_mention": record.get("direct_final_mention"),
            }
            if check["dependency_depth"] < 6:
                failures.append({"check": "dependency_depth", **check})
            if check["state_nodes"] < 6:
                failures.append({"check": "state_nodes", **check})
            if check["paragraph_ids"] < 3:
                failures.append({"check": "paragraph_spread", **check})
            if check["ledgers"] < 2:
                failures.append({"check": "ledger_count", **check})
            if check["solution_steps"] < 4:
                failures.append({"check": "solution_chain", **check})
            if check["direct_final_mention"] is not False:
                failures.append({"check": "direct_final_mention", **check})

    oracle = json.loads(args.oracle_score.read_text(encoding="utf-8"))
    oracle_overall = oracle["groups"]["overall"]
    if not (
        oracle_overall["gold"] == 48
        and oracle_overall["correct"] == 48
        and oracle_overall["missing"] == 0
        and oracle_overall["incorrect"] == 0
    ):
        failures.append({"check": "semantic_oracle", "observed": oracle_overall})

    report = {
        "audit_version": "0.1",
        "status": "PASS" if not failures else "FAIL",
        "blind_sha256": sha256(args.blind),
        "scoring_sha256": sha256(args.scoring),
        "forbidden_public_keys": forbidden,
        "details": details,
        "oracle": oracle_overall,
        "failures": failures,
        "limitations": [
            "Declared graph connectivity is not a proof of semantic unique solvability.",
            "Independent inverse extraction and human double annotation remain required.",
            "Numeric substring leakage requires contextual human review because ordinary cricket numbers recur naturally.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": report["status"], "failures": len(failures)}, indent=2))
    raise SystemExit(0 if not failures else 1)


if __name__ == "__main__":
    main()
