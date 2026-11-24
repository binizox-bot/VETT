from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from .auditor import audit_instance
from .generator import build_instance, load_canonical_roots


PILOT_MATCH_IDS = [
    "match_0003",
    "match_0007",
    "match_0009",
    "match_0025",
    "match_0026",
    "match_0030",
]


def _cross_instance_language_metrics(
    public_instances: list[dict[str, Any]],
) -> dict[str, Any]:
    openings = [
        " ".join(span.get("text", "").lower().split()[:5])
        for public in public_instances
        for document in public.get("documents", [])
        for span in document.get("spans", [])
        if span.get("text", "").strip()
    ]
    counts = Counter(openings)
    total = len(openings)
    unique_ratio = len(counts) / total if total else 0.0
    maximum_ratio = counts.most_common(1)[0][1] / total if counts and total else 1.0
    passed = bool(total) and unique_ratio >= 0.70 and maximum_ratio <= 0.08
    return {
        "status": "PASS" if passed else "FAIL",
        "span_count": total,
        "unique_five_word_openings": len(counts),
        "unique_five_word_opening_ratio": round(unique_ratio, 6),
        "maximum_five_word_opening_ratio": round(maximum_ratio, 6),
    }


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _file_record(root: Path, path: Path) -> dict[str, Any]:
    content = path.read_bytes()
    return {
        "path": path.relative_to(root).as_posix(),
        "bytes": len(content),
        "sha256": hashlib.sha256(content).hexdigest(),
    }


def _release_report(summary: dict[str, Any]) -> str:
    baseline_rows = "\n".join(
        f"| {name} | {metrics['correct']}/{metrics['total']} | {metrics['accuracy']:.2%} |"
        for name, metrics in summary["baselines"].items()
    )
    return f"""# VETT-Cricket R17 Implicit Trust Pilot

## Release decision

**{summary['status']}** — {summary['passed_instances']}/{summary['instances']} instances passed every adversarial machine gate.

## Scope

- Version: `{summary['dataset_version']}`
- Seed: `{summary['seed']}`
- Roots: {', '.join(summary['match_ids'])}
- Public numeric authority ranking: **absent**
- Documents: {summary['documents']}
- Claims: {summary['claims']}
- Scored targets: {summary['targets']} ({summary['direct_targets']} graph-resolved, {summary['derived_targets']} derived)
- Decisive-span deletion tests: {summary['counterfactuals']}
- Individual graph-edge ablations: {summary['edge_ablations']}
- Unique five-word opening ratio: {summary['cross_instance_language']['unique_five_word_opening_ratio']:.2%}
- Most common five-word opening ratio: {summary['cross_instance_language']['maximum_five_word_opening_ratio']:.2%}

## Shortcut baselines

| Baseline | Correct | Accuracy |
| --- | ---: | ---: |
{baseline_rows}

The policy-free reference resolver achieved {summary['targets']}/{summary['targets']}. These baselines are structural diagnostics, not proof that a language model fails.

## Difficulty in every instance

- two-stage correction-of-correction with exact scope limits;
- multi-hop scorer-to-radio-to-wire-to-cache ancestry;
- a late stale web page and non-chronological document array;
- a signed-looking but explicitly unissued draft plus registry void;
- withdrawn apparent wickets after overstep review;
- two internally reconciled wrong score worlds;
- cross-innings collisions and derived cricket constraints;
- literal public witnesses for every private amendment, withdrawal, and copy edge.

## Audit boundary

- No human naturalness audit was performed.
- No external blind language-model run was performed.
- Mechanical language checks reject known grammar artifacts and excessive repetition but do not establish human realism.
- The material is controlled semi-synthetic and is not represented as observed ball-by-ball commentary.
- This pilot supports a direction decision; it is not yet a public benchmark claim.
"""


def _dataset_card(summary: dict[str, Any]) -> str:
    return f"""# Dataset Card: {summary['dataset_version']}

R17 evaluates final-state reconstruction from explicit public amendments, withdrawals, scope limits, and copy ancestry without exposing a numeric source-priority table. Public document order is deliberately shuffled. Private artifacts contain claim semantics, graph edges, gold, and audits.

Use only `public/` as model input. Keep `private/` and `audit/` outside the solving context. Exposing the whole release invalidates evaluation.

Machine release status: **{summary['status']}**. Human naturalness and blind model performance remain unverified.
"""


def build_release(
    roots_path: Path,
    output_dir: Path,
    selected_ids: list[str] | None = None,
    *,
    seed: int = 17023,
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
    public_instances: list[dict[str, Any]] = []
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
        public_instances.append(bundle.public)

    baseline_names = (
        "first_mention",
        "last_array_mention",
        "latest_timestamp",
        "majority_vote",
    )
    aggregate_baselines: dict[str, dict[str, Any]] = {}
    for name in baseline_names:
        correct = sum(audit["baselines"][name]["correct"] for audit in audits)
        total = sum(audit["baselines"][name]["total"] for audit in audits)
        aggregate_baselines[name] = {
            "correct": correct,
            "total": total,
            "accuracy": round(correct / total, 6) if total else 0.0,
        }

    cross_instance_language = _cross_instance_language_metrics(public_instances)
    release_passed = (
        all(audit["status"] == "PASS" for audit in audits)
        and cross_instance_language["status"] == "PASS"
    )
    summary = {
        "dataset_version": "VETT-Cricket-v0.23-R17-pilot",
        "status": "PASS" if release_passed else "FAIL",
        "seed": seed,
        "instances": len(audits),
        "passed_instances": sum(audit["status"] == "PASS" for audit in audits),
        "match_ids": selected,
        "public_authority_ranking": False,
        "documents": sum(audit["summary"]["documents"] for audit in audits),
        "claims": sum(audit["summary"]["claims"] for audit in audits),
        "direct_targets": sum(audit["summary"]["direct_targets"] for audit in audits),
        "derived_targets": sum(audit["summary"]["derived_targets"] for audit in audits),
        "targets": sum(
            audit["summary"]["direct_targets"] + audit["summary"]["derived_targets"]
            for audit in audits
        ),
        "counterfactuals": sum(len(audit["counterfactuals"]) for audit in audits),
        "edge_ablations": sum(len(audit["edge_ablations"]) for audit in audits),
        "baselines": aggregate_baselines,
        "cross_instance_language": cross_instance_language,
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
            "dataset_version": summary["dataset_version"],
            "seed": seed,
            "file_count_excluding_manifest": len(manifest_files),
            "files": manifest_files,
        },
    )
    return summary


def audit_release(release_dir: Path) -> dict[str, Any]:
    manifest_errors: list[str] = []
    manifest_path = release_dir / "MANIFEST.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        records = manifest.get("files", [])
    except (OSError, json.JSONDecodeError, AttributeError) as exc:
        manifest = {}
        records = []
        manifest_errors.append(f"manifest unreadable: {exc}")
    records_by_path: dict[str, dict[str, Any]] = {}
    for record in records:
        path = record.get("path") if isinstance(record, dict) else None
        if not isinstance(path, str):
            manifest_errors.append("manifest record lacks a path")
            continue
        if path in records_by_path:
            manifest_errors.append(f"duplicate manifest path: {path}")
        records_by_path[path] = record
    if manifest.get("file_count_excluding_manifest") != len(records):
        manifest_errors.append("manifest file count does not match records")
    actual_files = {
        path.relative_to(release_dir).as_posix(): path
        for path in sorted(release_dir.rglob("*"))
        if path.is_file() and path.name != "MANIFEST.json"
    }
    for missing in sorted(set(records_by_path) - set(actual_files)):
        manifest_errors.append(f"missing file: {missing}")
    for extra in sorted(set(actual_files) - set(records_by_path)):
        manifest_errors.append(f"unlisted file: {extra}")
    for relative_path in sorted(set(records_by_path) & set(actual_files)):
        expected = records_by_path[relative_path]
        actual = _file_record(release_dir, actual_files[relative_path])
        if expected.get("bytes") != actual["bytes"]:
            manifest_errors.append(f"byte-count mismatch: {relative_path}")
        if expected.get("sha256") != actual["sha256"]:
            manifest_errors.append(f"sha256 mismatch: {relative_path}")

    semantic_errors: list[str] = []
    results: list[dict[str, Any]] = []
    public_instances: list[dict[str, Any]] = []
    public_paths = sorted((release_dir / "public").glob("*/public_instance.json"))
    discovered_ids = [path.parent.name for path in public_paths]
    try:
        summary = json.loads(
            (release_dir / "RELEASE_SUMMARY.json").read_text(encoding="utf-8")
        )
        expected_ids = summary.get("match_ids", [])
        if discovered_ids != expected_ids:
            semantic_errors.append(
                f"public instance IDs {discovered_ids} != summary IDs {expected_ids}"
            )
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
                (
                    release_dir / "private" / match_id / "private_evidence.json"
                ).read_text(encoding="utf-8")
            )
            results.append(audit_instance(public, gold, evidence))
            public_instances.append(public)
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            semantic_errors.append(f"{match_id}: {exc}")
    manifest_passed = not manifest_errors
    cross_instance_language = _cross_instance_language_metrics(public_instances)
    semantic_passed = (
        bool(results)
        and not semantic_errors
        and all(result["status"] == "PASS" for result in results)
        and cross_instance_language["status"] == "PASS"
    )
    return {
        "status": "PASS" if manifest_passed and semantic_passed else "FAIL",
        "manifest_status": "PASS" if manifest_passed else "FAIL",
        "manifest_errors": manifest_errors,
        "semantic_errors": semantic_errors,
        "cross_instance_language": cross_instance_language,
        "instances": len(results),
        "passed_instances": sum(result["status"] == "PASS" for result in results),
        "failed_instance_ids": [
            result["instance_id"] for result in results if result["status"] != "PASS"
        ],
    }
