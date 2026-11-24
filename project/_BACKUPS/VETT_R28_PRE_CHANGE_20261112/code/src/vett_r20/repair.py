from __future__ import annotations

import copy
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


VERSION = "VETT-Cricket-v0.26-R20-root-repair"

# These three source folders are byte-identical duplicates. They remain in the
# 220-item corpus as a dedicated duplicate-consistency slice, but are not
# counted as independent match roots in scientific results.
DUPLICATE_OF = {
    "match_0038": "match_0037",
    "match_0119": "match_0118",
    "match_0200": "match_0197",
}

CONSTRUCTION_REPLACEMENTS = {
    (
        "this anonymized kept the same basic shape as the original low-score "
        "blowout, but the rebuilt scorecard now gives it a slightly different "
        "rhythm"
    ): "this low-scoring match developed through two sharply different innings",
    (
        "this rebuilt seventeen-over match kept the same underlying shape as "
        "the source game but with a fully new scorecard fingerprint"
    ): "this seventeen-over match was decided by two contrasting recovery phases",
    (
        "this rewritten contest kept the same low-scoring chase architecture "
        "but moved every identifying scorecard fingerprint into a new structure"
    ): "this low-scoring contest turned on the difficult middle phase of each innings",
}

# A second, narrower family of leaks occurs in closing analysis.  These phrases
# talk about a match or scorecard having been reconstructed rather than about
# the cricket itself.  Keep ordinary cricket uses such as "the innings was
# rebuilt", while removing only the dataset-construction wording.
CONSTRUCTION_REGEX_REPLACEMENTS = (
    (r"\bfits the rebuilt match cleanly\b", "is fully justified"),
    (r"\bin this reconstructed match\b", "in this match"),
    (r"\bfits the reconstructed match cleanly\b", "is fully justified"),
    (r"\bfits the reconstructed match\b", "is fully justified"),
    (r"\bfits the reconstructed scorecard cleanly\b", "is fully justified"),
    (r"\bfits the reconstructed scorecard\b", "is fully justified"),
    (r"\bfits the rebuilt scorecard cleanly\b", "is fully justified"),
)

FORBIDDEN_CONSTRUCTION_PATTERNS = (
    r"\bscorecard fingerprint\b",
    r"\bsource game\b",
    r"\bthis anonymized\b",
    r"\brebuilt scorecard\b",
    r"\brebuilt match\b",
    r"\breconstructed scorecard\b",
    r"\breconstructed match\b",
    r"\bidentifying .* fingerprint\b",
)

FAILED_CHECKS = {
    "BAT_PLUS_EXTRAS",
    "BATTER_BALLS",
    "BOWLER_BALLS",
    "BOWLER_WICKETS",
    "BOWLING_RUNS",
    "FOW_FORMAT",
    "FOW_MONOTONIC",
    "MAX_PARTNERSHIP",
    "PARTNERSHIP_COMPONENTS",
    "PARTNERSHIP_FOW",
    "PARTNERSHIP_TOTAL",
    "POM_IN_SCORECARD",
}


def _json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def _jsonl_bytes(values: Iterable[dict[str, Any]]) -> bytes:
    return b"".join(
        (json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n").encode(
            "utf-8"
        )
        for value in values
    )


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _load_roots(path: Path) -> list[dict[str, Any]]:
    roots: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                roots.append(json.loads(line))
    return roots


def _replace_identity(value: Any, old_id: str, new_id: str) -> Any:
    if isinstance(value, str):
        return value.replace(old_id, new_id)
    if isinstance(value, list):
        return [_replace_identity(item, old_id, new_id) for item in value]
    if isinstance(value, dict):
        return {
            _replace_identity(key, old_id, new_id): _replace_identity(
                item, old_id, new_id
            )
            for key, item in value.items()
        }
    return value


def _source_hashes(match_dir: Path) -> dict[str, str]:
    names = {
        "commentary_sha256": "commentary.txt",
        "evidence_chain_sha256": "evidence_chain.md",
        "meta_sha256": "meta.json",
        "scorecard_sha256": "scorecard.md",
    }
    return {
        key: _sha256((match_dir / filename).read_bytes())
        for key, filename in names.items()
    }


def _restore_all_roots(
    roots: list[dict[str, Any]], raw_dir: Path
) -> list[dict[str, Any]]:
    by_id = {root["root_id"]: copy.deepcopy(root) for root in roots}
    for duplicate_id, source_id in DUPLICATE_OF.items():
        if duplicate_id in by_id:
            raise ValueError(f"duplicate-control ID already exists: {duplicate_id}")
        clone = _replace_identity(by_id[source_id], source_id, duplicate_id)
        clone["root_id"] = duplicate_id
        clone["source_match_id"] = duplicate_id
        clone["source_hashes"] = _source_hashes(raw_dir / duplicate_id)
        clone["r20_duplicate_of"] = source_id
        by_id[duplicate_id] = clone
    expected = {f"match_{index:04d}" for index in range(1, 221)}
    if set(by_id) != expected:
        missing = sorted(expected - set(by_id))
        extra = sorted(set(by_id) - expected)
        raise ValueError(f"220-root identity mismatch; missing={missing}, extra={extra}")
    return [by_id[match_id] for match_id in sorted(by_id)]


def _table_context(root: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {table["table_id"]: table for table in root.get("tables", [])}


def _row_context(table: dict[str, Any], row_id: str) -> dict[str, Any]:
    return next(
        (row for row in table.get("rows", []) if row.get("row_id") == row_id),
        {},
    )


def _same_innings(table: dict[str, Any], raw_innings: str) -> bool:
    if not raw_innings or raw_innings == "0":
        return table.get("innings_id") is None
    return table.get("innings_id") == f"I{raw_innings}"


def _cell_affected_by_failure(
    cell: dict[str, Any],
    table: dict[str, Any],
    failure: dict[str, str],
) -> bool:
    if not _same_innings(table, failure.get("innings", "")):
        return False
    check = failure["check"]
    table_type = table.get("table_type")
    column = cell.get("column")
    row = _row_context(table, str(cell.get("row_id", "")))
    field = str(row.get("Field", ""))

    if check == "POM_IN_SCORECARD":
        return table_type == "Match Summary" and field == "Player of the Match"
    if check == "BAT_PLUS_EXTRAS":
        return (
            (table_type == "Batting" and column in {"R"})
            or (
                table_type == "Innings Summary"
                and field in {"Total", "Total Extras"}
            )
        )
    if check == "BATTER_BALLS":
        return (
            (table_type == "Batting" and column in {"B", "SR"})
            or (table_type == "Innings Summary" and field == "Total")
        )
    if check == "BOWLER_BALLS":
        return (
            (table_type == "Bowling" and column in {"O", "Econ"})
            or (table_type == "Innings Summary" and field == "Total")
        )
    if check == "BOWLER_WICKETS":
        return (
            (table_type == "Bowling" and column == "W")
            or (table_type == "Batting" and column == "Dismissal")
            or table_type == "Fall of Wickets"
        )
    if check == "BOWLING_RUNS":
        return (
            (table_type == "Bowling" and column in {"R", "Econ"})
            or (
                table_type == "Innings Summary"
                and field in {"Total", "Byes", "Leg Byes"}
            )
        )
    if check in {"FOW_FORMAT", "FOW_MONOTONIC"}:
        return table_type == "Fall of Wickets"
    if check == "MAX_PARTNERSHIP":
        return (
            table_type == "Partnerships"
            or (table_type == "Innings Summary" and field == "Max Partnership")
        )
    if check in {"PARTNERSHIP_COMPONENTS", "PARTNERSHIP_TOTAL"}:
        return table_type == "Partnerships"
    if check == "PARTNERSHIP_FOW":
        return table_type in {"Partnerships", "Fall of Wickets"}
    raise ValueError(f"unmapped failed check: {check}")


def _sanitize_commentary(text: str) -> tuple[str, list[dict[str, str]]]:
    repaired = text
    edits: list[dict[str, str]] = []
    for original, replacement in CONSTRUCTION_REPLACEMENTS.items():
        pattern = re.compile(re.escape(original), flags=re.IGNORECASE)
        if pattern.search(repaired):
            repaired = pattern.sub(replacement, repaired)
            edits.append({"original": original, "replacement": replacement})
    for original, replacement in CONSTRUCTION_REGEX_REPLACEMENTS:
        pattern = re.compile(original, flags=re.IGNORECASE)
        if pattern.search(repaired):
            repaired = pattern.sub(replacement, repaired)
            edits.append({"original": original, "replacement": replacement})
    return repaired, edits


def _construction_hits(text: str) -> list[str]:
    return [
        pattern
        for pattern in FORBIDDEN_CONSTRUCTION_PATTERNS
        if re.search(pattern, text, flags=re.IGNORECASE)
    ]


def _source_record(match_id: str, raw_dir: Path) -> dict[str, Any]:
    match_dir = raw_dir / match_id
    commentary_bytes = (match_dir / "commentary.txt").read_bytes()
    commentary = commentary_bytes.decode("utf-8-sig")
    repaired, edits = _sanitize_commentary(commentary)
    hits = _construction_hits(repaired)
    if hits:
        raise ValueError(f"construction leakage remains in {match_id}: {hits}")
    scorecard = (match_dir / "scorecard.md").read_text(encoding="utf-8-sig")
    evidence_chain = (match_dir / "evidence_chain.md").read_text(
        encoding="utf-8-sig"
    )
    meta = json.loads((match_dir / "meta.json").read_text(encoding="utf-8-sig"))
    return {
        "match_id": match_id,
        "dataset_version": VERSION,
        "commentary": repaired,
        "scorecard": scorecard,
        "evidence_chain": evidence_chain,
        "meta": meta,
        "sanitization_edits": edits,
        "source_hashes": _source_hashes(match_dir),
        "repaired_commentary_sha256": _sha256(repaired.encode("utf-8")),
        "usage_policy": {
            "commentary": "SOURCE_REFERENCE_ONLY",
            "scorecard": "CANONICALIZATION_INPUT_PRIVATE",
            "evidence_chain": "PRIVATE_DO_NOT_EXPOSE_TO_SOLVERS",
        },
    }


def _repair_root(
    root: dict[str, Any],
    audit: dict[str, str],
    failures: list[dict[str, str]],
) -> dict[str, Any]:
    repaired = copy.deepcopy(root)
    tables = _table_context(repaired)
    masked = 0
    reasons = Counter()
    for cell in repaired.get("cells", []):
        table = tables[cell["table_id"]]
        cell_failures = [
            failure["check"]
            for failure in failures
            if _cell_affected_by_failure(cell, table, failure)
        ]
        cell["r20_original_gold_status"] = cell.get("gold_status")
        if cell_failures:
            cell["gold_status"] = "R20_UNSCORED_SOURCE_CONFLICT"
            cell["r20_conflict_checks"] = sorted(set(cell_failures))
            masked += 1
            reasons.update(set(cell_failures))
        else:
            cell["gold_status"] = "R20_VERIFIED_SOURCE"
            cell["r20_conflict_checks"] = []

    total = len(repaired.get("cells", []))
    scored = total - masked
    duplicate_of = repaired.get("r20_duplicate_of")
    repaired["dataset_version"] = VERSION
    repaired["r20_repair"] = {
        "release_status": "READY_FOR_R20_GENERATION",
        "original_curation_status": root.get("curation_status"),
        "original_recommended_action": audit.get("recommended_action"),
        "duplicate_of": duplicate_of,
        "independent_root": duplicate_of is None,
        "total_cells": total,
        "scored_verified_cells": scored,
        "masked_conflict_cells": masked,
        "masked_by_check": dict(sorted(reasons.items())),
        "source_failure_records": [
            {
                "innings": failure.get("innings"),
                "team": failure.get("team"),
                "check": failure.get("check"),
                "detail": failure.get("detail"),
            }
            for failure in failures
        ],
        "policy": (
            "Preserve source values; score only cells not implicated by a failed "
            "source-consistency check. Never guess an unidentifiable correction."
        ),
    }
    repaired["curation_status"] = "R20_READY_WITH_CELL_LEVEL_MASK"
    return repaired


def _file_record(base: Path, path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "path": path.relative_to(base).as_posix(),
        "bytes": len(data),
        "sha256": _sha256(data),
    }


def _report_markdown(summary: dict[str, Any]) -> str:
    return f"""# R20 220-Match Root Repair Report

## Decision

**{summary['status']}** — all {summary['matches']} source match IDs are represented.

## Corpus identity

- Independent canonical roots: {summary['independent_roots']}
- Duplicate-consistency controls: {summary['duplicate_controls']}
- Source commentaries sanitized for construction leakage: {summary['sanitized_commentaries']}

## Cell reliability

- Total source cells: {summary['total_cells']}
- Verified scored cells: {summary['scored_verified_cells']}
- Conflict-implicated cells excluded from scoring: {summary['masked_conflict_cells']}
- Matches with at least one masked cell: {summary['matches_with_masked_cells']}
- Minimum verified cells retained in one match: {summary['minimum_scored_cells_per_match']}

No ambiguous value is silently rewritten. A source-conflict mask removes only the table
regions implicated by a failed cricket-consistency check. The original value, original
status, failure code and audit detail remain in the repaired root for review.

The three exact duplicate source matches remain available as duplicate-consistency tests,
but scientific sample counts must report 217 independent matches rather than 220.
"""


def build_repair_release(
    roots_path: Path,
    raw_dir: Path,
    audit_csv: Path,
    check_details_csv: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    if any(path.is_file() for path in output_dir.rglob("*")):
        raise FileExistsError(f"repair output directory is not empty: {output_dir}")

    roots = _restore_all_roots(_load_roots(roots_path), raw_dir)
    audit_by_id = {row["match_id"]: row for row in _read_csv(audit_csv)}
    failed_by_id: dict[str, list[dict[str, str]]] = {
        match_id: [] for match_id in audit_by_id
    }
    for row in _read_csv(check_details_csv):
        if row.get("passed") == "0":
            if row.get("check") not in FAILED_CHECKS:
                raise ValueError(f"unmapped failed check: {row.get('check')}")
            failed_by_id[row["match_id"]].append(row)

    repaired_roots: list[dict[str, Any]] = []
    source_records: list[dict[str, Any]] = []
    for root in roots:
        match_id = root["root_id"]
        repaired_roots.append(
            _repair_root(root, audit_by_id[match_id], failed_by_id[match_id])
        )
        source_records.append(_source_record(match_id, raw_dir))

    roots_bytes = _jsonl_bytes(repaired_roots)
    sources_bytes = _jsonl_bytes(source_records)
    (output_dir / "canonical_roots_220_repaired.jsonl").write_bytes(roots_bytes)
    (output_dir / "source_documents_220_repaired.jsonl").write_bytes(sources_bytes)

    total_cells = sum(len(root["cells"]) for root in repaired_roots)
    scored_counts = [
        root["r20_repair"]["scored_verified_cells"] for root in repaired_roots
    ]
    masked_counts = [
        root["r20_repair"]["masked_conflict_cells"] for root in repaired_roots
    ]
    summary = {
        "dataset_version": VERSION,
        "status": "PASS",
        "matches": len(repaired_roots),
        "independent_roots": sum(
            root["r20_repair"]["independent_root"] for root in repaired_roots
        ),
        "duplicate_controls": sum(
            not root["r20_repair"]["independent_root"] for root in repaired_roots
        ),
        "duplicate_map": DUPLICATE_OF,
        "total_cells": total_cells,
        "scored_verified_cells": sum(scored_counts),
        "masked_conflict_cells": sum(masked_counts),
        "matches_with_masked_cells": sum(count > 0 for count in masked_counts),
        "minimum_scored_cells_per_match": min(scored_counts),
        "maximum_scored_cells_per_match": max(scored_counts),
        "sanitized_commentaries": sum(
            bool(record["sanitization_edits"]) for record in source_records
        ),
        "special_innings_counts": dict(
            sorted(Counter(len(root.get("innings", [])) for root in repaired_roots).items())
        ),
        "repair_policy": "CONSERVATIVE_CELL_MASK_NO_GUESSED_VALUES",
        "roots_sha256": _sha256(roots_bytes),
        "source_documents_sha256": _sha256(sources_bytes),
    }
    (output_dir / "REPAIR_SUMMARY.json").write_bytes(_json_bytes(summary))
    (output_dir / "REPAIR_REPORT.md").write_text(
        _report_markdown(summary), encoding="utf-8"
    )
    files = [
        _file_record(output_dir, path)
        for path in sorted(output_dir.rglob("*"))
        if path.is_file() and path.name != "MANIFEST.json"
    ]
    (output_dir / "MANIFEST.json").write_bytes(
        _json_bytes(
            {
                "dataset_version": VERSION,
                "file_count_excluding_manifest": len(files),
                "files": files,
            }
        )
    )
    return summary


def audit_repair_release(release_dir: Path) -> dict[str, Any]:
    errors: list[str] = []
    try:
        manifest = json.loads(
            (release_dir / "MANIFEST.json").read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError) as exc:
        return {"status": "FAIL", "errors": [f"manifest unreadable: {exc}"]}
    records = manifest.get("files", [])
    expected = {record.get("path"): record for record in records}
    actual = {
        path.relative_to(release_dir).as_posix(): path
        for path in release_dir.rglob("*")
        if path.is_file() and path.name != "MANIFEST.json"
    }
    if manifest.get("file_count_excluding_manifest") != len(records):
        errors.append("manifest count mismatch")
    if set(expected) != set(actual):
        errors.append("manifest file set mismatch")
    for relative_path in sorted(set(expected) & set(actual)):
        record = _file_record(release_dir, actual[relative_path])
        if record["bytes"] != expected[relative_path].get("bytes"):
            errors.append(f"byte mismatch: {relative_path}")
        if record["sha256"] != expected[relative_path].get("sha256"):
            errors.append(f"hash mismatch: {relative_path}")

    roots = _load_roots(release_dir / "canonical_roots_220_repaired.jsonl")
    sources = _load_roots(release_dir / "source_documents_220_repaired.jsonl")
    expected_ids = [f"match_{index:04d}" for index in range(1, 221)]
    if [root.get("root_id") for root in roots] != expected_ids:
        errors.append("root IDs are not the complete ordered 220-match set")
    if [record.get("match_id") for record in sources] != expected_ids:
        errors.append("source IDs are not the complete ordered 220-match set")
    for root in roots:
        cells = root.get("cells", [])
        if not cells:
            errors.append(f"{root.get('root_id')}: no cells")
            continue
        valid_statuses = {
            "R20_VERIFIED_SOURCE",
            "R20_UNSCORED_SOURCE_CONFLICT",
        }
        unknown = {cell.get("gold_status") for cell in cells} - valid_statuses
        if unknown:
            errors.append(f"{root.get('root_id')}: unknown statuses {sorted(unknown)}")
        if not any(cell.get("gold_status") == "R20_VERIFIED_SOURCE" for cell in cells):
            errors.append(f"{root.get('root_id')}: no verified cells")
        for failure in root.get("r20_repair", {}).get(
            "source_failure_records", []
        ):
            check = failure.get("check")
            if not any(check in cell.get("r20_conflict_checks", []) for cell in cells):
                errors.append(
                    f"{root.get('root_id')}: failed check {check} did not mask a cell"
                )
    for source in sources:
        hits = _construction_hits(str(source.get("commentary", "")))
        if hits:
            errors.append(f"{source.get('match_id')}: construction leakage {hits}")

    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "matches": len(roots),
        "source_records": len(sources),
        "independent_roots": sum(
            root.get("r20_repair", {}).get("independent_root") is True
            for root in roots
        ),
        "duplicate_controls": sum(
            root.get("r20_repair", {}).get("independent_root") is False
            for root in roots
        ),
    }


__all__ = [
    "DUPLICATE_OF",
    "VERSION",
    "audit_repair_release",
    "build_repair_release",
]
