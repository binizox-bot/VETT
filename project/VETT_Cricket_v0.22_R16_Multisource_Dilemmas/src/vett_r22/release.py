from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from .auditor import audit_instance
from .generator import build_instance
from .spec import DEFAULT_SEED, DUPLICATE_MAP, LEVELS, TARGET_FAMILIES, VERSION, expected_probe_count


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _roots(path: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            item = json.loads(line)
            result[item["root_id"]] = item
    return result


def _file_record(base: Path, path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "path": path.relative_to(base).as_posix(),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def _report(summary: dict[str, Any]) -> str:
    return f"""# VETT-Cricket R22 Five-Level Evidence Release

## Static release decision

**{summary['status']}** — {summary['passed_instances']}/{summary['instances']} instances passed all deterministic gates.

## Scale

- Full-table targets: {summary['table_targets']}
- Evidence probes: {summary['probes']}
- Decisive evidence spans: {summary['decisive_spans']}
- Decisive graph edges: {summary['decisive_edges']}
- Counterfactual deletion checks: {summary['counterfactual_checks']}
- Public words: {summary['public_words']}

Every included match has one probe in each cell of the 5-level by 5-target-family matrix.
R22 preserves the complete R21 Track A target set and requires every probe to dominate its
matched R21 target in decisive span count, edge count and graph depth.

## Split

- Development: {summary['split_counts']['development']}
- Blind independent: {summary['split_counts']['blind']}
- Duplicate controls: {summary['split_counts']['duplicate_control']}

## Calibration boundary

Static construction and audit are complete. Strong-model FAM is **UNMEASURED**. The
pre-registered release target is 58–65%, with a hard release-time ceiling of 65%, but no
empirical claim is made until the external model panel is run.
"""


def build_release(
    roots_path: Path,
    output_dir: Path,
    *,
    match_ids: list[str] | None = None,
    development_ids: list[str] | None = None,
    seed: int = DEFAULT_SEED,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    if any(output_dir.iterdir()):
        raise FileExistsError(f"R22 output directory is not empty: {output_dir}")
    roots = _roots(roots_path)
    selected = match_ids or sorted(roots)
    if len(selected) != len(set(selected)):
        raise ValueError("duplicate match ID in release selection")
    missing = sorted(set(selected) - set(roots))
    if missing:
        raise ValueError(f"unknown match IDs: {missing[:5]}")
    development = set(development_ids or [])
    if not development <= set(selected):
        raise ValueError("development split is not a subset of selected matches")
    duplicate_controls = set(DUPLICATE_MAP) & set(selected)
    split_records = []
    for match_id in selected:
        split = (
            "duplicate_control" if match_id in duplicate_controls
            else "development" if match_id in development
            else "blind"
        )
        split_records.append({"match_id": match_id, "split": split, "duplicate_of": DUPLICATE_MAP.get(match_id)})
    split = {
        "dataset_version": VERSION,
        "seed": seed,
        "records": split_records,
        "counts": dict(sorted(Counter(record["split"] for record in split_records).items())),
    }
    _write_json(output_dir / "SPLIT.json", split)

    audits: list[dict[str, Any]] = []
    level_counts: Counter[str] = Counter()
    family_counts: Counter[str] = Counter()
    matrix_counts: Counter[str] = Counter()
    for match_id in selected:
        bundle = build_instance(roots[match_id], seed=seed)
        audit = audit_instance(bundle.public, bundle.gold, bundle.evidence)
        if audit["status"] != "PASS":
            raise ValueError(f"{match_id}: R22 instance audit failed: {audit['errors'][:5]}")
        _write_json(output_dir / "public" / match_id / "public_instance.json", bundle.public)
        _write_json(output_dir / "private" / match_id / "private_gold.json", bundle.gold)
        _write_json(output_dir / "private" / match_id / "private_evidence.json", bundle.evidence)
        _write_json(output_dir / "audit" / f"{match_id}.audit.json", audit)
        audits.append(audit)
        for probe in bundle.gold["probes"]:
            level_counts[probe["level"]] += 1
            family_counts[probe["target_family"]] += 1
            matrix_counts[f"{probe['level']}|{probe['target_family']}"] += 1

    expected_matrix_cell = len(selected)
    matrix_ok = all(
        matrix_counts[f"{level}|{family}"] == expected_matrix_cell
        for level in LEVELS for family in TARGET_FAMILIES
    )
    summary = {
        "dataset_version": VERSION,
        "status": "PASS" if matrix_ok and all(audit["status"] == "PASS" for audit in audits) else "FAIL",
        "seed": seed,
        "instances": len(selected),
        "passed_instances": sum(audit["status"] == "PASS" for audit in audits),
        "independent_instances": len(selected) - len(duplicate_controls),
        "duplicate_controls": len(duplicate_controls),
        "match_ids": selected,
        "split_counts": {
            name: sum(record["split"] == name for record in split_records)
            for name in ("development", "blind", "duplicate_control")
        },
        "table_targets": sum(audit["summary"]["table_targets"] for audit in audits),
        "probes": sum(audit["summary"]["probes"] for audit in audits),
        "expected_probes": expected_probe_count(len(selected)),
        "probe_claims": sum(audit["summary"]["probe_claims"] for audit in audits),
        "decisive_spans": sum(audit["summary"]["decisive_spans"] for audit in audits),
        "decisive_edges": sum(audit["summary"]["decisive_edges"] for audit in audits),
        "counterfactual_checks": sum(audit["summary"]["counterfactual_checks"] for audit in audits),
        "documents": sum(audit["summary"]["documents"] for audit in audits),
        "public_words": sum(audit["summary"]["public_words"] for audit in audits),
        "baseline_words": sum(audit["summary"]["baseline_words"] for audit in audits),
        "minimum_public_words": min(audit["summary"]["public_words"] for audit in audits),
        "maximum_public_words": max(audit["summary"]["public_words"] for audit in audits),
        "by_level": dict(sorted(level_counts.items())),
        "by_family": dict(sorted(family_counts.items())),
        "matrix_counts": dict(sorted(matrix_counts.items())),
        "difficulty_no_regression": "PASS",
        "empirical_calibration": {
            "status": "UNMEASURED",
            "strong_model_fam_preferred_range": [0.58, 0.65],
            "strong_model_fam_ceiling": 0.65,
            "minimum_adjacent_level_gap": 0.08,
        },
    }
    if summary["probes"] != summary["expected_probes"]:
        summary["status"] = "FAIL"
    _write_json(output_dir / "RELEASE_SUMMARY.json", summary)
    (output_dir / "RELEASE_REPORT.md").write_text(_report(summary), encoding="utf-8")
    (output_dir / "DATASET_CARD.md").write_text(
        "# Dataset Card: R22 Five-Level Evidence Benchmark\n\n"
        "Use only `public/` as model input. Track A preserves full-table reconstruction; "
        "Track B contains a balanced 5x5 evidence-probe matrix per match. `private/` and "
        "`audit/` must remain outside the solver context. Static PASS proves deterministic "
        "resolvability, counterfactual necessity and no regression from R21; it does not "
        "prove the unmeasured strong-model <=65% target.\n",
        encoding="utf-8",
    )
    files = [
        _file_record(output_dir, path)
        for path in sorted(output_dir.rglob("*"))
        if path.is_file() and path.name != "MANIFEST.json"
    ]
    _write_json(output_dir / "MANIFEST.json", {
        "dataset_version": VERSION,
        "seed": seed,
        "file_count_excluding_manifest": len(files),
        "files": files,
    })
    return summary


def audit_release(release_dir: Path) -> dict[str, Any]:
    errors: list[str] = []
    try:
        manifest = json.loads((release_dir / "MANIFEST.json").read_text(encoding="utf-8"))
        summary = json.loads((release_dir / "RELEASE_SUMMARY.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"status": "FAIL", "errors": [f"release metadata unreadable: {exc}"]}
    expected_files = {record["path"]: record for record in manifest.get("files", [])}
    actual_files = {
        path.relative_to(release_dir).as_posix(): path
        for path in release_dir.rglob("*")
        if path.is_file() and path.name != "MANIFEST.json"
    }
    if set(expected_files) != set(actual_files):
        errors.append("manifest file set mismatch")
    for name in sorted(set(expected_files) & set(actual_files)):
        actual = _file_record(release_dir, actual_files[name])
        if actual["bytes"] != expected_files[name].get("bytes") or actual["sha256"] != expected_files[name].get("sha256"):
            errors.append(f"manifest mismatch: {name}")
    passed = 0
    probes = 0
    for match_id in summary.get("match_ids", []):
        try:
            public = json.loads((release_dir / "public" / match_id / "public_instance.json").read_text(encoding="utf-8"))
            gold = json.loads((release_dir / "private" / match_id / "private_gold.json").read_text(encoding="utf-8"))
            evidence = json.loads((release_dir / "private" / match_id / "private_evidence.json").read_text(encoding="utf-8"))
            audit = audit_instance(public, gold, evidence)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{match_id}: unreadable instance: {exc}")
            continue
        probes += audit["summary"]["probes"]
        if audit["status"] == "PASS":
            passed += 1
        else:
            errors.append(f"{match_id}: {audit['errors'][:5]}")
    if passed != summary.get("passed_instances"):
        errors.append("passed instance count mismatch")
    if probes != summary.get("probes") or probes != expected_probe_count(summary.get("instances", 0)):
        errors.append("release probe count mismatch")
    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "instances": summary.get("instances", 0),
        "passed_instances": passed,
        "probes": probes,
    }


__all__ = ["audit_release", "build_release"]
