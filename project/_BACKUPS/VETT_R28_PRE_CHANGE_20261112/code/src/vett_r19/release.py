from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from vett_r18.release import (
    PILOT_MATCH_IDS,
    _cross_instance_language_metrics,
    _file_record,
    _shortcut_metrics,
    _write_json,
)

from .auditor import audit_instance
from .generator import VERSION, build_instance, load_canonical_roots


BundleTuple = tuple[dict[str, Any], dict[str, Any], dict[str, Any]]


def _minute(document: dict[str, Any]) -> int:
    match = re.fullmatch(r"T\+(\d+)m", str(document.get("published_at", "")))
    return int(match.group(1)) if match else -1


def _amendment_rank_metrics(
    bundles: list[BundleTuple], max_rank: int = 16
) -> dict[str, dict[str, Any]]:
    correct_by_rank = {rank: 0 for rank in range(1, max_rank + 1)}
    total = 0
    for public, gold, evidence in bundles:
        documents = {
            document["document_id"]: document
            for document in public.get("documents", [])
        }
        schema = {
            target["target_id"]: target for target in public.get("target_schema", [])
        }
        for target in gold.get("targets", []):
            if not target.get("decisive_support"):
                continue
            total += 1
            target_schema = schema[target["target_id"]]
            candidates = [
                claim
                for claim in evidence.get("claims", [])
                if claim.get("status", "asserted") == "asserted"
                and claim.get("innings") == target_schema.get("innings")
                and claim.get("field") == target_schema.get("field")
                and re.search(
                    r"\bamends\s+K[0-9A-F]{8}-(?:M|I1|I2)\b",
                    documents[claim["document_id"]].get("text", ""),
                )
            ]
            ranked = sorted(
                candidates,
                key=lambda claim: _minute(documents[claim["document_id"]]),
                reverse=True,
            )
            for rank in range(1, max_rank + 1):
                prediction = (
                    ranked[rank - 1].get("value") if len(ranked) >= rank else None
                )
                correct_by_rank[rank] += int(prediction == target.get("value"))
    return {
        f"amendment_rank_{rank:02d}": {
            "correct": correct,
            "total": total,
            "accuracy": round(correct / total, 6) if total else 0.0,
        }
        for rank, correct in correct_by_rank.items()
    }


def _strict_support_metrics(bundles: list[BundleTuple]) -> dict[str, Any]:
    document_counts: dict[str, int] = {}
    instance_shares: dict[str, float] = {}
    for public, gold, evidence in bundles:
        claims = {claim["claim_id"]: claim for claim in evidence.get("claims", [])}
        support_documents = [
            claims[target["decisive_support"][0]]["document_id"]
            for target in gold.get("targets", [])
            if target.get("decisive_support")
        ]
        counts = Counter(support_documents)
        instance_id = str(public.get("instance_id"))
        document_counts[instance_id] = len(counts)
        instance_shares[instance_id] = round(
            max(counts.values()) / len(support_documents), 6
        )
    maximum_share = max(instance_shares.values()) if instance_shares else 1.0
    passed = (
        bool(instance_shares)
        and min(document_counts.values()) == 14
        and maximum_share <= 0.10
    )
    return {
        "status": "PASS" if passed else "FAIL",
        "maximum_document_share": round(maximum_share, 6),
        "document_counts": document_counts,
        "instance_shares": instance_shares,
    }


def _release_report(summary: dict[str, Any]) -> str:
    rows = "\n".join(
        f"| {name} | {item['correct']}/{item['total']} | {item['accuracy']:.2%} |"
        for name, item in summary["public_shortcuts"].items()
    )
    return f"""# VETT-Cricket R19 Fragmented Terminal Pilot

## Release decision

**{summary['status']}** — {summary['passed_instances']}/{summary['instances']} instances passed every machine gate.

## R19 hardening

- Fourteen direct targets use fourteen separate decisive documents per instance.
- Maximum answer concentration in one document: {summary['decisive_support']['maximum_document_share']:.2%}
- Each field receives a different one-to-fourteen-layer wrong amendment chain; its terminal claim is explicitly voided.
- Fixed amendment-rank selectors 1 through 16 are release-gated at 10%.
- Identifier-normalized unique five-word openings: {summary['cross_instance_language']['normalized_unique_ratio']:.2%}

| Public-only shortcut | Correct | Accuracy |
| --- | ---: | ---: |
{rows}

Passing these attacks is not proof that a language model cannot solve the task. External blind-model evaluation and human naturalness review remain unperformed.
"""


def _dataset_card(summary: dict[str, Any]) -> str:
    return f"""# Dataset Card: {summary['dataset_version']}

R19 fragments every direct target into a separate decisive document. Per-field late wrong-amendment chains have different depths from one to fourteen, and each terminal wrong claim is explicitly voided. Solvers must resolve each field through the public evidence graph rather than selecting a fixed amendment rank.

Use only `public/` as model input. Keep `private/` and `audit/` outside the solving context.

Machine release status: **{summary['status']}**. Blind language-model performance and human naturalness remain unverified.
"""


def build_release(
    roots_path: Path,
    output_dir: Path,
    selected_ids: list[str] | None = None,
    *,
    seed: int = 19041,
) -> dict[str, Any]:
    selected = selected_ids or PILOT_MATCH_IDS
    if len(set(selected)) != len(selected):
        raise ValueError("selected match IDs must be unique")
    output_dir.mkdir(parents=True, exist_ok=True)
    if any(path.is_file() for path in output_dir.rglob("*")):
        raise FileExistsError(f"release directory is not empty: {output_dir}")

    roots = load_canonical_roots(roots_path, set(selected))
    roots_by_id = {root["root_id"]: root for root in roots}
    audits: list[dict[str, Any]] = []
    bundles: list[BundleTuple] = []
    for match_id in selected:
        bundle = build_instance(roots_by_id[match_id], seed=seed)
        audit = audit_instance(bundle.public, bundle.gold, bundle.evidence)
        _write_json(output_dir / "public" / match_id / "public_instance.json", bundle.public)
        _write_json(output_dir / "private" / match_id / "private_gold.json", bundle.gold)
        _write_json(
            output_dir / "private" / match_id / "private_evidence.json",
            bundle.evidence,
        )
        _write_json(output_dir / "audit" / f"{match_id}.audit.json", audit)
        audits.append(audit)
        bundles.append((bundle.public, bundle.gold, bundle.evidence))

    baseline_names = (
        "first_mention",
        "last_array_mention",
        "latest_timestamp",
        "majority_vote",
    )
    baselines: dict[str, dict[str, Any]] = {}
    for name in baseline_names:
        correct = sum(audit["baselines"][name]["correct"] for audit in audits)
        total = sum(audit["baselines"][name]["total"] for audit in audits)
        baselines[name] = {
            "correct": correct,
            "total": total,
            "accuracy": round(correct / total, 6) if total else 0.0,
        }

    shortcuts = _shortcut_metrics(bundles)
    ranked_amendments = _amendment_rank_metrics(bundles)
    shortcuts.update(ranked_amendments)
    shortcuts["latest_amendment_per_target"] = dict(
        ranked_amendments["amendment_rank_01"]
    )
    language = _cross_instance_language_metrics([bundle[0] for bundle in bundles])
    support = _strict_support_metrics(bundles)
    release_passed = (
        all(audit["status"] == "PASS" for audit in audits)
        and language["status"] == "PASS"
        and support["status"] == "PASS"
        and all(item["accuracy"] <= 0.10 for item in shortcuts.values())
    )
    summary = {
        "dataset_version": VERSION,
        "status": "PASS" if release_passed else "FAIL",
        "seed": seed,
        "instances": len(audits),
        "passed_instances": sum(audit["status"] == "PASS" for audit in audits),
        "match_ids": selected,
        "documents": sum(audit["summary"]["documents"] for audit in audits),
        "claims": sum(audit["summary"]["claims"] for audit in audits),
        "direct_targets": sum(audit["summary"]["direct_targets"] for audit in audits),
        "derived_targets": sum(audit["summary"]["derived_targets"] for audit in audits),
        "counterfactuals": sum(len(audit["counterfactuals"]) for audit in audits),
        "edge_ablations": sum(len(audit["edge_ablations"]) for audit in audits),
        "baselines": baselines,
        "public_shortcuts": shortcuts,
        "decisive_support": support,
        "cross_instance_language": language,
    }
    _write_json(output_dir / "RELEASE_SUMMARY.json", summary)
    (output_dir / "RELEASE_REPORT.md").write_text(
        _release_report(summary), encoding="utf-8"
    )
    (output_dir / "DATASET_CARD.md").write_text(
        _dataset_card(summary), encoding="utf-8"
    )
    manifest_files = [
        _file_record(output_dir, path)
        for path in sorted(output_dir.rglob("*"))
        if path.is_file() and path.name != "MANIFEST.json"
    ]
    _write_json(
        output_dir / "MANIFEST.json",
        {
            "dataset_version": VERSION,
            "seed": seed,
            "file_count_excluding_manifest": len(manifest_files),
            "files": manifest_files,
        },
    )
    return summary


def audit_release(release_dir: Path) -> dict[str, Any]:
    manifest_errors: list[str] = []
    try:
        manifest = json.loads(
            (release_dir / "MANIFEST.json").read_text(encoding="utf-8")
        )
        records = manifest.get("files", [])
    except (OSError, json.JSONDecodeError, AttributeError) as exc:
        manifest = {}
        records = []
        manifest_errors.append(f"manifest unreadable: {exc}")
    records_by_path = {
        record.get("path"): record
        for record in records
        if isinstance(record, dict) and isinstance(record.get("path"), str)
    }
    if manifest.get("file_count_excluding_manifest") != len(records):
        manifest_errors.append("manifest file count does not match its records")
    if len(records_by_path) != len(records):
        manifest_errors.append("manifest contains a duplicate or invalid path")
    actual_files = {
        path.relative_to(release_dir).as_posix(): path
        for path in sorted(release_dir.rglob("*"))
        if path.is_file() and path.name != "MANIFEST.json"
    }
    if set(records_by_path) != set(actual_files):
        manifest_errors.append("manifest file set differs from release file set")
    for relative_path in sorted(set(records_by_path) & set(actual_files)):
        actual = _file_record(release_dir, actual_files[relative_path])
        expected = records_by_path[relative_path]
        if expected.get("bytes") != actual["bytes"]:
            manifest_errors.append(f"byte-count mismatch: {relative_path}")
        if expected.get("sha256") != actual["sha256"]:
            manifest_errors.append(f"sha256 mismatch: {relative_path}")

    semantic_errors: list[str] = []
    audits: list[dict[str, Any]] = []
    bundles: list[BundleTuple] = []
    public_paths = sorted((release_dir / "public").glob("*/public_instance.json"))
    discovered_ids = [path.parent.name for path in public_paths]
    try:
        summary = json.loads(
            (release_dir / "RELEASE_SUMMARY.json").read_text(encoding="utf-8")
        )
        if summary.get("dataset_version") != VERSION:
            semantic_errors.append("release summary has an unexpected dataset version")
        if summary.get("match_ids") != discovered_ids:
            semantic_errors.append("release summary match IDs differ from public files")
    except (OSError, json.JSONDecodeError, AttributeError) as exc:
        semantic_errors.append(f"summary unreadable: {exc}")
    for public_path in public_paths:
        match_id = public_path.parent.name
        try:
            public = json.loads(public_path.read_text(encoding="utf-8"))
            gold = json.loads(
                (release_dir / "private" / match_id / "private_gold.json").read_text(
                    encoding="utf-8"
                )
            )
            evidence = json.loads(
                (release_dir / "private" / match_id / "private_evidence.json").read_text(
                    encoding="utf-8"
                )
            )
            audits.append(audit_instance(public, gold, evidence))
            bundles.append((public, gold, evidence))
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            semantic_errors.append(f"{match_id}: {exc}")

    shortcuts = _shortcut_metrics(bundles)
    ranked_amendments = _amendment_rank_metrics(bundles)
    shortcuts.update(ranked_amendments)
    shortcuts["latest_amendment_per_target"] = dict(
        ranked_amendments["amendment_rank_01"]
    )
    language = _cross_instance_language_metrics([bundle[0] for bundle in bundles])
    support = _strict_support_metrics(bundles)
    semantic_passed = (
        bool(audits)
        and not semantic_errors
        and all(audit["status"] == "PASS" for audit in audits)
        and language["status"] == "PASS"
        and support["status"] == "PASS"
        and all(item["accuracy"] <= 0.10 for item in shortcuts.values())
    )
    manifest_passed = not manifest_errors
    return {
        "status": "PASS" if manifest_passed and semantic_passed else "FAIL",
        "manifest_status": "PASS" if manifest_passed else "FAIL",
        "manifest_errors": manifest_errors,
        "semantic_errors": semantic_errors,
        "instances": len(audits),
        "passed_instances": sum(audit["status"] == "PASS" for audit in audits),
        "cross_instance_language": language,
        "public_shortcuts": shortcuts,
        "decisive_support": support,
    }


__all__ = ["PILOT_MATCH_IDS", "audit_release", "build_release"]
