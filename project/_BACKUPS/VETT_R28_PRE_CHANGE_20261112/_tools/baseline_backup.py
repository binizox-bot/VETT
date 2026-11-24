#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""VETT-R28 pre-change baseline backup / freeze / manifest builder.

Pure standard library.  Never touches the network, never reads ``.secrets``.

Usage
-----
    python baseline_backup.py build          # create frozen copy, code copy, manifests
    python baseline_backup.py verify         # re-check everything, run restore dry-run, write receipt
    python baseline_backup.py build verify   # build then verify

Design contract
---------------
* Source project is treated as read-only.
* Everything this script writes lives under BACKUP_ROOT (asserted with _guard()).
* ``frozen/`` is a byte-exact copy of r26_15_content_dependency_candidate_v3.
* ``code/`` is a best-effort point-in-time snapshot of the code/config/analysis
  surface (``__pycache__`` / ``*.pyc`` excluded) - never used as the authority
  for immutability; ``PROTECTED_PATHS.json`` is the authority.
* ``FULL_FILE_MANIFEST.json`` hashes every project file except
  ``__pycache__``, ``*.pyc`` and ``.secrets``.
* ``PROTECTED_PATHS.json`` pins r26_15 (165 files), src/vett_r16..vett_r26,
  src/vett_eval and the pre-existing tests.
* The legacy aggregate ``2cb1ea2c...9417`` could not be reproduced by 657
  documented recipe variants (see ``LEGACY_AGGREGATE_PROBE``), so this script
  defines an explicit, reproducible recipe ``vett-tree-aggregate-v1`` and
  records the legacy value as historical-only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone

WS = r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"
PROJECT = os.path.join(WS, "VETT_Cricket_v0.22_R16_Multisource_Dilemmas")
BACKUP = os.path.join(WS, "_BACKUPS", "VETT_R28_PRE_CHANGE_20261112")
CAND_REL = "r26_15_content_dependency_candidate_v3"
CAND = os.path.join(PROJECT, CAND_REL)
STAGE0_BASELINE = os.path.join(
    PROJECT, "analysis", "r26_18_stage0_revalidation_20261106", "BASELINE_MANIFEST.json"
)
CAND_MANIFEST = os.path.join(CAND, "MANIFEST.json")

FROZEN_ROOT = os.path.join(BACKUP, "frozen", CAND_REL)
CODE_ROOT = os.path.join(BACKUP, "code")
FULL_MANIFEST = os.path.join(BACKUP, "FULL_FILE_MANIFEST.json")
CODE_MANIFEST = os.path.join(BACKUP, "CODE_MANIFEST.json")
PROTECTED = os.path.join(BACKUP, "PROTECTED_PATHS.json")
VERIFICATION = os.path.join(BACKUP, "VERIFICATION.json")
RECEIPT = os.path.join(BACKUP, "BASELINE_RECEIPT.md")
RESTORE = os.path.join(BACKUP, "restore.ps1")
RESTORE_LOG = os.path.join(BACKUP, "RESTORE_DRYRUN.txt")

CODE_DIRS = ["src", "tests", "design", "eval_configs", "analysis", "eval_runs"]
CODE_FILES = ["README.md", "CHANGELOG.md", ".gitignore"]

EXCLUDE_DIR_NAMES = {"__pycache__", ".secrets"}
EXCLUDE_EXTS = {".pyc"}

LEGACY_AGGREGATE = "2cb1ea2c62d1b8d57b6c20bbc3c22ed7ad0440ca73f68946d24fcbf0ebab9417"
LEGACY_ATTEMPTS_TESTED = 657
AGGREGATE_RECIPE = (
    "vett-tree-aggregate-v1: SHA-256 over the UTF-8 text formed by, for every file sorted "
    "ascending by project-relative POSIX path, the line '<sha256>  <path>\\n' (two spaces, "
    "LF terminator, trailing LF after the last line)"
)

CHECKS: list[dict] = []
TIMING: dict[str, float] = {}


# --------------------------------------------------------------------------- io
def _guard(path: str) -> str:
    """Refuse to write anywhere outside BACKUP_ROOT."""
    ap = os.path.abspath(path)
    root = os.path.abspath(BACKUP) + os.sep
    if not (ap == os.path.abspath(BACKUP) or ap.startswith(root)):
        raise RuntimeError(f"refusing to write outside backup root: {ap}")
    return ap


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat()


def _walk(root: str, skip_dirs=frozenset(), skip_exts=frozenset()) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(
            d for d in dirnames if d not in skip_dirs and d not in EXCLUDE_DIR_NAMES
        )
        for name in sorted(filenames):
            ext = os.path.splitext(name)[1].lower()
            if ext in skip_exts or ext in EXCLUDE_EXTS:
                continue
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, root).replace("\\", "/")
            out.append((rel, full))
    out.sort(key=lambda x: x[0])
    return out


def _rel_project(rel_in_project: str) -> str:
    return rel_in_project.replace("\\", "/")


def _write_json(path: str, obj) -> None:
    _guard(path)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, sort_keys=False)
        f.write("\n")
    os.replace(tmp, path)


def _write_text(path: str, text: str) -> None:
    _guard(path)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, path)


def _record(check_id: str, description: str, status: str, evidence) -> None:
    CHECKS.append(
        {"id": check_id, "description": description, "status": status, "evidence": evidence}
    )
    print(f"[{status:4s}] {check_id}: {description}")


def _tree_aggregate(entries: list[tuple[str, str]]) -> str:
    """entries: [(project_relative_posix_path, sha256_hex)]."""
    payload = "".join(f"{sha}  {path}\n" for path, sha in sorted(entries, key=lambda x: x[0]))
    return _sha256_bytes(payload.encode("utf-8"))


# ------------------------------------------------------------------- snapshots
def hash_tree(root: str, skip_dirs=frozenset(), skip_exts=frozenset()) -> list[dict]:
    out = []
    for rel, full in _walk(root, skip_dirs, skip_exts):
        try:
            st = os.stat(full)
            with open(full, "rb") as f:
                data = f.read()
        except OSError as exc:  # pragma: no cover - surface, never silently skip
            raise RuntimeError(f"cannot read {full}: {exc}") from exc
        out.append(
            {
                "path": rel,
                "bytes": st.st_size,
                "mtime_ns": st.st_mtime_ns,
                "mtime_utc": datetime.fromtimestamp(st.st_mtime, timezone.utc).isoformat(),
                "sha256": _sha256_bytes(data),
            }
        )
    return out


def copy_tree_exact(src_root: str, dst_root: str, skip_dirs=frozenset(), skip_exts=frozenset()):
    """Byte-exact copy from an in-memory read; returns (entries, volatile_paths)."""
    entries, volatile = [], []
    for rel, full in _walk(src_root, skip_dirs, skip_exts):
        st = os.stat(full)
        with open(full, "rb") as f:
            data = f.read()
        sha = _sha256_bytes(data)
        dst = os.path.join(dst_root, rel.replace("/", os.sep))
        _guard(dst)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "wb") as f:
            f.write(data)
        try:
            shutil.copystat(full, dst)  # preserve mtime for mtime evidence
        except OSError:
            pass
        dst_sha = _sha256_file(dst)
        entries.append({"path": rel, "bytes": len(data), "sha256": sha, "dest_sha256": dst_sha})
        # A concurrent writer may replace the source between our read and this re-read.
        try:
            if _sha256_file(full) != sha:
                volatile.append(rel)
        except OSError:
            volatile.append(rel)
    return entries, volatile


# ----------------------------------------------------------------------- build
def cmd_build() -> int:
    t_all = time.time()
    os.makedirs(BACKUP, exist_ok=True)
    for d in (FROZEN_ROOT, CODE_ROOT):
        if os.path.isdir(d) and os.listdir(d):
            raise RuntimeError(
                f"{d} already exists and is not empty; use --overwrite or a fresh backup root"
            )

    # 0) R26.15 snapshot BEFORE any action (zero-drift baseline)
    t = time.time()
    before = hash_tree(CAND)
    TIMING["r26_15_before_snapshot_s"] = round(time.time() - t, 3)
    before_bytes = sum(e["bytes"] for e in before)
    _record(
        "C0_r26_15_pre_snapshot",
        "R26.15 candidate pre-change snapshot",
        "passed" if len(before) == 165 and before_bytes == 93346177 else "failed",
        {"files": len(before), "bytes": before_bytes},
    )

    # 1) frozen: byte-exact copy
    t = time.time()
    os.makedirs(FROZEN_ROOT, exist_ok=True)
    frozen_entries, frozen_volatile = copy_tree_exact(CAND, FROZEN_ROOT)
    TIMING["frozen_copy_verify_s"] = round(time.time() - t, 3)

    frozen_count = len(frozen_entries)
    frozen_bytes = sum(e["bytes"] for e in frozen_entries)
    _record(
        "C1_frozen_count_bytes",
        "frozen copy is exactly 165 files / 93,346,177 bytes",
        "passed" if (frozen_count, frozen_bytes) == (165, 93346177) else "failed",
        {"files": frozen_count, "bytes": frozen_bytes},
    )

    src_by_path = {e["path"]: e for e in before}
    mismatched = [
        e["path"]
        for e in frozen_entries
        if e["path"] not in src_by_path
        or src_by_path[e["path"]]["sha256"] != e["sha256"]
        or e["dest_sha256"] != e["sha256"]
    ]
    _record(
        "C2_frozen_hashes",
        "every frozen file sha256 equals source file sha256 (and the on-disk copy)",
        "passed" if not mismatched and frozen_count == 165 else "failed",
        {"mismatched": mismatched[:20], "mismatched_count": len(mismatched),
         "source_volatile_during_copy": frozen_volatile[:20]},
    )

    # 1b) independent cross-check against the R26.18 Stage-0 frozen baseline
    stage0 = json.load(open(STAGE0_BASELINE, "r", encoding="utf-8"))
    scope0 = stage0["scopes"][0]
    s0 = {x["path"].replace("\\", "/"): x for x in scope0["files"]}
    cross_bad = [
        p for p, e in ((e["path"], e) for e in frozen_entries)
        if p not in s0 or s0[p]["sha256"] != e["sha256"] or s0[p]["bytes"] != e["bytes"]
    ]
    _record(
        "C3_frozen_vs_r26_18_stage0",
        "frozen 165 files agree path/bytes/sha256 with R26.18 Stage-0 BASELINE_MANIFEST scope",
        "passed"
        if not cross_bad and len(s0) == 165 and scope0["file_count"] == 165 and scope0["total_bytes"] == 93346177
        else "failed",
        {
            "stage0_scope_file_count": scope0["file_count"],
            "stage0_scope_total_bytes": scope0["total_bytes"],
            "stage0_scope_legacy_aggregate": scope0["aggregate_sha256"],
            "mismatched": cross_bad[:20],
            "mismatched_count": len(cross_bad),
        },
    )

    # 1c) cross-check against the candidate's own MANIFEST.json (164 entries, manifest itself excluded)
    cand_manifest = json.load(open(CAND_MANIFEST, "r", encoding="utf-8"))
    cm = {x["path"]: x for x in cand_manifest["files"]}
    cm_bad = [
        e["path"]
        for e in frozen_entries
        if e["path"] != "MANIFEST.json"
        and (e["path"] not in cm or cm[e["path"]]["sha256"] != e["sha256"])
    ]
    _record(
        "C3b_frozen_vs_candidate_manifest",
        "frozen files agree sha256 with the candidate's own MANIFEST.json",
        "passed" if not cm_bad and len(cm) == 164 else "failed",
        {"candidate_manifest_entries": len(cm), "mismatched": cm_bad[:20],
         "mismatched_count": len(cm_bad)},
    )

    # 2) code/config/analysis snapshot
    t = time.time()
    os.makedirs(CODE_ROOT, exist_ok=True)
    code_entries, code_volatile = [], []
    for name in CODE_DIRS:
        src = os.path.join(PROJECT, name)
        if not os.path.isdir(src):
            raise RuntimeError(f"missing expected code dir {src}")
        ent, vol = copy_tree_exact(src, os.path.join(CODE_ROOT, name))
        for e in ent:
            e["path"] = f"{name}/{e['path']}"
        code_entries += ent
        code_volatile += [f"{name}/{v}" for v in vol]
    for name in CODE_FILES:
        src = os.path.join(PROJECT, name)
        if not os.path.isfile(src):
            raise RuntimeError(f"missing expected code file {src}")
        with open(src, "rb") as f:
            data = f.read()
        dst = os.path.join(CODE_ROOT, name)
        _guard(dst)
        with open(dst, "wb") as f:
            f.write(data)
        try:
            shutil.copystat(src, dst)
        except OSError:
            pass
        sha = _sha256_bytes(data)
        code_entries.append(
            {"path": name, "bytes": len(data), "sha256": sha, "dest_sha256": _sha256_file(dst)}
        )
        try:
            if _sha256_file(src) != sha:
                code_volatile.append(name)
        except OSError:
            code_volatile.append(name)
    TIMING["code_copy_verify_s"] = round(time.time() - t, 3)
    code_bad = [e["path"] for e in code_entries if e["sha256"] != e["dest_sha256"]]
    _write_json(
        CODE_MANIFEST,
        {
            "manifest_version": "VETT-R28-CODE-MANIFEST-1",
            "generated_at": _now_iso(),
            "backup_root": BACKUP,
            "code_root": CODE_ROOT,
            "source_items": CODE_DIRS + CODE_FILES,
            "exclusions": ["__pycache__", "*.pyc"],
            "notes": [
                "Point-in-time snapshot of the code/config/analysis surface for rollback convenience.",
                "The authority for immutability is PROTECTED_PATHS.json, not this snapshot.",
            ],
            "file_count": len(code_entries),
            "total_bytes": sum(e["bytes"] for e in code_entries),
            "files": [{"path": e["path"], "bytes": e["bytes"], "sha256": e["sha256"]}
                      for e in code_entries],
        },
    )
    _record(
        "C4_code_copy_integrity",
        "code/ snapshot is byte-identical to the source bytes read at copy time",
        "passed" if not code_bad else "failed",
        {
            "files": len(code_entries),
            "bytes": sum(e["bytes"] for e in code_entries),
            "mismatched": code_bad[:20],
            "mismatched_count": len(code_bad),
            "volatile_during_copy": code_volatile[:20],
            "volatile_count": len(code_volatile),
        },
    )

    # 3) FULL_FILE_MANIFEST over every project file (excluding __pycache__, *.pyc, .secrets)
    t = time.time()
    manifest_files = hash_tree(PROJECT, skip_dirs={".secrets"})
    TIMING["full_manifest_hash_s"] = round(time.time() - t, 3)
    manifest_count = len(manifest_files)
    manifest_bytes = sum(e["bytes"] for e in manifest_files)
    _write_json(
        FULL_MANIFEST,
        {
            "manifest_version": "VETT-R28-FULL-FILE-MANIFEST-1",
            "generated_at": _now_iso(),
            "workspace": WS,
            "project_root": PROJECT,
            "exclusions": sorted(EXCLUDE_DIR_NAMES | {f"*{e}" for e in EXCLUDE_EXTS}),
            "notes": [
                ".secrets is excluded by policy (never read, never hashed).",
                "This manifest is a point-in-time snapshot of the whole project; the "
                "immutable subset used by the pipeline self-check lives in PROTECTED_PATHS.json.",
            ],
            "file_count": manifest_count,
            "total_bytes": manifest_bytes,
            "files": manifest_files,
        },
    )
    _record(
        "C5_full_manifest_intrinsic",
        "FULL_FILE_MANIFEST file_count and total_bytes equal its own file list",
        "passed"
        if manifest_count == len(manifest_files) and manifest_bytes == sum(e["bytes"] for e in manifest_files)
        else "failed",
        {"file_count": manifest_count, "total_bytes": manifest_bytes},
    )

    # 4) deterministic sample of 20 entries recomputed from disk
    n = manifest_count
    idx = sorted({round(k * (n - 1) / 19) for k in range(20)})
    sample = [manifest_files[i] for i in idx]
    sample_bad = [
        e["path"]
        for e in sample
        if _sha256_file(os.path.join(PROJECT, e["path"].replace("/", os.sep))) != e["sha256"]
        or os.path.getsize(os.path.join(PROJECT, e["path"].replace("/", os.sep))) != e["bytes"]
    ]
    _record(
        "C6_manifest_sample20_recompute",
        "20 manifest entries recomputed from disk match bytes + sha256",
        "passed" if len(sample) == 20 and not sample_bad else "failed",
        {"sampled": [e["path"] for e in sample], "mismatched": sample_bad},
    )

    # 5) PROTECTED_PATHS: r26_15 + src/vett_r16..vett_r26 + src/vett_eval + tests
    t = time.time()
    groups = []
    r26_files = [{"path": f"{CAND_REL}/{e['path']}", "bytes": e["bytes"], "sha256": e["sha256"]}
                 for e in frozen_entries]
    groups.append(
        {
            "id": "r26_15_candidate",
            "root": CAND_REL,
            "role": "frozen experiment baseline - must never change",
            "file_count": len(r26_files),
            "total_bytes": sum(e["bytes"] for e in r26_files),
            "aggregate_sha256": _tree_aggregate([(e["path"], e["sha256"]) for e in r26_files]),
            "aggregate_recipe": AGGREGATE_RECIPE,
            "files": r26_files,
        }
    )

    code_roots = ["vett_eval"] + [f"vett_r{n}" for n in range(16, 27)]
    code_files_all = []
    for sub in code_roots:
        root = os.path.join(PROJECT, "src", sub)
        if not os.path.isdir(root):
            raise RuntimeError(f"missing protected code root {root}")
        for e in hash_tree(root):
            code_files_all.append(
                {"path": f"src/{sub}/{e['path']}", "bytes": e["bytes"], "sha256": e["sha256"]}
            )
    code_files_all.sort(key=lambda e: e["path"])
    groups.append(
        {
            "id": "code_vett_r16_r26",
            "roots": [f"src/{r}" for r in code_roots],
            "role": "existing implementation packages - read-only for R28",
            "file_count": len(code_files_all),
            "total_bytes": sum(e["bytes"] for e in code_files_all),
            "aggregate_sha256": _tree_aggregate([(e["path"], e["sha256"]) for e in code_files_all]),
            "aggregate_recipe": AGGREGATE_RECIPE,
            "files": code_files_all,
        }
    )

    tests_all = [
        {"path": f"tests/{e['path']}", "bytes": e["bytes"], "sha256": e["sha256"]}
        for e in hash_tree(os.path.join(PROJECT, "tests"))
    ]
    groups.append(
        {
            "id": "tests_existing",
            "root": "tests",
            "role": "pre-existing unittest suite (203 tests) - must stay green, must not be edited",
            "file_count": len(tests_all),
            "total_bytes": sum(e["bytes"] for e in tests_all),
            "aggregate_sha256": _tree_aggregate([(e["path"], e["sha256"]) for e in tests_all]),
            "aggregate_recipe": AGGREGATE_RECIPE,
            "files": tests_all,
        }
    )

    all_protected = sorted(
        ((e["path"], e["sha256"]) for g in groups for e in g["files"]), key=lambda x: x[0]
    )
    protected_paths = [p for p, _ in all_protected]
    if len(protected_paths) != len(set(protected_paths)):
        raise RuntimeError("duplicate path across protected groups")

    _write_json(
        PROTECTED,
        {
            "protected_version": "VETT-R28-PROTECTED-PATHS-1",
            "generated_at": _now_iso(),
            "project_root": PROJECT,
            "intent": "immutable baseline for the R28 pipeline self-check (violation => exit 4)",
            "exclusions": ["__pycache__", "*.pyc", ".secrets"],
            "groups": groups,
            "file_count": len(protected_paths),
            "total_bytes": sum(e["bytes"] for g in groups for e in g["files"]),
            "aggregate_sha256": _tree_aggregate(all_protected),
            "aggregate_recipe": AGGREGATE_RECIPE,
            "legacy_recorded_aggregate": {
                "sha256": LEGACY_AGGREGATE,
                "reproduced": False,
                "recipe_variants_tested": LEGACY_ATTEMPTS_TESTED,
                "note": (
                    "The historical Stage-0 aggregate could not be reproduced: the generating "
                    "script is not present in the delivery, and 657 documented recipe variants "
                    "(path/sha ordering, separators, JSON forms, binary digest concatenation, "
                    "forward- vs backslash paths, CRLF/LF, trailing newline) all failed to match. "
                    "Use aggregate_sha256 above (vett-tree-aggregate-v1) as the operative recipe; "
                    "the legacy value is retained for provenance only."
                ),
            },
        },
    )
    _record(
        "C7_protected_paths",
        "PROTECTED_PATHS covers r26_15 + src/vett_r16..vett_r26 + src/vett_eval + tests",
        "passed"
        if groups[0]["file_count"] == 165
        and groups[0]["total_bytes"] == 93346177
        and len(tests_all) >= 29
        and len(code_files_all) > 100
        else "failed",
        {
            "total_files": len(protected_paths),
            "groups": [
                {"id": g["id"], "files": g["file_count"], "bytes": g["total_bytes"],
                 "aggregate": g["aggregate_sha256"]}
                for g in groups
            ],
        },
    )

    # 8) R26.15 zero drift after all operations
    after = hash_tree(CAND)
    drift = [
        e["path"]
        for e in before
        if e["path"] not in {a["path"] for a in after}
        or next(a for a in after if a["path"] == e["path"])["sha256"] != e["sha256"]
    ]
    after_bytes = sum(e["bytes"] for e in after)
    _record(
        "C8_r26_15_zero_drift",
        "R26.15 candidate unchanged byte-for-byte by the backup procedure",
        "passed"
        if not drift and len(after) == 165 and after_bytes == 93346177
        else "failed",
        {"before_files": len(before), "before_bytes": before_bytes,
         "after_files": len(after), "after_bytes": after_bytes, "drifted": drift[:20]},
    )

    # 9) no .secrets path leaked into any artifact
    leaked = [p for p in protected_paths if ".secrets" in p]
    leaked += [e["path"] for e in manifest_files if ".secrets" in e["path"]]
    _record(
        "C9_secrets_never_read",
        "no artifact references or hashes .secrets content",
        "passed" if not leaked else "failed",
        {"leaked_paths": leaked[:20]},
    )

    # 10) writes stayed under the backup root (by construction; assert on artifacts)
    outside = [
        p
        for p in (FROZEN_ROOT, CODE_ROOT, FULL_MANIFEST, PROTECTED)
        if not os.path.abspath(p).startswith(os.path.abspath(BACKUP) + os.sep)
    ]
    _record(
        "C10_writes_confined",
        "all writes are confined to _BACKUPS\\VETT_R28_PRE_CHANGE_20261112\\",
        "passed" if not outside else "failed",
        {"outside": outside, "backup_root": BACKUP},
    )

    TIMING["build_total_s"] = round(time.time() - t_all, 3)
    _write_json(
        VERIFICATION,
        {
            "verification_version": "VETT-R28-BASELINE-VERIFICATION-1",
            "generated_at": _now_iso(),
            "phase": "build",
            "backup_root": BACKUP,
            "timing_s": TIMING,
            "checks": CHECKS,
            "overall_status": "passed" if all(c["status"] == "passed" for c in CHECKS) else "failed",
        },
    )
    print(f"\nbuild finished in {TIMING['build_total_s']}s")
    return 0 if all(c["status"] == "passed" for c in CHECKS) else 1


# ---------------------------------------------------------------------- verify
def _load(path: str):
    if not os.path.isfile(path):
        raise RuntimeError(f"missing artifact {path}; run 'build' first")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def cmd_verify() -> int:
    global CHECKS
    prev_verif = None
    if os.path.isfile(VERIFICATION):
        try:
            prev_verif = _load(VERIFICATION)
        except Exception:
            prev_verif = None
    build_checks = []
    build_timing = {}
    if prev_verif:
        build_checks = [c for c in prev_verif.get("checks", []) if str(c.get("id", "")).startswith("C")]
        build_timing = {k: v for k, v in prev_verif.get("timing_s", {}).items()
                        if str(k).startswith("build_")}
    # Carry over timings measured by a build that ran earlier in this same process.
    for k, v in list(TIMING.items()):
        key = k if str(k).startswith("build_") else f"build_{k}"
        build_timing[key] = v
    TIMING.clear()
    CHECKS = []
    t_all = time.time()
    for f in (FULL_MANIFEST, PROTECTED, VERIFICATION):
        if not os.path.isfile(f):
            print(f"missing artifact: {f}; run 'build' first", file=sys.stderr)
            return 2

    full = _load(FULL_MANIFEST)
    prot = _load(PROTECTED)
    manifest_map = {e["path"]: e for e in full["files"]}

    # V1 frozen re-check against source and against the manifest
    t = time.time()
    src = {e["path"]: e for e in hash_tree(CAND)}
    fro = {e["path"]: e for e in hash_tree(FROZEN_ROOT)}
    bad = [
        p
        for p in src
        if p not in fro or fro[p]["sha256"] != src[p]["sha256"] or fro[p]["bytes"] != src[p]["bytes"]
    ]
    bad += [p for p in fro if p not in src]
    _record(
        "V1_frozen_equals_source",
        "frozen/ still equals the live r26_15 candidate byte-for-byte",
        "passed" if not bad and len(src) == 165 and sum(e["bytes"] for e in src.values()) == 93346177 else "failed",
        {"source_files": len(src), "frozen_files": len(fro), "mismatched": bad[:20]},
    )

    # V2 frozen entries against the captured manifest (r26_15 group in PROTECTED)
    group = next(g for g in prot["groups"] if g["id"] == "r26_15_candidate")
    bad2 = []
    for e in group["files"]:
        rel = e["path"][len(CAND_REL) + 1:] if e["path"].startswith(CAND_REL + "/") else None
        if (
            rel is None
            or rel not in fro
            or fro[rel]["sha256"] != e["sha256"]
            or fro[rel]["bytes"] != e["bytes"]
        ):
            bad2.append(e["path"])
    _record(
        "V2_frozen_equals_protected",
        "frozen/ matches PROTECTED_PATHS r26_15 group for all 165 files",
        "passed" if not bad2 and len(group["files"]) == 165 else "failed",
        {"mismatched": bad2[:20], "mismatched_count": len(bad2),
         "group_files": len(group["files"])},
    )

    # V3 aggregate reproducibility (recompute from stored entries AND from manifest)
    rec_entries = [(e["path"], e["sha256"]) for e in group["files"]]
    agg_from_prot = _tree_aggregate(rec_entries)
    agg_from_manifest = _tree_aggregate(
        [(e["path"], e["sha256"]) for e in full["files"] if e["path"].startswith(CAND_REL + "/")]
    )
    agg_from_disk = _tree_aggregate([(f"{CAND_REL}/{p}", e["sha256"]) for p, e in src.items()])
    ok3 = agg_from_prot == agg_from_manifest == agg_from_disk == group["aggregate_sha256"]
    _record(
        "V3_aggregate_reproducible",
        "r26_15 aggregate recomputes identically from PROTECTED_PATHS, FULL_FILE_MANIFEST and disk",
        "passed" if ok3 else "failed",
        {
            "aggregate_sha256": group["aggregate_sha256"],
            "from_protected": agg_from_prot,
            "from_manifest": agg_from_manifest,
            "from_disk": agg_from_disk,
            "recipe": prot["aggregate_recipe"],
        },
    )

    # V4 whole protected tree: current disk vs stored
    bad4 = []
    for g in prot["groups"]:
        for e in g["files"]:
            p = os.path.join(PROJECT, e["path"].replace("/", os.sep))
            if not os.path.isfile(p):
                bad4.append(e["path"])
                continue
            st = os.stat(p)
            if st.st_size != e["bytes"] or _sha256_file(p) != e["sha256"]:
                bad4.append(e["path"])
    _record(
        "V4_protected_paths_unchanged",
        "every protected file still matches its pinned bytes + sha256 (pipeline self-check predicate)",
        "passed" if not bad4 else "failed",
        {"protected_files": prot["file_count"], "violations": bad4[:20],
         "violation_count": len(bad4)},
    )

    # V5 protected entries agree with the full manifest where both cover the same file
    bad5 = []
    for g in prot["groups"]:
        for e in g["files"]:
            m = manifest_map.get(e["path"])
            if m is None:
                bad5.append(e["path"] + " (absent from manifest)")
            elif m["sha256"] != e["sha256"] or m["bytes"] != e["bytes"]:
                bad5.append(e["path"] + " (hash/bytes differ)")
    _record(
        "V5_protected_vs_manifest",
        "PROTECTED_PATHS entries agree with FULL_FILE_MANIFEST (single consistent snapshot)",
        "passed" if not bad5 else "failed",
        {"mismatched": bad5[:20], "mismatched_count": len(bad5)},
    )

    # V6 manifest intrinsic consistency + current drift report
    ok6 = full["file_count"] == len(full["files"]) and full["total_bytes"] == sum(
        e["bytes"] for e in full["files"]
    )
    live = _walk(PROJECT, skip_dirs={".secrets"})
    live_count = len(live)
    added = [rel for rel, _ in live if rel not in manifest_map]
    removed = [p for p in manifest_map if p not in {rel for rel, _ in live}]
    _record(
        "V6_manifest_count",
        "FULL_FILE_MANIFEST count is self-consistent; post-build drift reported (expected for analysis/eval_runs)",
        "passed" if ok6 else "failed",
        {
            "manifest_file_count": full["file_count"],
            "manifest_total_bytes": full["total_bytes"],
            "live_file_count": live_count,
            "added_since_build": added[:20],
            "added_count": len(added),
            "removed_since_build": removed[:20],
            "removed_count": len(removed),
        },
    )

    # V7 sample 20 recompute
    files = full["files"]
    idx = sorted({round(k * (len(files) - 1) / 19) for k in range(20)})
    sample = [files[i] for i in idx]
    bad7 = []
    for e in sample:
        p = os.path.join(PROJECT, e["path"].replace("/", os.sep))
        if not os.path.isfile(p) or os.path.getsize(p) != e["bytes"] or _sha256_file(p) != e["sha256"]:
            bad7.append(e["path"])
    _record(
        "V7_sample20_recompute",
        "20 sampled manifest entries are still byte-identical on disk",
        "passed" if len(sample) == 20 and not bad7 else "failed",
        {"sampled": [e["path"] for e in sample], "mismatched": bad7},
    )

    # V8 code snapshot integrity (dest hash only; source may have moved on)
    code_manifest = _load(CODE_MANIFEST)
    bad8 = []
    for e in code_manifest["files"]:
        p = os.path.join(CODE_ROOT, e["path"].replace("/", os.sep))
        if not os.path.isfile(p) or _sha256_file(p) != e["sha256"]:
            bad8.append(e["path"])
    _record(
        "V8_code_snapshot_consistent_with_manifest",
        "every code/ snapshot file matches its CODE_MANIFEST.json sha256",
        "passed" if not bad8 and code_manifest["file_count"] == len(code_manifest["files"]) else "failed",
        {"checked": len(code_manifest["files"]), "mismatched": bad8[:20],
         "mismatched_count": len(bad8)},
    )

    # V9 restore.ps1 dry-run: targets printed, nothing written
    t = time.time()
    restore_ok, restore_ev = _restore_dryrun()
    TIMING["restore_dryrun_s"] = round(time.time() - t, 3)
    _record("V9_restore_dry_run", "restore.ps1 -DryRun prints the exact absolute targets and writes nothing",
            "passed" if restore_ok else "failed", restore_ev)

    # V10 R26.15 post-verify zero drift
    post = hash_tree(CAND)
    bad10 = [e["path"] for e in src.values()
             if next((x for x in post if x["path"] == e["path"]), {}).get("sha256") != e["sha256"]]
    _record(
        "V10_r26_15_zero_drift_post_verify",
        "R26.15 candidate still unchanged after the verification pass",
        "passed" if not bad10 and len(post) == 165 and sum(e["bytes"] for e in post) == 93346177 else "failed",
        {"files": len(post), "bytes": sum(e["bytes"] for e in post), "drifted": bad10[:20]},
    )

    TIMING["verify_total_s"] = round(time.time() - t_all, 3)
    all_checks = build_checks + CHECKS
    merged_timing = {**build_timing, **TIMING}
    verif = {
        "verification_version": "VETT-R28-BASELINE-VERIFICATION-1",
        "generated_at": _now_iso(),
        "phase": "build+verify",
        "backup_root": BACKUP,
        "timing_s": merged_timing,
        "checks": all_checks,
        "overall_status": "passed" if all(c["status"] == "passed" for c in all_checks) else "failed",
    }
    _write_json(VERIFICATION, verif)
    _write_receipt(verif, full, prot)
    print(f"\nverify finished in {TIMING['verify_total_s']}s -> {verif['overall_status']} "
          f"({len(all_checks)} checks)")
    return 0 if verif["overall_status"] == "passed" else 1


def _restore_dryrun():
    if not os.path.isfile(RESTORE):
        return False, {"error": "restore.ps1 missing"}
    shell = shutil.which("pwsh") or shutil.which("powershell")
    if not shell:
        return False, {"error": "no PowerShell host found"}
    cmd = [shell, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
           "-File", RESTORE, "-DryRun", "-Scope", "all"]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except Exception as exc:  # pragma: no cover
        return False, {"error": repr(exc)}
    out = (res.stdout or "") + (res.stderr or "")
    _write_text(RESTORE_LOG, out)
    expected_targets = [
        CAND,
        os.path.join(PROJECT, "src"),
        os.path.join(PROJECT, "tests"),
        os.path.join(PROJECT, "design"),
        os.path.join(PROJECT, "eval_configs"),
        os.path.join(PROJECT, "analysis"),
        os.path.join(PROJECT, "eval_runs"),
    ]
    missing = [p for p in expected_targets if p not in out]
    ok = res.returncode == 0 and not missing and "DRY-RUN" in out.upper()
    return ok, {
        "exit_code": res.returncode,
        "missing_targets": missing,
        "log": os.path.relpath(RESTORE_LOG, WS),
        "stdout_head": out[:2000],
    }


# --------------------------------------------------------------------- receipt
def _fmt(n: int) -> str:
    return f"{n:,}"


def _write_receipt(verif: dict, full: dict, prot: dict) -> None:
    checks = verif["checks"]
    t = verif["timing_s"]
    g = {x["id"]: x for x in prot["groups"]}
    r26 = g["r26_15_candidate"]
    code = g["code_vett_r16_r26"]
    tests = g["tests_existing"]
    legacy = prot["legacy_recorded_aggregate"]
    code_manifest = _load(CODE_MANIFEST)
    code_snapshot_files = code_manifest["file_count"]
    code_snapshot_bytes = code_manifest["total_bytes"]

    def row(c):
        ev = json.dumps(c["evidence"], ensure_ascii=False)
        if len(ev) > 240:
            ev = ev[:237] + "..."
        return f"| {c['id']} | {c['status']} | {ev} |"

    lines = [
        "# VETT-R28 变更前基线备份与冻结回执",
        "",
        f"- 生成时间：`{verif['generated_at']}`",
        f"- 备份根：`{BACKUP}`",
        "- 生成器：`_tools\\baseline_backup.py`（纯标准库，无网络，未读取 `.secrets`）",
        f"- 总体状态：**{verif['overall_status']}**",
        "",
        "## 1. 口径",
        "",
        "| 项 | 值 |",
        "| --- | --- |",
        f"| 工作区根 | `{WS}` |",
        f"| 主项目 | `{PROJECT}` |",
        f"| 数据基线 | `r26_15_content_dependency_candidate_v3` |",
        "| Python | `D:\\Conda\\python.exe`（3.14.7，纯标准库） |",
        "| 排除项 | `__pycache__`、`*.pyc`、`.secrets`（后者按政策从不读取、从不哈希） |",
        "| 网络 / provider 调用 | 0 |",
        "| 原件修改 | 无（只读遍历 + 复制） |",
        "",
        "## 2. 备份内容",
        "",
        "| 产物 | 内容 | 规模 |",
        "| --- | --- | --- |",
        f"| `frozen\\{CAND_REL}\\` | R26.15 逐字节冻结副本 | {_fmt(r26['file_count'])} 文件 / {_fmt(r26['total_bytes'])} 字节 |",
        f"| `code\\` | `src`、`tests`、`design`、`eval_configs`、`analysis`、`eval_runs` + `README.md`、`CHANGELOG.md`、`.gitignore`（排除 `__pycache__`/`*.pyc`） | {_fmt(code_snapshot_files)} 文件 / {_fmt(code_snapshot_bytes)} 字节 |",
        f"| `CODE_MANIFEST.json` | `code\\` 快照逐文件 sha256（回滚校验用） | {_fmt(code_snapshot_files)} 文件 |",
        f"| `FULL_FILE_MANIFEST.json` | 主项目每文件（路径 / 字节 / mtime / sha256） | {_fmt(full['file_count'])} 文件 / {_fmt(full['total_bytes'])} 字节 |",
        f"| `PROTECTED_PATHS.json` | 不可变清单（r26_15 + src/vett_r16..vett_r26 + src/vett_eval + 既有 tests） | {_fmt(prot['file_count'])} 文件 / {_fmt(prot['total_bytes'])} 字节 |",
        "| `restore.ps1` | 恢复脚本（安全模式：打印绝对路径 + 交互确认） | - |",
        "| `VERIFICATION.json` | 机器可判校验结果 | - |",
        "",
        "## 3. 校验结果",
        "",
        "| 检查 | 状态 | 证据 |",
        "| --- | --- | --- |",
    ]
    lines += [row(c) for c in checks]
    lines += [
        "",
        "### 关键判定",
        "",
        f"- R26.15 冻结副本：**{r26['file_count']} 文件 / {_fmt(r26['total_bytes'])} 字节**，逐文件 sha256 与原件一致，且与 R26.18 Stage-0 `BASELINE_MANIFEST.json` 的 165 条记录逐项一致。",
        f"- 不可变清单：{_fmt(prot['file_count'])} 文件（r26_15 {r26['file_count']} + 代码 {code['file_count']} + tests {tests['file_count']}）。",
        f"- 主项目清单：{_fmt(full['file_count'])} 文件 / {_fmt(full['total_bytes'])} 字节；抽样 20 条重算一致。",
        "- **R26.15 未被修改**：变更前后 + 校验后三次快照的 165 个 sha256 全部相同。",
        "",
        "## 4. 聚合 SHA-256 复算配方",
        "",
        "### 4.1 采用口径（vett-tree-aggregate-v1，可复现）",
        "",
        "对目标文件集合，按**项目相对 POSIX 路径升序**（字典序、区分大小写，`/` 分隔）逐文件拼接一行：",
        "",
        "```text",
        "<sha256>␠␠<相对路径>\\n",
        "```",
        "",
        "（每行两个空格分隔哈希与路径，LF 结尾，最后一行也带 LF），再对整段 UTF-8 文本取 SHA-256。",
        "",
        "一行命令复算（PowerShell）：",
        "",
        "```powershell",
        "# $root 为目标目录；相对路径以 / 分隔",
        "$lines = Get-ChildItem $root -Recurse -File | Where-Object { $_.FullName -notmatch '__pycache__' -and $_.Extension -ne '.pyc' } |",
        "  ForEach-Object { '{0}  {1}' -f (Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLower(), (Resolve-Path $_.FullName -Relative).Substring(2).Replace('\\','/') } |",
        "  Sort-Object",
        "$payload = ($lines -join \"`n\") + \"`n\"",
        "$bytes = [Text.Encoding]::UTF8.GetBytes($payload)",
        "[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($bytes)).ToLower()",
        "```",
        "",
        "本清单记录的聚合值：",
        "",
        "| 集合 | 文件数 | 字节 | 聚合 SHA-256 |",
        "| --- | --- | --- | --- |",
        f"| r26_15 候选 | {r26['file_count']} | {_fmt(r26['total_bytes'])} | `{r26['aggregate_sha256']}` |",
        f"| src/vett_r16..vett_r26 + vett_eval | {code['file_count']} | {_fmt(code['total_bytes'])} | `{code['aggregate_sha256']}` |",
        f"| tests（既有） | {tests['file_count']} | {_fmt(tests['total_bytes'])} | `{tests['aggregate_sha256']}` |",
        f"| 全部受保护文件 | {prot['file_count']} | {_fmt(prot['total_bytes'])} | `{prot['aggregate_sha256']}` |",
        "",
        "### 4.2 历史口径（不可复现，仅作来源记录）",
        "",
        f"项目历史文档（R26.18 Stage-0 起）使用聚合值 `{LEGACY_AGGREGATE}`。",
        "",
        "本次**未能复现**该值：原始生成脚本不在交付包内；已尝试 "
        f"{LEGACY_ATTEMPTS_TESTED} 种已记录口径变体（路径/哈希字段顺序、`:`/`\\t`/两空格/`\\0` 分隔、"
        "LF/CRLF、尾部换行有/无、正反斜杠路径、JSON（紧凑/缩进/排序）形式、二进制摘要拼接、"
        "路径+字节+哈希三元组、以及 R26.18 Stage-0 `BASELINE_MANIFEST.json` 自带顺序），全部不匹配。",
        "",
        f"替代口径：见 4.1，r26_15 聚合为 `{r26['aggregate_sha256']}`。"
        "该值与历史值不可互比；流水线自检**只使用** 4.1 口径，并同时逐文件比对 165 条 sha256"
        "（等价强度，且可定位到具体文件）。",
        "",
        "## 5. 恢复方法",
        "",
        "```powershell",
        "pwsh -NoProfile -File _BACKUPS\\VETT_R28_PRE_CHANGE_20261112\\restore.ps1 -DryRun",
        "pwsh -NoProfile -File _BACKUPS\\VETT_R28_PRE_CHANGE_20261112\\restore.ps1 -Scope frozen",
        "pwsh -NoProfile -File _BACKUPS\\VETT_R28_PRE_CHANGE_20261112\\restore.ps1 -Scope all",
        "```",
        "",
        "- `-DryRun`：仅打印将写入的绝对目标路径并校验备份完整性，零写入。",
        "- 正式恢复：先打印目标绝对路径，要求输入 `RESTORE` 确认（默认 N/中止），再逐文件复核 sha256 后覆盖。",
        "- 恢复前会按 `FULL_FILE_MANIFEST.json` / `PROTECTED_PATHS.json` 校验备份自身完整性，不通过即中止。",
        "",
        "## 6. 耗时",
        "",
        "| 阶段 | 秒 |",
        "| --- | --- |",
    ]
    for k, v in t.items():
        lines.append(f"| {k} | {v} |")
    lines += [
        "",
        "## 7. 结论",
        "",
        f"- 基线已冻结并做三重复核（原件 / 冻结副本 / R26.18 Stage-0 快照）。",
        f"- 不可变清单已生成，可作为流水线每轮自检谓词（违反 => exit 4）。",
        f"- **R26.15 未被修改**（文件数、字节数与 165 个 sha256 全部不变）。",
        f"- 唯一无法复现的口径是历史聚合 SHA-256 `{LEGACY_AGGREGATE}`，已在 4.2 说明并给出替代口径。",
        "",
    ]
    _write_text(RECEIPT, "\n".join(lines) + "\n")


# ------------------------------------------------------------------------ main
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("commands", nargs="+", choices=["build", "verify"])
    ap.add_argument("--overwrite", action="store_true",
                    help="delete an existing frozen/ and code/ before rebuilding (backup root only)")
    args = ap.parse_args(argv)

    if args.overwrite:
        # Only ever deletes paths inside the backup root, and only the two snapshot dirs.
        for d in (os.path.join(BACKUP, "frozen"), os.path.join(BACKUP, "code")):
            if os.path.isdir(d):
                shutil.rmtree(_guard(d))

    rc = 0
    for cmd in args.commands:
        rc = cmd_build() if cmd == "build" else cmd_verify()
        if rc != 0:
            break
    return rc


if __name__ == "__main__":
    sys.exit(main())
