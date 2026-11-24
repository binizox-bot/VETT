from __future__ import annotations

import hashlib
import json
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
    return f"""# VETT-Cricket R16 Pilot Release Report

## Release decision

**{summary['status']}** — {summary['passed_instances']}/{summary['instances']} instances passed every machine gate.

## Scope

- Version: `{summary['dataset_version']}`
- Seed: `{summary['seed']}`
- Roots: {', '.join(summary['match_ids'])}
- Documents: {summary['documents']}
- Claims: {summary['claims']}
- Scored targets: {summary['targets']} ({summary['direct_targets']} direct/versioned, {summary['derived_targets']} derived)
- Counterfactual decisive-support deletions: {summary['counterfactuals']}

## Weak baselines

| Baseline | Correct | Accuracy |
| --- | ---: | ---: |
{baseline_rows}

The authority-aware reference resolver achieved {summary['targets']}/{summary['targets']}. Weak baselines are structural diagnostics only; they are not evidence that a language model fails.

## Difficulty included in every instance

- stale preliminary values and later narrow-scope corrections;
- duplicated syndication copies and late unrefreshed reports;
- identical field types colliding across two innings;
- partial corrections that leave neighboring fields unchanged;
- an invalidated apparent wicket after a no-ball review;
- internally reconciled alternate score worlds whose extras and totals remain plausible;
- correct values positioned away from first, last, and majority mentions;
- bowling-charge derivations from total runs, byes, and leg-byes.

## Audit boundary

- No human naturalness audit was performed.
- A mechanical anti-template proxy rejects repeated openings, short fragments, known grammar artifacts, and excessive duplicate spans.
- No external blind language-model run was performed.
- All documents are disclosed as controlled semi-synthetic material derived from canonical scorecards, not observed ball-by-ball logs.
- The pilot is suitable for deciding the next difficulty direction, not yet for a public benchmark claim.
"""


def _dataset_card(summary: dict[str, Any]) -> str:
    return f"""# Dataset Card: {summary['dataset_version']}

This pilot evaluates scoped, versioned cricket state reconstruction from mixed-source documents. Public inputs contain source class, chronology, span IDs, authority rules, documents, and blank targets. Private artifacts contain gold values, claim semantics, evidence edges, derivations, and audits.

The six roots were selected from canonical entries marked `READY_FOR_GENERATED_VIEWS` and cover a close T20 chase, an ODI run-margin win, a five-wicket chase, a shortened women's match, a large-margin match, and a low-score chase.

Use `public/` as model input. Keep `private/` and `audit/` outside the solving context. Results are invalid if the complete release directory is exposed to the model.

Machine release status: **{summary['status']}**. Human naturalness and blind model performance remain unverified.
"""


def build_release(
    roots_path: Path,
    output_dir: Path,
    selected_ids: list[str] | None = None,
    *,
    seed: int = 16022,
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

    for match_id in selected:
        bundle = build_instance(roots_by_id[match_id], seed=seed)
        audit = audit_instance(bundle.public, bundle.gold, bundle.evidence)
        _write_json(output_dir / "public" / match_id / "public_instance.json", bundle.public)
        _write_json(output_dir / "private" / match_id / "private_gold.json", bundle.gold)
        _write_json(output_dir / "private" / match_id / "private_evidence.json", bundle.evidence)
        _write_json(output_dir / "audit" / f"{match_id}.audit.json", audit)
        audits.append(audit)

    baseline_names = ("first_mention", "last_mention", "majority_vote", "source_only")
    aggregate_baselines: dict[str, dict[str, Any]] = {}
    for name in baseline_names:
        correct = sum(audit["baselines"][name]["correct"] for audit in audits)
        total = sum(audit["baselines"][name]["total"] for audit in audits)
        aggregate_baselines[name] = {
            "correct": correct,
            "total": total,
            "accuracy": round(correct / total, 6) if total else 0.0,
        }

    summary = {
        "dataset_version": "VETT-Cricket-v0.22-R16-pilot",
        "status": "PASS" if all(audit["status"] == "PASS" for audit in audits) else "FAIL",
        "seed": seed,
        "instances": len(audits),
        "passed_instances": sum(audit["status"] == "PASS" for audit in audits),
        "match_ids": selected,
        "documents": sum(audit["summary"]["documents"] for audit in audits),
        "claims": sum(audit["summary"]["claims"] for audit in audits),
        "direct_targets": sum(audit["summary"]["direct_targets"] for audit in audits),
        "derived_targets": sum(audit["summary"]["derived_targets"] for audit in audits),
        "targets": sum(
            audit["summary"]["direct_targets"] + audit["summary"]["derived_targets"]
            for audit in audits
        ),
        "counterfactuals": sum(len(audit["counterfactuals"]) for audit in audits),
        "baselines": aggregate_baselines,
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
    manifest = {
        "dataset_version": summary["dataset_version"],
        "seed": seed,
        "file_count_excluding_manifest": len(manifest_files),
        "files": manifest_files,
    }
    _write_json(output_dir / "MANIFEST.json", manifest)
    return summary


def audit_release(release_dir: Path) -> dict[str, Any]:
    manifest_errors: list[str] = []
    manifest_path = release_dir / "MANIFEST.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_records = manifest.get("files", [])
    except (OSError, json.JSONDecodeError, AttributeError) as exc:
        manifest = {}
        manifest_records = []
        manifest_errors.append(f"manifest unreadable: {exc}")

    manifest_by_path: dict[str, dict[str, Any]] = {}
    for record in manifest_records:
        path = record.get("path") if isinstance(record, dict) else None
        if not isinstance(path, str):
            manifest_errors.append("manifest contains a record without a path")
            continue
        if path in manifest_by_path:
            manifest_errors.append(f"duplicate manifest path: {path}")
        manifest_by_path[path] = record
    if manifest.get("file_count_excluding_manifest") != len(manifest_records):
        manifest_errors.append("manifest file count does not match its records")

    actual_files = {
        path.relative_to(release_dir).as_posix(): path
        for path in sorted(release_dir.rglob("*"))
        if path.is_file() and path.name != "MANIFEST.json"
    }
    for missing in sorted(set(manifest_by_path) - set(actual_files)):
        manifest_errors.append(f"missing file: {missing}")
    for extra in sorted(set(actual_files) - set(manifest_by_path)):
        manifest_errors.append(f"unlisted file: {extra}")
    for relative_path in sorted(set(manifest_by_path) & set(actual_files)):
        expected = manifest_by_path[relative_path]
        actual = _file_record(release_dir, actual_files[relative_path])
        if expected.get("bytes") != actual["bytes"]:
            manifest_errors.append(f"byte-count mismatch: {relative_path}")
        if expected.get("sha256") != actual["sha256"]:
            manifest_errors.append(f"sha256 mismatch: {relative_path}")

    results: list[dict[str, Any]] = []
    semantic_errors: list[str] = []
    for public_path in sorted((release_dir / "public").glob("*/public_instance.json")):
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
            results.append(audit_instance(public, gold, evidence))
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            semantic_errors.append(f"{match_id}: {exc}")

    manifest_passed = not manifest_errors
    semantic_passed = (
        bool(results)
        and not semantic_errors
        and all(item["status"] == "PASS" for item in results)
    )
    return {
        "status": "PASS" if manifest_passed and semantic_passed else "FAIL",
        "manifest_status": "PASS" if manifest_passed else "FAIL",
        "manifest_errors": manifest_errors,
        "semantic_errors": semantic_errors,
        "instances": len(results),
        "passed_instances": sum(item["status"] == "PASS" for item in results),
        "failed_instance_ids": [
            item["instance_id"] for item in results if item["status"] != "PASS"
        ],
    }
