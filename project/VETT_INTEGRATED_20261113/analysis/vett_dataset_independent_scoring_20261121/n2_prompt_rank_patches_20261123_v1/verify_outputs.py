from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def rows_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def rows_jsonl(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


manifest = json.loads((OUT / "VERSION_MANIFEST.json").read_text(encoding="utf-8"))
for x in manifest["generated_files"]:
    p = OUT / x["path"]
    assert p.stat().st_size == x["bytes"]
    assert sha_bytes(p.read_bytes()) == x["sha256"]

for x in rows_csv(OUT / "SOURCE_INVENTORY.csv"):
    p = ROOT / x["path"]
    assert p.stat().st_size == int(x["bytes"])
    assert sha_bytes(p.read_bytes()) == x["sha256"]

old_audit = rows_csv(OUT / "patch_01_oldvalue" / "private_scoring" / "N2_OLDVALUE_PROMPT_AUDIT.csv")
rank_audit = rows_csv(OUT / "patch_02_ranking" / "private_scoring" / "N2_RANKING_EVENT_CHECKLIST.csv")
rank_gold = rows_csv(OUT / "patch_02_ranking" / "private_scoring" / "N2_RANK_PAIR_GOLD.csv")
old_inputs = rows_jsonl(OUT / "patch_01_oldvalue" / "model_inputs" / "inputs.jsonl")
rank_inputs = rows_jsonl(OUT / "patch_02_ranking" / "model_inputs" / "inputs.jsonl")

assert len(old_audit) == 8 and len(rank_audit) == 8 and len(rank_gold) == 4
assert len(old_inputs) == 16 and len(rank_inputs) == 4
assert all(set(x) == {"sample_id", "prompt_sha256", "text_sha256", "prompt"} for x in old_inputs + rank_inputs)
assert all(sha_text(x["prompt"]) == x["prompt_sha256"] for x in old_inputs + rank_inputs)
assert all("gold" not in x and "condition" not in x for x in old_inputs + rank_inputs)

rank_by_id = {x["sample_id"]: x for x in rank_inputs}
facts = {
    "n2r-0008-b": "Evan Reed conceded 27 runs in the innings.",
    "n2r-0010-b": "Luke Barrett conceded 38 runs in the innings.",
}
for supplemented, fact in facts.items():
    original = supplemented[:-1] + "a"
    before = rank_by_id[original]["prompt"]
    after = rank_by_id[supplemented]["prompt"]
    assert fact not in before and after.count(fact) == 1
    assert after.replace(f"\n\n{fact}", "", 1) == before

verification = json.loads((OUT / "VERIFICATION.json").read_text(encoding="utf-8"))
assert verification["neutral_exact_scope_checks_passed"] is True
assert verification["model_input_rows_contain_gold_keys"] is False
assert verification["selection_experiment"]["answer_to_user_choice"] == "Connor"

print(
    json.dumps(
        {
            "status": "PASS",
            "manifest_files_verified": len(manifest["generated_files"]),
            "source_files_verified": len(rows_csv(OUT / "SOURCE_INVENTORY.csv")),
            "oldvalue_events": len(old_audit),
            "ranking_events": len(rank_audit),
            "model_inputs": len(old_inputs) + len(rank_inputs),
            "private_rows": len(old_audit) + len(rank_audit) + len(rank_gold),
            "rank_pair_diff_scope": "one exact inserted fact per supplemented prompt",
        },
        indent=2,
    )
)
