"""Recompute the 04_verify gate content hash — standalone, one command, no imports from j_gate.

The captain's rule: **an invariant that others cannot recompute must not enter an acceptance
checklist.**  So the recipe is spelled out here twice — once in prose (``--recipe``), once as
an independent implementation — and the tool is deliberately *not* importing
``verify_snapshot.py``: if two independent implementations agree, the recipe is followable.

    python recompute_content_hash.py                 # prints the digest + the steps it took
    python recompute_content_hash.py --recipe        # prints only the algorithm
    python recompute_content_hash.py --file X.json    # any gate JSON with the same shape
    python recompute_content_hash.py --compare A B    # two files -> equal / differ

Algorithm (vett-gate-content-digest/v2)
---------------------------------------
1. read the JSON file;
2. delete exactly these keys (dotted paths):
       generated_at_utc
       protocol_precondition.evidence.verify_checked_at_utc
       items.J0_protocol_precondition.evidence.verify_checked_at_utc
   (the J0 evidence block is emitted twice; both copies carry the upstream verifier's
   timestamp, which changes on every `protocol_verify.py --check`);
3. serialise with ``json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))``
   — UTF-8, keys sorted, **compact** separators, no trailing newline;
4. SHA-256 over the UTF-8 bytes of that string.

Exit codes: 0 = printed / equal, 4 = compare mismatch or unreadable input.
Standard library only, read-only, no network.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VERIFY_ROOT = HERE.parent
DEFAULT_FILE = VERIFY_ROOT / "J_GATE.json"

VOLATILE_PATHS = (
    "generated_at_utc",
    "protocol_precondition.evidence.verify_checked_at_utc",
    "items.J0_protocol_precondition.evidence.verify_checked_at_utc",
)

RECIPE = """vett-gate-content-digest/v2
1) 读取 JSON
2) 删除（点号路径，逐层下钻，仅当父对象存在时删除）：
     generated_at_utc
     protocol_precondition.evidence.verify_checked_at_utc
     items.J0_protocol_precondition.evidence.verify_checked_at_utc
3) 序列化：json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
   —— UTF-8、键升序、紧凑分隔符、无尾随换行
4) 对上述字符串的 UTF-8 字节做 SHA-256
排除项说明：三个时间戳都是"元数据"，其中两个来自上游 protocol_verify 的运行时刻。
artifacts/verdicts/evidence 的数字与结构**全部参与**哈希（不做任何归一化）。"""


def strip_paths(doc: object, paths: tuple[str, ...] = VOLATILE_PATHS) -> object:
    """Independent implementation of step 2 (deep copy, no shared helpers)."""
    text = json.dumps(doc)                      # cheap deep copy
    body = json.loads(text)
    for path in paths:
        parts = path.split(".")
        node = body
        ok = True
        for part in parts[:-1]:
            if isinstance(node, dict) and part in node:
                node = node[part]
            else:
                ok = False
                break
        if ok and isinstance(node, dict):
            node.pop(parts[-1], None)
    return body


def content_hash(doc: object) -> str:
    body = strip_paths(doc)
    text = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="recompute the gate content hash (recipe v2)")
    parser.add_argument("--file", default=str(DEFAULT_FILE))
    parser.add_argument("--recipe", action="store_true")
    parser.add_argument("--compare", nargs=2, default=None)
    args = parser.parse_args(argv)

    if args.recipe:
        print(RECIPE)
        print("volatile_paths:", list(VOLATILE_PATHS))
        return 0

    if args.compare:
        first, second = (Path(x) for x in args.compare)
        try:
            a, b = content_hash(load(first)), content_hash(load(second))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[FAIL] {exc}", file=sys.stderr)
            return 4
        same = a == b
        print(f"A {first}  {a}")
        print(f"B {second}  {b}")
        print(f"[{'ok' if same else 'FAIL'}] content {'EQUAL (metadata-only change)' if same else 'DIFFERS (content change)'}")
        return 0 if same else 4

    path = Path(args.file)
    try:
        doc = load(path)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        return 4
    digest = content_hash(doc)
    print(RECIPE)
    print(f"file    : {path}")
    print(f"digest  : {digest}")
    print(f"stripped: {list(VOLATILE_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
