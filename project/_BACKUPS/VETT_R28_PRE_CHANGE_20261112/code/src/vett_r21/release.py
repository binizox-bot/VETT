from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from .auditor import audit_instance
from .generator import VERSION, build_instance


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _read_roots(path: Path) -> dict[str, dict[str, Any]]:
    return {
        root["root_id"]: root
        for root in (json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    }


def _file_record(base: Path, path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {"path": path.relative_to(base).as_posix(), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def _aggregate_heuristics(audits: list[dict[str, Any]]) -> dict[str, Any]:
    totals: dict[str, Counter[str]] = {}
    for audit in audits:
        for name, metric in audit["heuristics"].items():
            totals.setdefault(name, Counter()).update({"correct": metric["correct"], "total": metric["total"]})
    return {
        name: {"correct": values["correct"], "total": values["total"], "accuracy": round(values["correct"] / values["total"], 6)}
        for name, values in sorted(totals.items())
    }


def _report(summary: dict[str, Any]) -> str:
    heuristics = "\n".join(
        f"| {name} | {value['correct']}/{value['total']} | {value['accuracy']:.2%} |"
        for name, value in summary["heuristic_baselines"].items()
    )
    return f"""# VETT-Cricket R21 Evidence-Chain Pilot

## Release decision

**{summary['status']}** — {summary['passed_instances']}/{summary['instances']} selected independent matches passed all machine gates.

## Scale

- Direct value targets: {summary['targets']}
- Typed evidence claims: {summary['claims']}
- Required evidence spans: {summary['required_evidence_spans']}
- Required graph edges: {summary['required_edges']}
- Public documents: {summary['documents']}
- Public words: {summary['public_words']}

## Mechanisms

The pilot mixes one-step and two-step supersession, copied-majority traps, explicit
retraction with independent replacement, and coordinate-scoped amendment. Public evidence
uses semantic row/table/column descriptions rather than literal target or table IDs.

| Public-only heuristic | Correct | Accuracy |
| --- | ---: | ---: |
{heuristics}

No external model result is included. The intended calibration target remains about 75%
for strong-model answer accuracy, with evidence and joint accuracy lower; this must be
measured by blind runs through the unified runner.
"""


def build_release(
    roots_path: Path,
    selection_path: Path,
    output_dir: Path,
    *,
    seed: int = 21031,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    existing = [path for path in output_dir.rglob("*") if path.is_file() and path.name != "SELECTION.json"]
    if existing:
        raise FileExistsError(f"R21 output is not empty: {output_dir}")
    roots = _read_roots(roots_path)
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    _write_json(output_dir / "SELECTION.json", selection)
    selected = selection["match_ids"]
    audits: list[dict[str, Any]] = []
    for match_id in selected:
        bundle = build_instance(roots[match_id], seed=seed)
        audit = audit_instance(bundle.public, bundle.gold, bundle.evidence)
        _write_json(output_dir / "public" / match_id / "public_instance.json", bundle.public)
        _write_json(output_dir / "private" / match_id / "private_gold.json", bundle.gold)
        _write_json(output_dir / "private" / match_id / "private_evidence.json", bundle.evidence)
        _write_json(output_dir / "audit" / f"{match_id}.audit.json", audit)
        audits.append(audit)
    mechanisms = Counter()
    for audit in audits:
        mechanisms.update(audit["summary"]["mechanisms"])
    heuristics = _aggregate_heuristics(audits)
    passed = all(audit["status"] == "PASS" for audit in audits) and all(value["accuracy"] <= 0.60 for value in heuristics.values())
    summary = {
        "dataset_version": VERSION,
        "status": "PASS" if passed else "FAIL",
        "seed": seed,
        "instances": len(selected),
        "passed_instances": sum(audit["status"] == "PASS" for audit in audits),
        "match_ids": selected,
        "targets": sum(audit["summary"]["targets"] for audit in audits),
        "claims": sum(audit["summary"]["claims"] for audit in audits),
        "required_evidence_spans": sum(audit["summary"]["required_evidence_spans"] for audit in audits),
        "required_edges": sum(audit["summary"]["required_edges"] for audit in audits),
        "documents": sum(audit["summary"]["documents"] for audit in audits),
        "public_words": sum(audit["summary"]["words"] for audit in audits),
        "minimum_words_per_instance": min(audit["summary"]["words"] for audit in audits),
        "maximum_words_per_instance": max(audit["summary"]["words"] for audit in audits),
        "mechanisms": dict(sorted(mechanisms.items())),
        "heuristic_baselines": heuristics,
        "calibration_target": {"answer_cell_accuracy": 0.75, "status": "UNMEASURED"},
    }
    _write_json(output_dir / "RELEASE_SUMMARY.json", summary)
    (output_dir / "RELEASE_REPORT.md").write_text(_report(summary), encoding="utf-8")
    (output_dir / "DATASET_CARD.md").write_text(
        "# Dataset Card: R21 Evidence-Chain Pilot\n\n"
        "Use only `public/` as model input. Each prediction must contain an exact value, "
        "evidence span IDs and typed evidence edges. Keep `private/` and `audit/` outside "
        "the solver context. All 20 matches are independent roots selected by the frozen "
        "`SELECTION.json`. External model calibration and human naturalness review remain pending.\n",
        encoding="utf-8",
    )
    files = [_file_record(output_dir, path) for path in sorted(output_dir.rglob("*")) if path.is_file() and path.name != "MANIFEST.json"]
    _write_json(output_dir / "MANIFEST.json", {"dataset_version": VERSION, "seed": seed, "file_count_excluding_manifest": len(files), "files": files})
    return summary


def audit_release(release_dir: Path) -> dict[str, Any]:
    errors: list[str] = []
    try:
        manifest = json.loads((release_dir / "MANIFEST.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"status": "FAIL", "errors": [f"manifest unreadable: {exc}"]}
    expected = {record["path"]: record for record in manifest.get("files", [])}
    actual = {path.relative_to(release_dir).as_posix(): path for path in release_dir.rglob("*") if path.is_file() and path.name != "MANIFEST.json"}
    if set(expected) != set(actual):
        errors.append("manifest file set mismatch")
    for relative in sorted(set(expected) & set(actual)):
        record = _file_record(release_dir, actual[relative])
        if record["bytes"] != expected[relative].get("bytes") or record["sha256"] != expected[relative].get("sha256"):
            errors.append(f"manifest mismatch: {relative}")
    summary = json.loads((release_dir / "RELEASE_SUMMARY.json").read_text(encoding="utf-8"))
    passed = 0
    for match_id in summary.get("match_ids", []):
        public = json.loads((release_dir / "public" / match_id / "public_instance.json").read_text(encoding="utf-8"))
        gold = json.loads((release_dir / "private" / match_id / "private_gold.json").read_text(encoding="utf-8"))
        evidence = json.loads((release_dir / "private" / match_id / "private_evidence.json").read_text(encoding="utf-8"))
        audit = audit_instance(public, gold, evidence)
        if audit["status"] == "PASS":
            passed += 1
        else:
            errors.append(f"{match_id}: {audit['errors'][:3]}")
    if passed != summary.get("passed_instances"):
        errors.append("passed instance count mismatch")
    return {"status": "PASS" if not errors else "FAIL", "errors": errors, "instances": summary.get("instances", 0), "passed_instances": passed}


__all__ = ["audit_release", "build_release"]
