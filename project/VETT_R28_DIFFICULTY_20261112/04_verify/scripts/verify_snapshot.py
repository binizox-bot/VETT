"""Verify the 04_verify artefacts against `GATE_J_SNAPSHOT.json` (S1) and classify drift.

Why this exists
---------------
`J_GATE.json` carries a volatile `generated_at_utc`: any consumer that *runs* `j_gate.py`
(t20's closed-loop verification does exactly that) rewrites the file and its sha256 changes,
even though every verdict, count and evidence field stays identical.  Treating that as
"drift" makes every downstream audit lose its anchor; treating *real* content changes as
harmless is worse.  So the snapshot carries two hashes per artefact family:

    sha256                      -> exact bytes (what t8 pins)
    content_sha256_excluding_timestamp -> everything except `generated_at_utc`

and this tool classifies each artefact as:

    IDENTICAL        bytes match the snapshot
    METADATA_ONLY    bytes differ but the timestamp-free content digest matches
                     (no downstream re-verification needed; re-quote the new byte hash)
    CONTENT_CHANGED  content digest differs -> anchor invalid, needs a new snapshot id (S2…)
    MISSING          the file is gone

Usage:
    python verify_snapshot.py                 # human readable, exit 0/4
    python verify_snapshot.py --json          # machine readable
    python verify_snapshot.py --expect S1     # fail if the snapshot id is not S1

Exit codes: 0 = no CONTENT_CHANGED / MISSING, 4 = anchor invalid.
Read-only, stdlib only, no network.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
VERIFY_ROOT = HERE.parent
SNAPSHOT_PATH = VERIFY_ROOT / "GATE_J_SNAPSHOT.json"

# F8: `J_GATE.json` also embeds `verify_checked_at_utc` (copied from the protocol verifier's
# result file, which is rewritten on every `protocol_verify.py --check`).  That is upstream
# metadata, not gate content, so it is excluded from the content digest as well.
# F8 (two lobes): the J0 evidence block is emitted **twice** in J_GATE.json (once at
# `protocol_precondition`, once at `items.J0_protocol_precondition`), and both copies carry the
# upstream verifier's `verify_checked_at_utc`, which changes on every `protocol_verify --check`.
# Excluding only one copy leaves the content digest non-deterministic.
RECIPE = ("vett-gate-content-digest/v2: 1) 读取 J_GATE.json；2) 递归删除路径 "
          "generated_at_utc、protocol_precondition.evidence.verify_checked_at_utc、"
          "items.J0_protocol_precondition.evidence.verify_checked_at_utc；3) "
          "sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')) 的 UTF-8 字节)。"
          "实现见 scripts/verify_snapshot.py --content-digest；不要自行重实现。")

VOLATILE_PATHS = (
    "generated_at_utc",
    "protocol_precondition.evidence.verify_checked_at_utc",
    "items.J0_protocol_precondition.evidence.verify_checked_at_utc",
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _strip_paths(doc: Any, paths: tuple[str, ...]) -> Any:
    """Return a copy of ``doc`` with every dotted path removed."""
    import copy

    body = copy.deepcopy(doc)
    for path in paths:
        node = body
        parts = path.split(".")
        for part in parts[:-1]:
            if not isinstance(node, dict) or part not in node:
                node = None
                break
            node = node[part]
        if isinstance(node, dict):
            node.pop(parts[-1], None)
    return body


def content_digest(doc: Any, volatile: tuple[str, ...] = VOLATILE_PATHS) -> str:
    body = _strip_paths(doc, volatile) if isinstance(doc, dict) else doc
    return sha256_bytes(json.dumps(body, ensure_ascii=False, sort_keys=True,
                                   separators=(",", ":")).encode("utf-8"))


def classify(rel_path: str, expected: dict[str, Any], snapshot: dict[str, Any]) -> dict[str, Any]:
    path = VERIFY_ROOT / rel_path
    if not path.exists():
        return {"artifact": rel_path, "status": "MISSING", "expected_sha256": expected.get("sha256")}
    raw = path.read_bytes()
    actual = sha256_bytes(raw)
    out: dict[str, Any] = {"artifact": rel_path, "expected_sha256": expected.get("sha256"),
                           "actual_sha256": actual, "bytes": len(raw)}
    if actual == expected.get("sha256"):
        out["status"] = "IDENTICAL"
        return out
    repro = snapshot.get("reproducibility") or {}
    snapshot_content = (repro.get("content_sha256_excluding_volatile")
                        or repro.get("content_sha256_excluding_timestamp"))
    if rel_path.endswith(".json"):
        try:
            doc = json.loads(raw)
        except json.JSONDecodeError:
            out["status"] = "CONTENT_CHANGED"
            out["reason"] = "unparsable JSON"
            return out
        actual_content = content_digest(doc)
        out["actual_content_sha256"] = actual_content
        out["expected_content_sha256"] = snapshot_content
        if snapshot_content and actual_content == snapshot_content:
            out["status"] = "METADATA_ONLY"
            out["note"] = (f"仅 {list(VOLATILE_PATHS)} 变动；内容摘要一致 → 不触发下游重验，"
                           f"但需重新引用新的字节 sha256")
            return out
    out["status"] = "CONTENT_CHANGED"
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="classify drift against GATE_J_SNAPSHOT.json")
    parser.add_argument("--snapshot", default=str(SNAPSHOT_PATH))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--expect", default=None, help="expected snapshot_id, e.g. S2")
    parser.add_argument("--content-digest", nargs="?", const=str(VERIFY_ROOT / "J_GATE.json"),
                        default=None, help="print the content digest of a gate JSON (recipe v2)")
    parser.add_argument("--recipe", action="store_true", help="print the content-digest recipe")
    parser.add_argument("--fingerprints", action="store_true",
                        help="print a copy-paste fingerprint block for every 04_verify artefact "
                             "(so reports never quote a stale size/hash again)")
    args = parser.parse_args(argv)

    if args.fingerprints:
        import hashlib as _h
        files = ["J_GATE.json", "J_GATE.md", "J8_REOPEN_RUNBOOK.md",
                 "GATE_J_SNAPSHOT.json", "GATE_J_SNAPSHOT_POLICY.md",
                 "scripts/j_gate.py", "scripts/reaudit_packets.py",
                 "scripts/verify_snapshot.py", "scripts/recompute_content_hash.py",
                 "tests/test_j_gate.py"]
        print("| 文件 | bytes | sha256 |")
        print("|---|---:|---|")
        for name in files:
            path = VERIFY_ROOT / name
            if not path.exists():
                print(f"| `{name}` | — | MISSING |")
                continue
            raw = path.read_bytes()
            print(f"| `{name}` | {len(raw):,} | `{_h.sha256(raw).hexdigest()}` |")
        gate = VERIFY_ROOT / "J_GATE.json"
        if gate.exists():
            print()
            print(f"content_sha256_v2 = {content_digest(json.loads(gate.read_text(encoding='utf-8')))}")
        snap = VERIFY_ROOT / "GATE_J_SNAPSHOT.json"
        if snap.exists():
            doc = json.loads(snap.read_text(encoding="utf-8"))
            print(f"snapshot_id = {doc.get('snapshot_id')}  status = {doc.get('status')}")
        return 0

    if args.recipe:
        print(RECIPE)
        print("volatile_paths:", list(VOLATILE_PATHS))
        return 0
    if args.content_digest:
        target = Path(args.content_digest)
        doc = json.loads(target.read_text(encoding="utf-8"))
        print(content_digest(doc))
        return 0

    snapshot_path = Path(args.snapshot)
    if not snapshot_path.exists():
        print(f"[FAIL] snapshot missing: {snapshot_path}", file=sys.stderr)
        return 4
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    snapshot_id = str(snapshot.get("snapshot_id") or "?")
    if args.expect and not (snapshot_id == args.expect or snapshot_id.endswith(args.expect)):
        print(f"[FAIL] snapshot id is {snapshot_id}, expected {args.expect}", file=sys.stderr)
        return 4

    results = [classify(name, spec, snapshot)
               for name, spec in (snapshot.get("artifacts") or {}).items()]
    bad = [r for r in results if r["status"] in ("CONTENT_CHANGED", "MISSING")]
    meta = [r for r in results if r["status"] == "METADATA_ONLY"]
    payload = {
        "schema": "vett-r28-gate-j-snapshot-check/v1",
        "snapshot_id": snapshot_id,
        "snapshot_frozen_at_utc": snapshot.get("frozen_at_utc"),
        "snapshot_sha256": sha256_bytes(snapshot_path.read_bytes()),
        "artifacts": results,
        "summary": {"total": len(results),
                    "identical": sum(1 for r in results if r["status"] == "IDENTICAL"),
                    "metadata_only": len(meta),
                    "content_changed": len(bad),
                    "ok": not bad},
        "policy": (snapshot.get("reproducibility") or {}).get("note"),
        "content_digest_recipe": RECIPE,
        "volatile_paths": list(VOLATILE_PATHS),
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=1))
    else:
        print(f"snapshot       : {snapshot_id} (frozen {snapshot.get('frozen_at_utc')})")
        for r in results:
            extra = ""
            if r["status"] == "METADATA_ONLY":
                extra = f"  new byte sha256={r['actual_sha256'][:16]}…（内容摘要一致）"
            elif r["status"] == "CONTENT_CHANGED":
                extra = f"  actual={str(r.get('actual_sha256'))[:16]}… content={str(r.get('actual_content_sha256'))[:16]}…"
            print(f"  {r['status']:16s} {r['artifact']}{extra}")
        print(f"[{'ok' if not bad else 'FAIL'}] {len(results) - len(bad)}/{len(results)} artifacts "
              f"match {snapshot_id}（{len(meta)} 个属 metadata-only）")
    return 0 if not bad else 4


if __name__ == "__main__":
    raise SystemExit(main())
