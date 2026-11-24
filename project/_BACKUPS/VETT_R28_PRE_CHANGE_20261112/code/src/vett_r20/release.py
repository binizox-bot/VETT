from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from .auditor import audit_instance
from .generator import DATASET_VERSION, build_instance
from .repair import DUPLICATE_OF


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _file_record(base: Path, path: Path) -> dict[str, Any]:
    return {
        "path": path.relative_to(base).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": _sha256(path),
    }


def _aggregate_heuristics(audits: Iterable[dict[str, Any]]) -> dict[str, Any]:
    totals: dict[str, Counter[str]] = {}
    for audit in audits:
        for name, item in audit["heuristics"].items():
            totals.setdefault(name, Counter()).update(
                {"correct": item["correct"], "total": item["total"]}
            )
    return {
        name: {
            "correct": count["correct"],
            "total": count["total"],
            "accuracy": round(count["correct"] / count["total"], 6)
            if count["total"]
            else 0.0,
        }
        for name, count in sorted(totals.items())
    }


def _report(summary: dict[str, Any]) -> str:
    rows = "\n".join(
        f"| {name} | {item['correct']}/{item['total']} | {item['accuracy']:.2%} |"
        for name, item in summary["heuristic_baselines"].items()
    )
    return f"""# VETT-Cricket R20 220-Match Full-Table Release

## Release decision

**{summary['status']}** — {summary['passed_instances']}/{summary['instances']} instances passed all machine gates.

## Scale

- Match IDs: {summary['instances']}
- Independent roots: {summary['independent_roots']}
- Duplicate-consistency controls: {summary['duplicate_controls']}
- Direct scoreable cells: {summary['direct_targets']}
- Public documents: {summary['documents']}
- Public words: {summary['public_words']}
- Evidence claims, including superseded distractors: {summary['claims']}

## Difficulty controls

Every scoreable cell has a one-, two-, or three-step explicit revision chain. Claims are
distributed across opaque, shuffled documents; document order, genre and folio are
non-authoritative. The table schema is public, while answers and the evidence graph are
private.

| Public-only heuristic | Correct | Accuracy |
| --- | ---: | ---: |
{rows}

The strongest-model direct-fact target is approximately 75%, with row/table exact match
expected to be lower. This is a preregistered calibration target, **not a measured result**.
It must be measured on the frozen public release with blind model runs before a paper claim.
"""


def _dataset_card(summary: dict[str, Any]) -> str:
    return f"""# Dataset Card: {DATASET_VERSION}

R20 is a 220-match long-context text-to-full-table benchmark. It contains
{summary['direct_targets']} directly scored cells grounded in repaired canonical roots.
Source-conflicted cells remain preserved in the repair release but are not targets.

Use only each `public_instance.json` as model input. Never expose `private_gold.json`,
`private_evidence.json`, or `audit/` to a solver. Report 217 independent matches and the
three exact duplicates separately as consistency controls.

Primary metrics are micro cell exact match, macro match cell accuracy, row exact match,
table exact match, and match exact match. Report results by revision depth. The intended
strong-model direct-cell accuracy is about 75%; that value is pending blind calibration.
"""


def build_release(
    roots_path: Path,
    output_dir: Path,
    selected_ids: list[str] | None = None,
    *,
    seed: int = 20027,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    if any(path.is_file() for path in output_dir.rglob("*")):
        raise FileExistsError(f"release output directory is not empty: {output_dir}")
    roots = _read_jsonl(roots_path)
    by_id = {root["root_id"]: root for root in roots}
    selected = selected_ids or [f"match_{index:04d}" for index in range(1, 221)]
    if len(selected) != len(set(selected)):
        raise ValueError("selected match IDs must be unique")
    missing = sorted(set(selected) - set(by_id))
    if missing:
        raise ValueError(f"unknown selected IDs: {missing}")

    audits: list[dict[str, Any]] = []
    for match_id in selected:
        bundle = build_instance(by_id[match_id], seed=seed)
        audit = audit_instance(bundle.public, bundle.gold, bundle.evidence)
        _write_json(
            output_dir / "public" / match_id / "public_instance.json", bundle.public
        )
        _write_json(
            output_dir / "private" / match_id / "private_gold.json", bundle.gold
        )
        _write_json(
            output_dir / "private" / match_id / "private_evidence.json",
            bundle.evidence,
        )
        _write_json(output_dir / "audit" / f"{match_id}.audit.json", audit)
        audits.append(audit)

    heuristics = _aggregate_heuristics(audits)
    release_passed = all(audit["status"] == "PASS" for audit in audits) and all(
        item["accuracy"] <= 0.60 for item in heuristics.values()
    )
    summary = {
        "dataset_version": DATASET_VERSION,
        "status": "PASS" if release_passed else "FAIL",
        "seed": seed,
        "instances": len(selected),
        "passed_instances": sum(audit["status"] == "PASS" for audit in audits),
        "match_ids": selected,
        "independent_roots": sum(match_id not in DUPLICATE_OF for match_id in selected),
        "duplicate_controls": sum(match_id in DUPLICATE_OF for match_id in selected),
        "direct_targets": sum(audit["summary"]["targets"] for audit in audits),
        "claims": sum(audit["summary"]["claims"] for audit in audits),
        "documents": sum(audit["summary"]["documents"] for audit in audits),
        "public_words": sum(audit["summary"]["words"] for audit in audits),
        "minimum_words_per_instance": min(
            audit["summary"]["words"] for audit in audits
        ),
        "maximum_words_per_instance": max(
            audit["summary"]["words"] for audit in audits
        ),
        "heuristic_baselines": heuristics,
        "calibration_target": {
            "strong_model_direct_cell_accuracy": 0.75,
            "status": "UNMEASURED_PREREGISTERED_TARGET",
        },
    }
    _write_json(output_dir / "RELEASE_SUMMARY.json", summary)
    (output_dir / "RELEASE_REPORT.md").write_text(_report(summary), encoding="utf-8")
    (output_dir / "DATASET_CARD.md").write_text(
        _dataset_card(summary), encoding="utf-8"
    )
    files = [
        _file_record(output_dir, path)
        for path in sorted(output_dir.rglob("*"))
        if path.is_file() and path.name != "MANIFEST.json"
    ]
    _write_json(
        output_dir / "MANIFEST.json",
        {
            "dataset_version": DATASET_VERSION,
            "seed": seed,
            "file_count_excluding_manifest": len(files),
            "files": files,
        },
    )
    return summary


def audit_release(release_dir: Path) -> dict[str, Any]:
    errors: list[str] = []
    try:
        manifest = json.loads(
            (release_dir / "MANIFEST.json").read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError) as exc:
        return {"status": "FAIL", "errors": [f"manifest unreadable: {exc}"]}
    records = {item["path"]: item for item in manifest.get("files", [])}
    actual = {
        path.relative_to(release_dir).as_posix(): path
        for path in release_dir.rglob("*")
        if path.is_file() and path.name != "MANIFEST.json"
    }
    if set(records) != set(actual):
        errors.append("manifest file set mismatch")
    if manifest.get("file_count_excluding_manifest") != len(records):
        errors.append("manifest count mismatch")
    for relative in sorted(set(records) & set(actual)):
        if actual[relative].stat().st_size != records[relative].get("bytes"):
            errors.append(f"byte mismatch: {relative}")
        if _sha256(actual[relative]) != records[relative].get("sha256"):
            errors.append(f"hash mismatch: {relative}")

    summary_path = release_dir / "RELEASE_SUMMARY.json"
    try:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"summary unreadable: {exc}")
        summary = {}
    ids = summary.get("match_ids", [])
    passed = 0
    for match_id in ids:
        try:
            public = json.loads(
                (release_dir / "public" / match_id / "public_instance.json").read_text(
                    encoding="utf-8"
                )
            )
            gold = json.loads(
                (release_dir / "private" / match_id / "private_gold.json").read_text(
                    encoding="utf-8"
                )
            )
            evidence = json.loads(
                (
                    release_dir
                    / "private"
                    / match_id
                    / "private_evidence.json"
                ).read_text(encoding="utf-8")
            )
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{match_id}: artifact unreadable: {exc}")
            continue
        audit = audit_instance(public, gold, evidence)
        if audit["status"] == "PASS":
            passed += 1
        else:
            errors.append(f"{match_id}: instance audit failed: {audit['errors'][:3]}")
    if passed != summary.get("passed_instances"):
        errors.append("recomputed passed-instance count mismatch")
    if summary.get("instances") != len(ids):
        errors.append("summary instance count mismatch")
    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "instances": len(ids),
        "passed_instances": passed,
    }


__all__ = ["audit_release", "build_release"]
