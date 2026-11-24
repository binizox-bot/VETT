import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read_csv(name):
    with (HERE / name).open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def as_bool(value):
    return str(value).casefold() == "true"


def sha_file(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


rows = read_csv("N2_12_CASES.csv")
answerability = read_csv("N2_4ROOT_ANSWERABILITY.csv")
fields = read_csv("FIELD_REGRESSION_ALL24.csv")
sources = read_csv("SOURCE_INVENTORY.csv")
summary = json.loads((HERE / "SUMMARY.json").read_text(encoding="utf-8"))

assert len(rows) == 12
assert len({r["match"] for r in rows}) == 4
assert len({r["model"] for r in rows}) == 3
assert len(answerability) == 4
assert [r["match"] for r in answerability if as_bool(r["model_visible_top2_unique"])] == ["match_0096"]
assert sum(as_bool(r["model_visible_top2_unique"]) for r in rows) == 3

correct_lists = [r for r in rows if r["list_member_set_oracle"] == "correct"]
assert len(correct_lists) == 6
assert sum(as_bool(r["oracle_correct_list_then_hint_lost_person"]) for r in correct_lists) == 0
assert sum(as_bool(r["oracle_correct_list_then_hint_kept_two_wrong_number"]) for r in correct_lists) == 6
assert sum(as_bool(r["oracle_correct_list_then_hint_only_team_total_wrong"]) for r in correct_lists) == 0
assert sum(r["hint_team_total_status"] == "correct" for r in correct_lists) == 6

assert len(fields) == 24 * 43
reported = [r for r in fields if as_bool(r["reported_45_direct_to_hint_regression"])]
v4_reg = [r for r in fields if as_bool(r["v4_direct_to_hint_regression"])]
v4_gain = [r for r in fields if as_bool(r["v4_direct_to_hint_gain"])]
assert len(reported) == 45
assert len(v4_reg) == 31
assert len(v4_gain) == 38
assert sum(as_bool(r["hint_empty_or_unrecoverable"]) for r in reported) == 0
assert Counter(r["hint_recovery_source"] for r in reported) == {"strict_json": 19, "token_recovery": 15, "fenced_json": 11}

assert summary["core8_vs_fair6"]["core8_rows"] == 24
assert summary["core8_vs_fair6"]["fair6_rows"] == 18
assert summary["core8_vs_fair6"]["excluded_rows"] == 6
assert summary["core8_vs_fair6"]["core8_oracle_directions"]["both_member_sets_wrong_or_undetermined"] == 8
assert summary["core8_vs_fair6"]["fair6_directions"]["both_member_sets_wrong_or_undetermined"] == 2

root = HERE.parents[3]
for item in sources:
    path = root / item["path"]
    assert path.is_file(), path
    assert sha_file(path) == item["sha256"], path
    assert path.stat().st_size == int(item["bytes"]), path

manifest_path = HERE / "VERSION_MANIFEST.json"
if manifest_path.exists():
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["status"] == "frozen_v1"
    for item in manifest["generated_files"]:
        path = HERE / item["path"]
        assert path.is_file(), path
        assert sha_file(path) == item["sha256"], path
        assert path.stat().st_size == item["bytes"], path

print(json.dumps({
    "status": "PASS",
    "n2_rows": len(rows),
    "answerable_roots": 1,
    "fair_rows": 3,
    "oracle_correct_lists": len(correct_lists),
    "reported_regressions": len(reported),
    "v4_recovery_regressions": len(v4_reg),
    "v4_recovery_gains": len(v4_gain),
}, ensure_ascii=False, indent=2))
