"""Independent environment/baseline check used by the kit self-test.

Two things are re-computed from bytes, never read from a previous receipt:

1. the R26.15 frozen baseline (165 files) plus the other protected groups against
   ``_BACKUPS/VETT_R28_PRE_CHANGE_20261112/PROTECTED_PATHS.json``: every file's
   size and SHA-256, each group's ``vett-tree-aggregate-v1`` and the whole-set
   aggregate;
2. the current R28 preregistration and contract files against their freeze files,
   so that the kit's design/sample cannot be silently built on a drifted contract.

Exit code 0 on success, 4 on any mismatch.
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402


def tree_aggregate(rows: list[dict[str, Any]]) -> str:
    """vett-tree-aggregate-v1: sorted '<sha256>  <path>\\n' lines, one trailing LF."""
    ordered = sorted(rows, key=lambda row: row["path"])
    text = "".join(f"{row['sha256']}  {row['path']}\n" for row in ordered)
    return common.sha256_text(text)


def check_protected_paths(protected_path: str) -> dict[str, Any]:
    protected = common.load_json(protected_path)
    project_root = protected["project_root"]
    groups_out: list[dict[str, Any]] = []
    all_rows: list[dict[str, Any]] = []
    errors: list[str] = []
    total_files = 0
    total_bytes = 0
    for group in protected.get("groups", []):
        rows = []
        group_bytes = 0
        for entry in group.get("files", []):
            relative = entry["path"]
            absolute = os.path.join(project_root, relative.replace("/", os.sep))
            row = {"path": relative, "expected_sha256": entry["sha256"], "expected_bytes": entry["bytes"]}
            if not os.path.isfile(absolute):
                errors.append(f"{group['id']}: missing {relative}")
                row.update({"sha256": None, "bytes": None, "status": "MISSING"})
            else:
                size = os.path.getsize(absolute)
                digest = common.sha256_file(absolute)
                row.update({"sha256": digest, "bytes": size, "status": "OK"})
                if size != entry["bytes"]:
                    errors.append(f"{group['id']}: bytes {relative}: {size} != {entry['bytes']}")
                    row["status"] = "BYTES_MISMATCH"
                if digest != entry["sha256"]:
                    errors.append(f"{group['id']}: sha256 {relative}")
                    row["status"] = "SHA_MISMATCH"
                group_bytes += size
            rows.append(row)
            all_rows.append({"path": relative, "sha256": row["sha256"] or "", "bytes": row["bytes"] or 0})
        aggregate = tree_aggregate([{"path": r["path"], "sha256": r["sha256"]} for r in rows if r["sha256"]])
        expected_aggregate = group.get("aggregate_sha256")
        if expected_aggregate and aggregate != expected_aggregate:
            errors.append(f"{group['id']}: group aggregate {aggregate} != {expected_aggregate}")
        if group.get("file_count") is not None and len(rows) != group["file_count"]:
            errors.append(f"{group['id']}: file count {len(rows)} != {group['file_count']}")
        if group.get("total_bytes") is not None and group_bytes != group["total_bytes"]:
            errors.append(f"{group['id']}: group bytes {group_bytes} != {group['total_bytes']}")
        groups_out.append(
            {
                "id": group.get("id"),
                "files": len(rows),
                "bytes": group_bytes,
                "aggregate_sha256": aggregate,
                "expected_aggregate_sha256": expected_aggregate,
                "bytes_ok": group.get("total_bytes") in (None, group_bytes),
                "aggregate_ok": expected_aggregate in (None, aggregate),
            }
        )
        total_files += len(rows)
        total_bytes += group_bytes
    overall = tree_aggregate([{"path": row["path"], "sha256": row["sha256"]} for row in all_rows if row["sha256"]])
    if protected.get("aggregate_sha256") and overall != protected["aggregate_sha256"]:
        errors.append(f"protected aggregate {overall} != {protected['aggregate_sha256']}")
    if protected.get("file_count") is not None and total_files != protected["file_count"]:
        errors.append(f"protected file count {total_files} != {protected['file_count']}")
    return {
        "protected_path": os.path.abspath(protected_path),
        "schema": protected.get("protected_version"),
        "groups": groups_out,
        "totals": {
            "files": total_files,
            "bytes": total_bytes,
            "aggregate_sha256": overall,
            "expected_aggregate_sha256": protected.get("aggregate_sha256"),
            "aggregate_ok": overall == protected.get("aggregate_sha256"),
        },
        "errors": errors,
        "ok": not errors,
    }


def check_freeze_binding() -> dict[str, Any]:
    run = common.run_root()
    contract_path = os.path.join(run, "02_contract", "r28_contract.json")
    contract_freeze_path = os.path.join(run, "02_contract", "contract_freeze.json")
    prereg_path = os.path.join(run, "preregistration.json")
    prereg_freeze_path = os.path.join(run, "prereg_freeze.json")
    result: dict[str, Any] = {"ok": True, "checks": []}

    def add(name: str, path: str, expected_sha: str | None, expected_bytes: int | None) -> None:
        exists = os.path.isfile(path)
        actual_sha = common.sha256_file(path) if exists else None
        actual_bytes = os.path.getsize(path) if exists else None
        ok = exists and (expected_sha is None or actual_sha == expected_sha) and (expected_bytes is None or actual_bytes == expected_bytes)
        result["checks"].append(
            {
                "name": name,
                "path": os.path.abspath(path),
                "exists": exists,
                "sha256": actual_sha,
                "bytes": actual_bytes,
                "expected_sha256": expected_sha,
                "expected_bytes": expected_bytes,
                "ok": ok,
            }
        )
        if not ok:
            result["ok"] = False

    if os.path.isfile(contract_freeze_path):
        freeze = common.load_json(contract_freeze_path)
        add("contract_json", contract_path, freeze["file"]["sha256"], freeze["file"]["bytes"])
        doc = freeze.get("doc_files", {}).get("R28_CONTRACT.md")
        if doc:
            add("contract_md", os.path.join(run, "02_contract", "R28_CONTRACT.md"), doc["sha256"], doc["bytes"])
    else:
        result["ok"] = False
        result["checks"].append({"name": "contract_freeze", "path": contract_freeze_path, "ok": False, "note": "missing"})
    if os.path.isfile(prereg_freeze_path):
        freeze = common.load_json(prereg_freeze_path)
        files = freeze.get("files", {})
        if "preregistration.json" in files:
            add("preregistration_json", prereg_path, files["preregistration.json"]["sha256"], files["preregistration.json"]["bytes"])
        if "PREREGISTRATION.md" in files:
            add(
                "preregistration_md",
                os.path.join(run, "PREREGISTRATION.md"),
                files["PREREGISTRATION.md"]["sha256"],
                files["PREREGISTRATION.md"]["bytes"],
            )
    else:
        result["ok"] = False
        result["checks"].append({"name": "prereg_freeze", "path": prereg_freeze_path, "ok": False, "note": "missing"})
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify R26.15 zero-drift and contract/prereg freeze binding")
    parser.add_argument(
        "--protected-paths",
        default=os.path.join(common.workspace_root(), "_BACKUPS", "VETT_R28_PRE_CHANGE_20261112", "PROTECTED_PATHS.json"),
    )
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    protected = check_protected_paths(args.protected_paths)
    freeze = check_freeze_binding()
    result = {
        "schema": f"{common.SCHEMA_PREFIX}.baseline_check.v1",
        "kit_version": common.KIT_VERSION,
        "generated_at_utc": common.utc_now(),
        "protected_paths": protected,
        "freeze_binding": freeze,
        "ok": protected["ok"] and freeze["ok"],
        "notes": [
            "Every hash is recomputed from bytes in this run; no receipt is trusted.",
            "R26.15 is read-only in this kit; the check never writes inside the dataset.",
        ],
    }
    if args.out:
        common.write_json(args.out, result)
    print(
        common.canonical_json(
            {
                "ok": result["ok"],
                "protected_files": protected["totals"]["files"],
                "protected_bytes": protected["totals"]["bytes"],
                "protected_aggregate": protected["totals"]["aggregate_sha256"],
                "freeze_ok": freeze["ok"],
                "n_errors": len(protected["errors"]) + (0 if freeze["ok"] else 1),
            }
        )
    )
    return 0 if result["ok"] else 4


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except common.KitError as exc:
        common.eprint(f"ERROR {exc}")
        raise SystemExit(4)
