from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csv_rows(name: str) -> list[dict]:
    with (HERE / name).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


manifest = json.loads((HERE / "VERSION_MANIFEST.json").read_text(encoding="utf-8"))
for x in manifest["generated_files"]:
    p = HERE / x["path"]
    assert p.stat().st_size == x["bytes"]
    assert sha(p) == x["sha256"]

for x in csv_rows("SOURCE_INVENTORY.csv"):
    p = ROOT / x["path"]
    assert p.stat().st_size == int(x["bytes"])
    assert sha(p) == x["sha256"]

chain = csv_rows("TOP2_CHAIN_ROWS.csv")
answer = csv_rows("TOP2_ANSWERABILITY.csv")
summary = csv_rows("TOP2_CHAIN_SUMMARY.csv")
b256 = csv_rows("B256_LINE_REVIEW.csv")
b256_summary = csv_rows("B256_MODEL_SUMMARY.csv")

assert len(chain) == 72 and len(answer) == 24 and len(b256) == 48 and len(b256_summary) == 6
assert len({(r["match"], r["model"], r["notification"]) for r in chain}) == 72
assert all(r["top2_batch"] in ("B254", "B255") for r in chain)
assert all(r["partial_batch"] == ("B253" if r["notification"] == "N0" else "B248") for r in chain)
assert all(r["fulltable_batch"] == ("B247" if r["notification"] == "N0" else f"B{228 + ['match_0003','match_0008','match_0010','match_0012','match_0015','match_0017','match_0026','match_0030'].index(r['match'])}") for r in chain)

comparable = [r for r in chain if r["input_top2_determinable"] == "True"]
assert len(comparable) == 36
by_arm = Counter(r["notification"] for r in comparable)
assert by_arm == {"N0": 9, "N1": 9, "N2": 18}
forward = {r["match"] for r in comparable if r["member_set_comparison_direction"] == "top2_correct_fulltable_wrong"}
reverse = {r["match"] for r in comparable if r["member_set_comparison_direction"] == "top2_wrong_fulltable_correct"}
assert forward == {"match_0003", "match_0008", "match_0012", "match_0017", "match_0026", "match_0030"}
assert reverse == {"match_0003"}

for match in ("match_0008", "match_0010"):
    rows = [r for r in chain if r["match"] == match and r["notification"] == "N2"]
    assert len(rows) == 3
    assert all(r["named_A_in_legal_top2"] == "False" for r in rows)
    assert all(r["member_set_comparison_direction"] == "not_comparable_input" for r in rows)

assert all(sum(int(r[x]) for x in ("fully_old", "fully_new", "only_original_minus1", "only_new_plus1", "other_values", "unrecoverable")) == 8 for r in b256_summary)
gemma_full = next(r for r in b256_summary if r["model"] == "Gemma" and r["input_arm"] == "N2_F")
assert (gemma_full["fully_old"], gemma_full["fully_new"], gemma_full["only_new_plus1"]) == ("0", "6", "2")

print(json.dumps({
    "status": "PASS",
    "generated_hashes_verified": len(manifest["generated_files"]),
    "source_hashes_verified": len(csv_rows("SOURCE_INVENTORY.csv")),
    "chain_rows": len(chain),
    "comparable_rows": len(comparable),
    "forward_independent_roots": len(forward),
    "reverse_independent_roots": len(reverse),
    "b256_rows": len(b256),
}, indent=2))
