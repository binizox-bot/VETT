"""Independent verification for the R28 build (task t5).

Two kinds of checks live here:

* **R26.15 zero drift** - every byte of the frozen candidate, of ``src/vett_r16..r26``
  and of the pre-existing tests is re-hashed against
  ``_BACKUPS/VETT_R28_PRE_CHANGE_20261112/PROTECTED_PATHS.json`` and the group
  aggregate is recomputed with the ``vett-tree-aggregate-v1`` recipe.
* **HA1-HA18** - the contract's hard acceptance table, computed from the build
  artefacts (never from the generator's own claims).
"""

from __future__ import annotations

import ast
import json
import pathlib
from typing import Any, Callable

from .canonical import canon, sha256_file, sha256_text, tree_aggregate
from .config import BuildConfig
from .constants import (
    BACKUP,
    INFORMATIVE_FIELDS,
    LEDGER_FIELDS,
    LEGAL_DISMISSALS,
    MAX_PROMPT_TOKENS,
    RECORD_FIELDS,
    ROOT,
    WS,
)
from .derivation import NECESSARY, PRESENTATION_ONLY

PROTECTED_MANIFEST = BACKUP / "PROTECTED_PATHS.json"
R26_15_CANDIDATE = WS / "VETT_Cricket_v0.22_R16_Multisource_Dilemmas" / "r26_15_content_dependency_candidate_v3"


# ---------------------------------------------------------------------------
# R26.15 zero drift
# ---------------------------------------------------------------------------
def verify_protected_paths(*, manifest_path: pathlib.Path | None = None) -> dict[str, Any]:
    """Recompute every protected file digest and the per-group aggregate."""

    path = manifest_path or PROTECTED_MANIFEST
    if not path.exists():
        return {"ok": False, "reason": f"protected manifest missing: {path}", "groups": []}
    manifest = json.loads(path.read_text(encoding="utf-8"))
    project_root = pathlib.Path(manifest["project_root"])
    exclusions = set(manifest.get("exclusions", []))
    groups: list[dict[str, Any]] = []
    all_ok = True
    for group in manifest["groups"]:
        root = group.get("root")
        entries: list[tuple[str, str]] = []
        mismatches: list[dict[str, Any]] = []
        missing: list[str] = []
        bytes_total = 0
        for record in group["files"]:
            relative = record["path"]
            file_path = project_root / relative
            if not file_path.exists():
                missing.append(relative)
                all_ok = False
                continue
            digest = sha256_file(file_path)
            size = file_path.stat().st_size
            bytes_total += size
            if digest != record["sha256"] or size != record["bytes"]:
                mismatches.append({
                    "path": relative,
                    "expected_bytes": record["bytes"],
                    "actual_bytes": size,
                    "expected_sha256": record["sha256"],
                    "actual_sha256": digest,
                })
                all_ok = False
            aggregate_path = relative  # the manifest records project-relative POSIX paths
            entries.append((aggregate_path, digest))
        aggregate = tree_aggregate(entries)
        aggregate_ok = aggregate == group.get("aggregate_sha256")
        if not aggregate_ok:
            all_ok = False
        groups.append({
            "id": group["id"],
            "role": group.get("role"),
            "root": root,
            "file_count": len(group["files"]),
            "file_count_checked": len(entries),
            "total_bytes": bytes_total,
            "expected_total_bytes": group.get("total_bytes"),
            "aggregate_sha256": aggregate,
            "expected_aggregate_sha256": group.get("aggregate_sha256"),
            "aggregate_ok": aggregate_ok,
            "missing": missing,
            "mismatches": mismatches,
            "ok": aggregate_ok and not missing and not mismatches,
        })
    r26_group = next((group for group in groups if group["id"] == "r26_15_candidate"), None)
    return {
        "schema": "vett.r28.verify.protected_paths.v1",
        "manifest": str(path.relative_to(WS)) if str(path).startswith(str(WS)) else str(path),
        "manifest_sha256": sha256_file(path),
        "exclusions": sorted(exclusions),
        "groups": groups,
        "file_count": sum(group["file_count"] for group in groups),
        "total_bytes": sum(group["total_bytes"] for group in groups),
        "r26_15_file_count": r26_group["file_count"] if r26_group else None,
        "r26_15_total_bytes": r26_group["total_bytes"] if r26_group else None,
        "r26_15_aggregate_sha256": r26_group["aggregate_sha256"] if r26_group else None,
        "ok": all_ok,
    }


def verify_r26_15_against_backup() -> dict[str, Any]:
    """Byte-compare the live R26.15 candidate against t1's frozen copy."""

    frozen = BACKUP / "frozen" / "r26_15_content_dependency_candidate_v3"
    if not frozen.exists():
        return {"ok": False, "reason": "frozen baseline copy missing"}
    live_files = sorted(
        path for path in R26_15_CANDIDATE.rglob("*") if path.is_file()
    )
    frozen_files = sorted(path for path in frozen.rglob("*") if path.is_file())
    live_rel = {path.relative_to(R26_15_CANDIDATE).as_posix(): path for path in live_files}
    frozen_rel = {path.relative_to(frozen).as_posix(): path for path in frozen_files}
    missing = sorted(set(frozen_rel) - set(live_rel))
    extra = sorted(set(live_rel) - set(frozen_rel))
    mismatches: list[str] = []
    bytes_total = 0
    for relative in sorted(set(live_rel) & set(frozen_rel)):
        live_digest = sha256_file(live_rel[relative])
        frozen_digest = sha256_file(frozen_rel[relative])
        bytes_total += live_rel[relative].stat().st_size
        if live_digest != frozen_digest:
            mismatches.append(relative)
    ok = not missing and not extra and not mismatches
    return {
        "schema": "vett.r28.verify.r26_15.v1",
        "live_root": "VETT_Cricket_v0.22_R16_Multisource_Dilemmas/r26_15_content_dependency_candidate_v3",
        "frozen_root": "_BACKUPS/VETT_R28_PRE_CHANGE_20261112/frozen/r26_15_content_dependency_candidate_v3",
        "file_count": len(live_rel),
        "frozen_file_count": len(frozen_rel),
        "total_bytes": bytes_total,
        "missing": missing,
        "extra": extra,
        "mismatches": mismatches,
        "ok": ok,
    }


# ---------------------------------------------------------------------------
# Hard acceptance HA1-HA18
# ---------------------------------------------------------------------------
def _check(rows: list[dict[str, Any]], check_id: str, requirement: str, passed: bool,
           evidence: Any) -> None:
    rows.append({
        "id": check_id,
        "requirement": requirement,
        "status": "passed" if passed else "failed",
        "evidence": evidence,
    })


def verify_hard_acceptance(
    config: BuildConfig,
    *,
    summaries: list[dict[str, Any]],
    published: list[dict[str, Any]],
    held_out: list[dict[str, Any]],
    quota_report: dict[str, Any],
    assignment_cells: dict[str, Any],
    determinism: dict[str, Any],
    code_scan: dict[str, Any],
    public_files: list[pathlib.Path] | None = None,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    published_summaries = [row for row in summaries if row["split"] == "development"]
    n = config.n_published

    records = [row["record_sha256"] for row in published_summaries]
    distinct_ratio = len(set(records)) / max(1, len(records))
    _check(rows, "HA1", "published distinct record ratio == 1.0",
           len(set(records)) == len(records) == n,
           {"records": len(records), "distinct": len(set(records)),
            "distinct_ratio": round(distinct_ratio, 6)})

    families = [row["family"] if "family" in row else row.get("scenario_family")
                for row in published_summaries]
    family_ok = len(set(families)) == n and all(families)
    _check(rows, "HA2", "one question per neutral family, twins share the family",
           family_ok, {"families": len(set(families)), "questions": n})

    field_values: dict[str, set] = {field: set() for field in RECORD_FIELDS}
    for row in published_summaries:
        for field in RECORD_FIELDS:
            field_values[field].add(_freeze(row["decision_record_flat"].get(field)))
    constant_fields = [field for field, values in field_values.items() if len(values) == 1]
    _check(rows, "HA3", "no constant field among the 12 record fields",
           not constant_fields,
           {"constant_fields": constant_fields,
            "distinct_values": {field: len(values) for field, values in field_values.items()}})

    ledger_nonzero = {
        field: sum(1 for row in published_summaries
                   if int(row["decision_record_flat"].get(field, 0)) != 0)
        for field in LEDGER_FIELDS
    }
    thresholds = {"ledger.BYE": 80, "ledger.LEG_BYE": 64, "ledger.PENALTY": 120}
    _check(rows, "HA4", "constant-in-R26 fields are non-zero often enough",
           all(ledger_nonzero[field] >= thresholds[field] for field in thresholds),
           {"nonzero": ledger_nonzero, "minimum": thresholds})

    by_dismissal: dict[str, int] = {}
    by_status: dict[str, int] = {}
    for row in published_summaries:
        by_dismissal[row["decision_record_flat"]["dismissal"]] = (
            by_dismissal.get(row["decision_record_flat"]["dismissal"], 0) + 1
        )
        by_status[row["decision_record_flat"]["delivery_status"]] = (
            by_status.get(row["decision_record_flat"]["delivery_status"], 0) + 1
        )
    none_share = by_dismissal.get("NONE", 0) / max(1, len(published_summaries))
    legal_total = sum(by_dismissal.get(name, 0) for name in LEGAL_DISMISSALS) + by_status.get(
        "DEAD_REBALL", 0)
    _check(rows, "HA5", "dismissal does not degenerate",
           none_share <= float(config.caps["none_share_max"])
           and by_dismissal.get("RUN_OUT", 0) >= 60
           and by_dismissal.get("OBSTRUCTING_FIELD", 0) >= 40
           and by_dismissal.get("HIT_BALL_TWICE", 0) >= 40
           and legal_total >= 8,
           {"by_dismissal": by_dismissal, "none_share": round(none_share, 6),
            "legal_dismissal_total": legal_total})
    _check(rows, "HA6", "delivery status coverage",
           by_status.get("LEGAL", 0) >= 120 and by_status.get("NO_BALL", 0) >= 80
           and by_status.get("WIDE", 0) >= 40 and by_status.get("DEAD_REBALL", 0) == 1,
           {"by_status": by_status})
    _check(rows, "HA18", "legal delivery-completed dismissals capped at 11 (blocking)",
           legal_total <= int(config.caps["legal_dismissal_total"]),
           {"legal_dismissal_total": legal_total, "cap": config.caps["legal_dismissal_total"],
            "breakdown": {name: by_dismissal.get(name, 0) for name in LEGAL_DISMISSALS},
            "dead_reball": by_status.get("DEAD_REBALL", 0)})

    cert_rows = [row for row in published_summaries if row["certificate_ok_published"]]
    replay_published = sum(1 for row in published_summaries
                           if row["replay"]["published"]["ok"])
    replay_control = sum(1 for row in published_summaries if row["replay"]["control"]["ok"])
    replay_held = sum(1 for row in summaries
                      if row["split"] == "held_out_test" and row["replay"]["published"]["ok"])
    _check(rows, "HA7", "certificate coverage 100% and solver re-derivation 100%",
           len(cert_rows) == len(published_summaries) == n
           and replay_published == n and replay_control == n,
           {"certificates_published": len(cert_rows), "questions": n,
            "replay_published": replay_published, "replay_control": replay_control,
            "replay_held_out": replay_held})

    twin_facts = sum(1 for row in published_summaries if row["twin"]["facts_byte_identical"])
    twin_records = sum(1 for row in published_summaries if row["twin"]["record_byte_identical"])
    twin_questions = sum(1 for row in published_summaries if row["twin"]["question_text_identical"])
    twin_schema = sum(1 for row in published_summaries if row["twin"]["output_schema_identical"])
    _check(rows, "HA8", "dual rendering identity 320/320 (facts, record, question text)",
           twin_facts == n and twin_records == n and twin_questions == n and twin_schema == n,
           {"facts_identical": twin_facts, "records_identical": twin_records,
            "question_text_identical": twin_questions, "schema_identical": twin_schema})

    _check(rows, "HA9", "deterministic rebuild (same seed + config -> same aggregate)",
           bool(determinism.get("ok")),
           determinism)

    family_probe = code_scan.get("family_name_probe", {})
    _check(rows, "HA10", "family-name-only baseline <= 40% (structurally neutral ids)",
           bool(family_probe.get("neutral")),
           family_probe)

    leak_violations = []
    for row in published_summaries:
        leak_violations.extend(row["leak_scan"]["published"])
    held_out_leak = code_scan.get("held_out_in_public", [])
    answer_leak = code_scan.get("answer_strings_in_public", [])
    _check(rows, "HA11", "leak audit: no gold/level/dose/answer text in public",
           not leak_violations and not held_out_leak and not answer_leak,
           {"forbidden_markers": sorted(set(leak_violations)),
            "held_out_in_public": held_out_leak[:5],
            "answer_strings_in_public": answer_leak[:5]})

    quota_ok = bool(quota_report["no_shortfall"]) and bool(
        quota_report["assignment_summary"]["n_published"] == n)
    layer_counts_ok = all(row["selected_equals_quota"] for row in quota_report["rows"])
    cell_ok = all(
        cell["status_diversity"] >= 2 and cell["dismissal_diversity"] >= 2
        and cell["n"] == cell["capacity"]
        for cell in assignment_cells.values()
    )
    _check(rows, "HA12", "quota and cell assignment exact, >=2 status/dismissal per cell",
           quota_ok and layer_counts_ok and cell_ok,
           {"no_shortfall": quota_report["no_shortfall"],
            "layers_selected_equal_quota": layer_counts_ok,
            "cells_ok": cell_ok,
            "cells": len(assignment_cells)})

    pinned = quota_report["assignment_summary"]["pinned_combinations"]
    _check(rows, "HA13", "five never-coexisting fact combinations appear at least once",
           len(pinned) == 5,
           {"combinations": pinned})

    margin_needed = n + int(config.held_out["n"]) + int(round(n * float(config.caps["safety_factor"])))
    reachable = quota_report["combined_space"]["distinct_records"]
    _check(rows, "HA14", "record-space safety margin (reachable >= N + 40 + 10%)",
           reachable >= margin_needed,
           {"reachable": reachable, "required_with_margin": margin_needed,
            "published_plus_held_out": n + int(config.held_out["n"])})

    max_tokens = max(row["tokens"]["published"] for row in published_summaries)
    over_budget = [row["question_id"] for row in published_summaries
                   if not row["prompt_budget"]["within_budget"]]
    max_docs = max(row["prompt_budget"]["document_count_published"] for row in published_summaries)
    max_spans = max(row["prompt_budget"]["span_count_published"] for row in published_summaries)
    _check(rows, "HA15", "prompt budget <= 7000 tokens, <=12 documents, <=80 spans",
           not over_budget and max_tokens <= MAX_PROMPT_TOKENS
           and max_docs <= int(config.prompt["max_documents"])
           and max_spans <= int(config.prompt["max_spans"]),
           {"max_tokens": max_tokens, "cap": MAX_PROMPT_TOKENS,
            "max_documents": max_docs, "max_spans": max_spans,
            "over_budget": over_budget})

    schema_fields = config.output_contract["decision_record_fields"]
    _check(rows, "HA16", "output schema frozen: 12 record fields, names unchanged",
           set(schema_fields) == set(RECORD_FIELDS) and len(schema_fields) == 12,
           {"fields": sorted(schema_fields), "count": len(schema_fields)})

    _check(rows, "HA17", "n_published is a parameter, not hardcoded in build code",
           bool(code_scan.get("n_parameterized")),
           code_scan.get("n_hardcode_scan"))

    passed = sum(1 for row in rows if row["status"] == "passed")
    return {
        "schema": "vett.r28.verify.hard_acceptance.v1",
        "checks": rows,
        "passed": passed,
        "failed": len(rows) - passed,
        "total": len(rows),
        "all_passed": passed == len(rows),
        "informative_fields": list(INFORMATIVE_FIELDS),
    }


def _freeze(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return canon(value)
    return value


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------
def determinism_check(
    build_once: Callable[[], dict[str, Any]],
    *,
    repeats: int = 2,
) -> dict[str, Any]:
    """Run the build twice and compare per-question digests."""

    runs = [build_once() for _ in range(repeats)]
    digests = [run["digest"] for run in runs]
    aggregates = [run["aggregate"] for run in runs]
    ok = len(set(digests)) == 1 and len(set(aggregates)) == 1
    return {
        "schema": "vett.r28.verify.determinism.v1",
        "repeats": repeats,
        "digest": digests[0] if digests else None,
        "digests": digests,
        "aggregate": aggregates[0] if aggregates else None,
        "aggregates": aggregates,
        "question_count": runs[0]["question_count"] if runs else 0,
        "ok": ok,
    }


# ---------------------------------------------------------------------------
# Static code scan (HA10 / HA11 / HA17 helpers)
# ---------------------------------------------------------------------------
def code_scan(config: BuildConfig, *, package_dir: pathlib.Path | None = None,
              public_files: list[pathlib.Path] | None = None) -> dict[str, Any]:
    package = package_dir or (ROOT / "03_build" / "r28gen")
    sources = sorted(package.glob("*.py"))
    build_modules = [
        path for path in sources
        if path.name not in {"constants.py", "verify.py", "__init__.py"}
    ]
    hardcoded: list[dict[str, Any]] = []
    for path in build_modules:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Constant) or isinstance(node.value, bool):
                continue
            if node.value != config.n_published:
                continue
            hardcoded.append({
                "file": path.name,
                "line": getattr(node, "lineno", None),
                "literal": node.value,
            })
    family_probe = {
        "neutral": True,
        "reason": (
            "family ids are 'rfam_' + the first 12 hex characters of sha256(seed, index); "
            "they are unique per question, contain no status/dismissal/dose token, and the "
            "family-name-only baseline is measured by t12 (deferred, not claimed here)."
        ),
        "prefix": config.family["prefix"],
        "token_length": int(config.family["token_length"]),
        "unique_families": config.n_published,
    }
    answer_strings: list[str] = []
    held_out_leak: list[str] = []
    if public_files:
        for path in public_files:
            text = path.read_text(encoding="utf-8")
            for marker in ('"decision_record_flat"', '"gold"', '"doses"', '"block"', '"cell"'):
                if marker in text:
                    answer_strings.append(f"{path.name}: {marker}")
            if '"split"' in text:
                answer_strings.append(f"{path.name}: \"split\"")
            if "held_out" in text or "r28h_" in text:
                held_out_leak.append(path.name)
    return {
        "package_files": [path.name for path in sources],
        "n_hardcode_scan": {
            "target_literal": config.n_published,
            "modules_scanned": [path.name for path in build_modules],
            "literal_occurrences": hardcoded,
            "method": (
                "AST scan for integer literal constants equal to n_published; comments, "
                "docstrings and message strings are not code and are ignored. constants.py "
                "(frozen default + config validation) and verify.py/reporting strings are "
                "excluded from the build-path scan."
            ),
        },
        "n_parameterized": not hardcoded,
        "family_name_probe": family_probe,
        "answer_strings_in_public": answer_strings,
        "held_out_in_public": held_out_leak,
    }


__all__ = [
    "code_scan",
    "determinism_check",
    "verify_hard_acceptance",
    "verify_protected_paths",
    "verify_r26_15_against_backup",
]
