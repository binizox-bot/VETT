"""Re-audit blind packets against the **current frozen protocol** pattern table.

Used by t20 (fix verification) and t8 (independent re-check) to prove that the
PAMEND-003 pattern table really fires, and that existing packets are still clean.

    python reaudit_packets.py                     # t16 packet files (T1/T1-arm/T2)
    python reaudit_packets.py --glob "**/*packets*.jsonl" --root <dir>
    python reaudit_packets.py --json              # machine-readable
    python reaudit_packets.py --inject-selftest    # prove the table fires on R28 ids

Exit codes: 0 = clean (and self-test passed when requested), 4 = violations or self-test failure.
Read-only, no network, no model.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VERIFY_ROOT = HERE.parent
RUN_ROOT = VERIFY_ROOT.parent
sys.path.insert(0, str(RUN_ROOT / "02_design" / "scripts"))

import judge_protocol as jp  # noqa: E402

DEFAULT_ROOT = RUN_ROOT / "03_build" / "local" / "annotations" / "packets"
DATASET_PUBLIC = RUN_ROOT / "03_build" / "dataset_r28" / "public"
DEFAULT_FILES = ("T1_packets.jsonl", "T1_localarm_packets.jsonl", "T2_packets.jsonl")

INJECTIONS = (
    ("BP-R28-ID", {"passage": "item r28q_0001 says four"}),
    ("BP-R28-ID", {"span_text": "span r28fact_446afd688a87582ab949"}),
    ("BP-R28-ID", {"span_text": "rule r28rule_e2e38c24dc261b9ef56b"}),
    ("BP-R28-HELDOUT-ITEM", {"passage": "held-out twin r28h_0005"}),
    ("BP-R28-FAMILY", {"passage": "family rfam_83faedd9516b"}),
    ("BP-MATCH-ID", {"passage": "as in match_0021"}),
    ("BP-FAMILY", {"passage": "family L5_RUNOUT_LATER_BOUNDARY"}),
)


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def namespace_audit() -> dict:
    """Derive every measured R28 span prefix from the dataset and prove each is blocked.

    This is the guard against "rules that can never fire": PAMEND-003 listed 5 prefixes and
    missed 5 more; PAMEND-004 replaced the whitelist with a shape rule, and this audit is what
    keeps that honest on every run.
    """
    import re as _re
    samples: dict[str, str] = {}
    for path in sorted(DATASET_PUBLIC.glob("*/public_instance.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        for document in (doc.get("dossier") or {}).get("documents") or []:
            for span in document.get("spans") or []:
                sid = str(span.get("span_id") or "")
                m = _re.match(r"(r28[a-z]+)", sid)
                if m and m.group(1) not in samples:
                    samples[m.group(1)] = sid
    results: dict[str, str] = {}
    for prefix, sample in sorted(samples.items()):
        packet = _probe_packet("S1_span_topic", {"span_text": f"the span {sample} says four"})
        codes = {v["code"] for v in jp.audit_packet(packet)}
        results[prefix] = "BLOCKED" if "BP-R28-ID" in codes else f"MISSED({sorted(codes)})"
    # items / held-out items / families
    for label, text in (("r28q_item", "item r28q_0001"),
                        ("r28h_heldout", "twin r28h_0005"),
                        ("rfam_family", "family rfam_83faedd9516b")):
        codes = {v["code"] for v in jp.audit_packet(_probe_packet("T1_factor_visibility",
                                                                 {"passage": text}))}
        results[label] = "BLOCKED" if codes & {"BP-R28-ID", "BP-R28-HELDOUT-ITEM",
                                              "BP-R28-FAMILY"} else f"MISSED({sorted(codes)})"
    return results


def collect(root: Path, glob: str) -> list[Path]:
    return sorted(p for p in root.glob(glob) if p.is_file())


def audit(paths: list[Path]) -> dict:
    packets, violations = 0, []
    per_file = {}
    by_code: dict[str, int] = {}
    max_tokens = 0
    for path in paths:
        rows = load_jsonl(path)
        bad = 0
        for packet in rows:
            packets += 1
            max_tokens = max(max_tokens, int(packet.get("token_estimate") or 0))
            problems = jp.audit_packet(packet)
            if problems:
                bad += 1
                violations.append({"file": path.name, "packet_id": packet.get("packet_id"),
                                   "violations": problems})
                for problem in problems:
                    by_code[problem["code"]] = by_code.get(problem["code"], 0) + 1
        per_file[path.name] = {"packets": len(rows), "violations": bad}
    return {"packets": packets, "violations": violations, "per_file": per_file,
            "by_code": by_code, "max_token_estimate": max_tokens,
            "pattern_table": [p["id"] for p in jp.BLIND_FORBIDDEN_PATTERNS]}


def _probe_packet(task: str, payload: dict) -> dict:
    return {"schema_version": "vett-blind-packet/v1", "packet_id": "pkt_0123456789abcdef",
            "item_handle": "0123456789abcdef", "task": task, "ruler": "local",
            "prompt_template_version": "probe", "token_estimate": 9,
            "contains_answer": False, "payload": payload}


def self_test() -> dict:
    """Each injection must be blocked **by the named pattern**; a clean item must pass."""
    out = {}
    salt = "reaudit-selftest-salt-0123456789"
    for index, (expected, item) in enumerate(INJECTIONS):
        task = "S1_span_topic" if "span_text" in item else "T1_factor_visibility"
        codes = {v["code"] for v in jp.audit_packet(_probe_packet(task, dict(item)))}
        label = expected if expected not in out else f"{expected}#{index}"
        out[label] = "BLOCKED" if expected in codes else f"MISSING({sorted(codes)})"
    clean = jp.build_blind_packet({"passage": "Four runs were scored off the bat.",
                                   "instance_id": "i2"}, "T1_factor_visibility", salt)
    out["clean_packet"] = "PASS" if not jp.audit_packet(clean) else "VIOLATION"
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="re-audit blind packets with the frozen protocol")
    parser.add_argument("--root", default=str(DEFAULT_ROOT))
    parser.add_argument("--glob", default=None,
                        help="override the file set (default: t16 T1/T1-arm/T2 packet files)")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--inject-selftest", action="store_true",
                        help="prove the pattern table fires on real R28 id forms "
                             "(named-pattern injections + every measured span prefix)")
    args = parser.parse_args(argv)

    root = Path(args.root)
    if args.glob:
        paths = collect(root, args.glob)
    else:
        paths = [root / name for name in DEFAULT_FILES if (root / name).exists()]
    if not paths:
        print(f"[FAIL] no packet files under {root}", file=sys.stderr)
        return 4

    result = audit(paths)
    selftest = self_test() if args.inject_selftest else None
    namespace = namespace_audit() if args.inject_selftest else None
    selftest_ok = selftest is None or all(v in ("BLOCKED", "PASS") for v in selftest.values())
    namespace_ok = namespace is None or all(v == "BLOCKED" for v in namespace.values())
    clean = not result["violations"] and selftest_ok and namespace_ok
    if args.json:
        print(json.dumps({**result, "selftest": selftest, "namespace_audit": namespace,
                          "ok": clean}, ensure_ascii=False, indent=1))
    else:
        print(f"pattern table : {len(result['pattern_table'])} 条 -> {', '.join(result['pattern_table'])}")
        print(f"files         : {len(paths)}")
        print(f"packets       : {result['packets']}")
        print(f"violations    : {len(result['violations'])}")
        if result["by_code"]:
            print(f"by code       : {result['by_code']}")
        print(f"max tokens    : {result['max_token_estimate']}")
        if selftest:
            print("self-test     : " + ", ".join(f"{k}={v}" for k, v in selftest.items()))
        if namespace:
            missed = {k: v for k, v in namespace.items() if v != "BLOCKED"}
            print(f"namespace     : {len(namespace) - len(missed)}/{len(namespace)} blocked"
                  + (f"  MISSED={missed}" if missed else ""))
        print(f"[{'ok' if clean else 'FAIL'}] re-audit")
    return 0 if clean else 4


if __name__ == "__main__":
    raise SystemExit(main())
