from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE = HERE.parent
FROZEN = BASE / "v1_frozen"
DSH = BASE / "run_dsh_v1"


def find_workspace() -> Path:
    for p in HERE.parents:
        if (p / "Self-cricket-clean_text_scorecard_v1_220_matches").is_dir() and (p / "VETT_INTEGRATED_20261113").is_dir():
            return p
    raise RuntimeError("workspace root not found")


ROOT = find_workspace()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        fieldnames = list(rows[0]) if rows else []
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def load_source_record(source_file: str, source_line: int, cache: dict[str, list[str]]) -> dict:
    if source_file not in cache:
        cache[source_file] = (ROOT / source_file).read_text(encoding="utf-8").splitlines()
    return json.loads(cache[source_file][source_line - 1])


def pick_two_bowlers(cells: dict) -> tuple[str, str]:
    keys = [k for k in cells if k.endswith("_wickets") and k != "innings_total_wickets"]
    if len(keys) != 2:
        raise AssertionError(f"expected two bowler wicket fields, got {keys}")
    return keys[0][:-8], keys[1][:-8]


def val(cells: dict, field: str, part: str = "pred"):
    return cells.get(field, {}).get(part)


def classify(old_a, old_b, correct_a, correct_b, pred_a, pred_b) -> tuple[str, str]:
    if pred_a is None or pred_b is None:
        return "information_insufficient", "信息不足"
    if pred_a == old_a and pred_b == old_b:
        return "old_values_retained", "沿用旧值"
    if pred_a == correct_a and pred_b == old_b:
        return "only_original_bowler_changed", "只改原投手"
    if pred_a == old_a and pred_b == correct_b:
        return "only_new_bowler_changed", "只改新投手"
    if pred_a == old_a + 1 and pred_b == old_b - 1:
        return "direction_reversed", "方向反转"
    return "other_wrong_value", "其他错值"


hist_path = FROZEN / "historical_line_scores.csv"
with hist_path.open("r", encoding="utf-8-sig", newline="") as f:
    hist = list(csv.DictReader(f))

failures = [r for r in hist if r["condition"] == "C_change" and r["new_task_correct"] == "False"]
assert len(failures) == 12, len(failures)

line_cache: dict[str, list[str]] = {}
hist_record: dict[tuple[str, str, str], dict] = {}
hist_row: dict[tuple[str, str, str], dict] = {}
for r in hist:
    key = (r["event_id"], r["model"], r["condition"])
    hist_row[key] = r
    hist_record[key] = load_source_record(r["source_file"], int(r["source_line"]), line_cache)

model_order = {"gemma2:9b": 0, "llama3.1:8b": 1, "qwen2.5:7b-instruct-q4_K_M": 2}
failure_rows: list[dict] = []
raw_links: list[dict] = []

for r in failures:
    event = r["event_id"]
    model = r["model"]
    change = hist_record[(event, model, "C_change")]
    maintain = hist_record[(event, model, "C_maintain")]
    cells = change["score"]["cells"]
    old_cells = maintain["score"]["cells"]
    a, b = pick_two_bowlers(cells)
    aw, ar = f"{a}_wickets", f"{a}_runs"
    bw, br = f"{b}_wickets", f"{b}_runs"
    total = "innings_total_wickets"
    old_a, old_b = val(old_cells, aw, "gold"), val(old_cells, bw, "gold")
    correct_a, correct_b = val(cells, aw, "gold"), val(cells, bw, "gold")
    pred_a, pred_b = val(cells, aw), val(cells, bw)
    category_code, category = classify(old_a, old_b, correct_a, correct_b, pred_a, pred_b)

    correct_candidates = [
        x for x in hist
        if x["event_id"] == event and x["condition"] == "C_change" and x["new_task_correct"] == "True"
    ]
    correct_candidates.sort(key=lambda x: model_order.get(x["model"], 99))
    contrast = correct_candidates[0] if correct_candidates else None
    contrast_record = None
    if contrast:
        contrast_record = load_source_record(contrast["source_file"], int(contrast["source_line"]), line_cache)
    contrast_cells = contrast_record["score"]["cells"] if contrast_record else {}

    row = {
        "batch_id": r["batch_id"],
        "match_root": r["match_root"],
        "innings": change.get("innings"),
        "event_id": event,
        "model": model,
        "original_bowler": a,
        "new_bowler": b,
        "original_old_wickets": old_a,
        "original_old_runs": val(old_cells, ar, "gold"),
        "new_old_wickets": old_b,
        "new_old_runs": val(old_cells, br, "gold"),
        "original_correct_wickets": correct_a,
        "original_correct_runs": val(cells, ar, "gold"),
        "new_correct_wickets": correct_b,
        "new_correct_runs": val(cells, br, "gold"),
        "original_pred_wickets": pred_a,
        "original_pred_runs": val(cells, ar),
        "new_pred_wickets": pred_b,
        "new_pred_runs": val(cells, br),
        "innings_total_old": val(old_cells, total, "gold"),
        "innings_total_correct": val(cells, total, "gold"),
        "innings_total_pred": val(cells, total),
        "observable_category_code": category_code,
        "observable_category": category,
        "causal_explanation": "uncertain_from_single_output",
        "correct_contrast_model": contrast["model"] if contrast else "",
        "correct_contrast_original_wickets": val(contrast_cells, aw) if contrast else "",
        "correct_contrast_original_runs": val(contrast_cells, ar) if contrast else "",
        "correct_contrast_new_wickets": val(contrast_cells, bw) if contrast else "",
        "correct_contrast_new_runs": val(contrast_cells, br) if contrast else "",
        "correct_contrast_total": val(contrast_cells, total) if contrast else "",
        "correct_contrast_source_file": contrast["source_file"] if contrast else "",
        "correct_contrast_source_line": int(contrast["source_line"]) if contrast else "",
        "task_key": change.get("task_key", ""),
        "input_version": change.get("input_version", ""),
        "prompt_version": change.get("prompt_version", ""),
        "text_sha256": change.get("text_sha256", ""),
        "prompt_sha256": change.get("prompt_sha256", ""),
        "model_digest": change.get("model_digest", ""),
        "decode_json": json.dumps(change.get("decode", {}), ensure_ascii=False, sort_keys=True),
        "source_file": r["source_file"],
        "source_line": int(r["source_line"]),
        "raw_output_sha256": r["raw_output_sha256"],
        "raw_output_hash_verified": hashlib.sha256(change.get("raw_output", "").encode("utf-8")).hexdigest() == r["raw_output_sha256"],
        "raw_output": change.get("raw_output", ""),
    }
    failure_rows.append(row)
    raw_links.append({
        "event_id": event,
        "match_root": r["match_root"],
        "model": model,
        "source_file": r["source_file"],
        "source_line": int(r["source_line"]),
        "raw_output_sha256": r["raw_output_sha256"],
        "raw_output": change.get("raw_output", ""),
        "parsed": change.get("parsed"),
        "score": change.get("score"),
    })

failure_rows.sort(key=lambda x: (x["match_root"], model_order.get(x["model"], 99)))
write_csv(HERE / "formal_change_failures_12.csv", failure_rows)
write_jsonl(HERE / "historical_failure_raw_links.jsonl", raw_links)

category_defs = [
    ("old_values_retained", "沿用旧值"),
    ("only_original_bowler_changed", "只改原投手"),
    ("only_new_bowler_changed", "只改新投手"),
    ("direction_reversed", "方向反转"),
    ("other_wrong_value", "其他错值"),
    ("information_insufficient", "信息不足"),
]
category_rows: list[dict] = []
for code, label in category_defs:
    group = [x for x in failure_rows if x["observable_category_code"] == code]
    roots = sorted({x["match_root"] for x in group})
    models = sorted({x["model"] for x in group}, key=lambda x: model_order.get(x, 99))
    contrasts = []
    for root in roots:
        x = next(y for y in group if y["match_root"] == root)
        if x["correct_contrast_model"]:
            contrasts.append(f"{root}:{x['correct_contrast_model']}")
    category_rows.append({
        "observable_category_code": code,
        "observable_category": label,
        "failure_rows": len(group),
        "independent_match_roots": len(roots),
        "match_roots": ";".join(roots),
        "models": ";".join(models),
        "same_event_correct_contrasts": ";".join(contrasts),
    })
write_csv(HERE / "failure_category_summary.csv", category_rows)

# Independently scored DSH batch, produced by invoking the frozen scorer with -B and output outside v1_frozen.
ind_scores = read_jsonl(HERE / "dsh_scores_independent.jsonl")
dsh_scores = read_jsonl(DSH / "scores.jsonl")
dsh_raw = read_jsonl(DSH / "raw.jsonl")
gold = {x["sample_id"]: x for x in read_jsonl(FROZEN / "private_gold.jsonl")}
inputs = {x["sample_id"]: x for x in read_jsonl(FROZEN / "model_inputs.jsonl")}
dsh_scores_by_key = {(x["sample_id"], x["model"]): x for x in dsh_scores}

score_comparison: list[dict] = []
for x in ind_scores:
    key = (x["sample_id"], x["model"])
    y = dsh_scores_by_key.get(key)
    exact = y is not None and json.dumps(x, sort_keys=True, ensure_ascii=False) == json.dumps(y, sort_keys=True, ensure_ascii=False)
    g = gold[x["sample_id"]]
    score_comparison.append({
        "sample_id": x["sample_id"],
        "match_root": g["match_root"],
        "condition_code": g["condition_code"],
        "condition_semantics": g["condition_semantics"],
        "model": x["model"],
        "independent_executable": x["executable"],
        "independent_task_correct": x["task_correct"],
        "independent_correct_fields": x["correct_fields"],
        "independent_total_fields": x["total_fields"],
        "dsh_score_present": y is not None,
        "dsh_task_correct": y.get("task_correct") if y else "",
        "exact_record_match": exact,
    })
score_comparison.sort(key=lambda x: (x["sample_id"], model_order.get(x["model"], 99)))
write_csv(HERE / "dsh_score_comparison.csv", score_comparison)

by_model_sample = {(x["model"], x["sample_id"]): x for x in ind_scores}
models = sorted({x["model"] for x in ind_scores}, key=lambda x: model_order.get(x, 99))
long_transitions = []
triplets = []
for model in models:
    full = by_model_sample[(model, "vett-dev-v1-0001-c00")]
    window = by_model_sample[(model, "vett-dev-v1-0001-c01")]
    long_transitions.append({
        "model": model,
        "full_correct": full["task_correct"],
        "window_correct": window["task_correct"],
        "transition": ("wrong_to_right" if not full["task_correct"] and window["task_correct"] else
                       "right_to_wrong" if full["task_correct"] and not window["task_correct"] else
                       "right_to_right" if full["task_correct"] and window["task_correct"] else "wrong_to_wrong"),
    })
    change = by_model_sample[(model, "vett-dev-v1-0002-c10")]
    maintain = by_model_sample[(model, "vett-dev-v1-0002-c11")]
    no_notice = by_model_sample[(model, "vett-dev-v1-0002-c12")]
    triplets.append({
        "model": model,
        "change_correct": change["task_correct"],
        "maintain_correct": maintain["task_correct"],
        "no_notice_correct": no_notice["task_correct"],
        "change_and_maintain_correct": change["task_correct"] and maintain["task_correct"],
        "unexecutable_count": sum(not z["executable"] for z in (change, maintain, no_notice)),
    })
write_csv(HERE / "dsh_full_window_transitions.csv", long_transitions)
write_csv(HERE / "dsh_attribution_triplets.csv", triplets)

raw_keys = [(x["sample_id"], x["model"]) for x in dsh_raw]
prompt_hash_mismatch = [
    f"{x['sample_id']}|{x['model']}" for x in dsh_raw
    if x.get("prompt_sha256") != inputs[x["sample_id"]]["prompt_sha256"]
]
settings_by_model = defaultdict(set)
for x in dsh_raw:
    d = x["decode"]
    settings_by_model[x["model"]].add((x.get("model_digest"), d.get("temperature"), d.get("seed"), d.get("num_ctx"), d.get("num_predict")))

summary = {
    "raw_rows": len(dsh_raw),
    "expected_rows": 15,
    "unique_request_keys": len(set(raw_keys)),
    "duplicate_request_keys": len(raw_keys) - len(set(raw_keys)),
    "prompt_hash_mismatches": prompt_hash_mismatch,
    "settings_variants_per_model": {k: len(v) for k, v in sorted(settings_by_model.items())},
    "independent_score_rows": len(ind_scores),
    "independent_executable": sum(bool(x["executable"]) for x in ind_scores),
    "independent_task_correct": sum(bool(x["task_correct"]) for x in ind_scores),
    "dsh_score_exact_record_matches": sum(bool(x["exact_record_match"]) for x in score_comparison),
    "dsh_score_record_differences": sum(not bool(x["exact_record_match"]) for x in score_comparison),
    "formal_reassignment_correct": sum(x["change_correct"] for x in triplets),
    "maintain_correct": sum(x["maintain_correct"] for x in triplets),
    "no_notice_correct": sum(x["no_notice_correct"] for x in triplets),
    "change_and_maintain_correct": sum(x["change_and_maintain_correct"] for x in triplets),
    "actual_mistransfer": 0,
    "unexecutable": sum(x["unexecutable_count"] for x in triplets),
    "full_to_window_wrong_to_right": sum(x["transition"] == "wrong_to_right" for x in long_transitions),
    "full_to_window_right_to_wrong": sum(x["transition"] == "right_to_wrong" for x in long_transitions),
    "full_to_window_right_to_right": sum(x["transition"] == "right_to_right" for x in long_transitions),
}
(HERE / "dsh_first_batch_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# Evidence and provenance checks for the strongest linked historical failure.
scorecard = ROOT / "Self-cricket-clean_text_scorecard_v1_220_matches/match_0003/scorecard.md"
commentary = ROOT / "Self-cricket-clean_text_scorecard_v1_220_matches/match_0003/commentary.txt"
commentary_text = commentary.read_text(encoding="utf-8")
evidence_records = [x for x in read_jsonl(FROZEN / "evidence_chain.jsonl") if x["sample_id"] == "vett-dev-v1-0002-c10"]
assert len(evidence_records) == 1
ev = evidence_records[0]
historical_case = next(x for x in failure_rows if x["match_root"] == "match_0003")
historical_raw = next(x for x in raw_links if x["match_root"] == "match_0003")
historical_prompt_record = hist_record[("match_0003.inn1.attribution", historical_case["model"], "C_change")]
historical_batch = json.loads((ROOT / "VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117/batches/B019.json").read_text(encoding="utf-8"))
hist_task = next(t for t in historical_batch["tasks"] if t["task_key"] == historical_prompt_record["task_key"])
hist_record_text = hist_task["prompt"].split("Record:\n", 1)[1].rsplit("\n\nJSON:", 1)[0]

frozen_prompt = inputs["vett-dev-v1-0002-c10"]["prompt"]
frozen_record_text = frozen_prompt.split("Record:\n", 1)[1].rsplit("\n\nJSON:", 1)[0]
controlled_sentences = [x["quote"] for x in ev["evidence_sentences"]]
exact_sentence_matches = {s: s in commentary_text for s in controlled_sentences}

field_map_path = ROOT / "VETT_INTEGRATED_20261113/analysis/answerability_and_short_evidence/FIELD_ANSWERABILITY_V2.jsonl"
field_map_rows = [
    x for x in read_jsonl(field_map_path)
    if x.get("match") == "match_0003" and x.get("field") in {
        "inn1.bowl1_name", "inn1.bowl1_wickets", "inn1.bowl1_runs",
        "inn1.bowl2_name", "inn1.bowl2_wickets", "inn1.bowl2_runs",
    }
]
field_map_rows.sort(key=lambda x: x["field"])
write_jsonl(HERE / "match_0003_full_table_field_mapping.jsonl", field_map_rows)

source_checks = {
    "classification": "local_controlled_edit_from_scorecard",
    "published_original": False,
    "local_controlled_edit": True,
    "rerender": False,
    "match_root_only_mapping": False,
    "controlled_sentences_exactly_in_published_commentary": exact_sentence_matches,
    "historical_record_text": hist_record_text,
    "frozen_record_text": frozen_record_text,
    "scorecard_sha256": sha256(scorecard),
    "commentary_sha256": sha256(commentary),
}
(HERE / "match_0003_provenance_check.json").write_text(json.dumps(source_checks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# Next pair selection, based on the frozen screening table plus observed failure shape.
next_pair = [
    {
        "match_root": "match_0008",
        "role": "attribution_difficulty",
        "priority_basis": "uncovered old-value direction: equal old wickets",
        "old_values": "Luke Barrett 3/30; Ryan Frost 3/37; innings total 10",
        "formal_target": "Luke Barrett 2/30; Ryan Frost 4/37; innings total 10",
        "historical_note": "all three historical models answered the formal-change arm correctly; use as a contrast to the destination-overvalue failures",
        "pre_freeze_requirement": "recheck same-event three arms, scorecard cells, prompt hashes, and no tail-summary conflict",
    },
    {
        "match_root": "match_0180",
        "role": "ordinary_long_evidence",
        "priority_basis": "fixed-seed ordinary root with dense competing score checkpoints",
        "old_values": "not an attribution case",
        "formal_target": "published innings close 327/6; evidence window still to be frozen",
        "historical_note": "commentary contains at least six score checkpoints (87/2, 199/3, 327/6, 25/2, 110/5, 129 all out)",
        "pre_freeze_requirement": "extract verbatim final-sentence window, verify offsets/hash, and run full/window scorer self-test",
    },
]
write_csv(HERE / "next_development_pair.csv", next_pair)

# Human-readable reports.
failure_md = [
    "# 正式改判失败：12 条逐行复核",
    "",
    "筛选规则：`historical_line_scores.csv` 中 `condition=C_change` 且 `new_task_correct=False`。共 12 条，均已按 `source_file + source_line` 回到 B019/B022 原始回答。分类只描述可观察输出，不把单次输出解释为内部原因。",
    "",
    "| 比赛 | 模型 | 旧值（原→新投手） | 正确新值 | 模型值 | 全队 wickets 旧/正确/模型 | 分类 | 同事件正确对照 |",
    "| --- | --- | --- | --- | --- | --- | --- | --- |",
]
for x in failure_rows:
    failure_md.append(
        f"| {x['match_root']} | {x['model']} | {x['original_bowler']} {x['original_old_wickets']}/{x['original_old_runs']} → {x['new_bowler']} {x['new_old_wickets']}/{x['new_old_runs']} | "
        f"{x['original_correct_wickets']}/{x['original_correct_runs']} → {x['new_correct_wickets']}/{x['new_correct_runs']} | "
        f"{x['original_pred_wickets']}/{x['original_pred_runs']} → {x['new_pred_wickets']}/{x['new_pred_runs']} | "
        f"{x['innings_total_old']}/{x['innings_total_correct']}/{x['innings_total_pred']} | {x['observable_category']} | {x['correct_contrast_model']} |"
    )
failure_md += [
    "",
    "## 分类汇总",
    "",
    "| 分类 | 失败条数 | 独立比赛根 | 模型 |",
    "| --- | ---: | ---: | --- |",
]
for x in category_rows:
    failure_md.append(f"| {x['observable_category']} | {x['failure_rows']} | {x['independent_match_roots']} | {x['models'] or '—'} |")
failure_md += [
    "",
    "可观察到的集中形态：11 条“其他错值”全部把新投手 wickets 报得高于正确值，其中 10 条高 1、`match_0017` 高 2；9/11 同时把原投手正确减 1。剩余 1 条（`match_0003` Qwen）正确增加新投手，却沿用原投手旧值。该形态支持设计对照题，不足以单独判断模型为什么这样算。",
    "",
    "逐行值、原始输出、哈希和行号见 `formal_change_failures_12.csv`；原始回答的结构化副本见 `historical_failure_raw_links.jsonl`。",
]
(HERE / "FAILURE_ANALYSIS.md").write_text("\n".join(failure_md) + "\n", encoding="utf-8")

evidence_md = f"""# match_0003 失败案例与输入来源

## 历史失败

- 失败行：`{historical_case['source_file']}:{historical_case['source_line']}`，模型 `{historical_case['model']}`。
- 历史模型实际回答：Evan Clarke `{historical_case['original_pred_wickets']}/{historical_case['original_pred_runs']}`，Connor Reed `{historical_case['new_pred_wickets']}/{historical_case['new_pred_runs']}`，全队 wickets `{historical_case['innings_total_pred']}`。
- 正确值：Evan Clarke `3/28`，Connor Reed `2/28`，全队 wickets `8`。
- 可观察分类：只改新投手。单次输出不能区分是漏减、复制旧值还是其他机制，原因保持不确定。

历史输入原句：

> {hist_record_text}

正文没有直接写出最终数对 `3/28`、`2/28`。它写出旧值，再给一次从 Evan Clarke 到 Connor Reed 的改判；必须跨句执行 Evan `4→3`、Connor `1→2`，runs 与全队 wickets 保持。

## 同源整表字段

两个投手都能回到同一份 `match_0003/scorecard.md`：

- 第 43 行 Evan Clarke bowling 行：`R=28, W=4`；整表字段 `inn1.bowl1_name / inn1.bowl1_runs / inn1.bowl1_wickets`。
- 第 46 行 Connor Reed bowling 行：`R=28, W=1`；整表字段 `inn1.bowl2_name / inn1.bowl2_runs / inn1.bowl2_wickets`。
- 第 28 行 Brandon Hale dismissal：`c Mason Cooper b Evan Clarke`；第 14 行 innings total：`164/8 (20.0 Overs)`。

改判后若更新同一整表，Evan 仍是 bowl1（3/28），Connor 仍是 bowl2（2/28），所以不会因排序改变而换字段。字段映射原始记录见 `match_0003_full_table_field_mapping.jsonl`。

## 本轮冻结输入来源判定

判定：**局部受控编辑**。不是发布版长文原句相同，不是重渲染，也不是仅同场映射。

- 发布版长文只以叙事方式写 Brandon 原先归 Clarke，例如：“Brandon followed soon after, again to Clarke, again with Cooper involved, and suddenly Brookmere were 17 for 2 ...”。
- 本轮冻结输入把同一 scorecard 的出局行、两条 bowling 行和 innings total 合成旧值句，再加入三种受控通知。三个受控句逐字都不出现在发布版 commentary。
- 它不是“仅比赛根映射”，因为可以精确回到 scorecard 第 28、43、46、14 行和上述整表字段。

当前 frozen `c10` 原句：

> {frozen_record_text}

通知语义仍沿用冻结交付的 `pending_human_review` 状态。
"""
(HERE / "MATCH_0003_EVIDENCE_AND_PROVENANCE.md").write_text(evidence_md, encoding="utf-8")

dsh_md = f"""# DSH 首批独立评分

- 原始回答：15/15 到齐，无重复键；每个模型 5 条。
- 提示哈希：15/15 与冻结 `model_inputs.jsonl` 匹配。
- 可比设置：每个模型只有 1 组 digest、temperature、seed、num_ctx、num_predict。
- 独立评分：15/15 可执行，15/15 整题正确。
- DSH 自带 `scores.jsonl` 对照：15/15 记录逐字段完全相同，差异 0。
- 归属三臂：正式改判 3/3，维持 3/3，无通知 3/3；改判与维持同时正确 3/3；实际误转移 0，不可执行 0。
- 长文全文/窗口：3 个模型均对→对；错→对 0，对→错 0。

这批结果与历史 `match_0003` Qwen 失败不构成同一输入复现：本轮使用新的冻结样本 ID、输入版本和 prompt/text hash。可以说明当前冻结输入在三模型上通过，不能据此把历史失败抹去。

逐行独立分数见 `dsh_scores_independent.jsonl`；与 DSH 分数的逐行对照见 `dsh_score_comparison.csv`。
"""
(HERE / "DSH_FIRST_BATCH_INDEPENDENT_SCORE.md").write_text(dsh_md, encoding="utf-8")

next_md = """# 下一对开发根

1. `match_0008`：归属难度根。旧 wickets 为 3/3，补“旧值相等”的方向覆盖。历史三模型正式改判都答对，可作为本轮 11 条新投手过量记账失败的成功对照。下一版仍须重新核对三臂、来源格、哈希和尾部冲突。
2. `match_0180`：普通长文根。固定种子候选，正文至少有 87/2、199/3、327/6、25/2、110/5、129 all out 六个比分检查点，适合补事件密度和竞争比分。尚未冻结证据窗口，先做逐字窗口、偏移/哈希和全文-窗口自测。

不优先 `match_0010/0012/0015/0030`：它们强化低旧值或格式边界，但本轮 11 条“其他错值”已覆盖这些根，新增方向小于 3/3 相等旧值。`match_0017/0026` 继续保留为错误复核材料，不占下一对；`match_0026` 的相等 runs 不补 wickets 方向。
"""
(HERE / "NEXT_DEV_PAIR.md").write_text(next_md, encoding="utf-8")

readme = """# v2 failure analysis

本目录是 `v1_frozen` 的只读后续分析。没有修改冻结输入、金标、评分器或清单。

- `FAILURE_ANALYSIS.md`：12 条历史正式改判失败与分类。
- `formal_change_failures_12.csv`：逐比赛、模型、旧值、正确值、实际值、全队数和正确对照。
- `MATCH_0003_EVIDENCE_AND_PROVENANCE.md`：最完整失败案例、整表字段和输入来源判定。
- `DSH_FIRST_BATCH_INDEPENDENT_SCORE.md`：DSH 首批独立评分。
- `NEXT_DEV_PAIR.md`：下一对开发根。
- `verification.json`：计数、哈希和只读完整性检查。
"""
(HERE / "README.md").write_text(readme, encoding="utf-8")

source_paths = [
    FROZEN / "FROZEN_MANIFEST.json",
    FROZEN / "historical_line_scores.csv",
    FROZEN / "CANDIDATE_SCREENING.csv",
    FROZEN / "model_inputs.jsonl",
    FROZEN / "private_gold.jsonl",
    FROZEN / "evidence_chain.jsonl",
    ROOT / "VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117/runs/B019.jsonl",
    ROOT / "VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117/runs/B022.jsonl",
    ROOT / "VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117/batches/B019.json",
    ROOT / "VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117/batches/B022.json",
    DSH / "raw.jsonl",
    DSH / "scores.jsonl",
    scorecard,
    commentary,
    field_map_path,
    ROOT / "Self-cricket-clean_text_scorecard_v1_220_matches/match_0180/commentary.txt",
]
source_manifest = [{"path": rel(p), "sha256": sha256(p), "bytes": p.stat().st_size} for p in source_paths]
(HERE / "SOURCE_MANIFEST.json").write_text(json.dumps(source_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

frozen_manifest = json.loads((FROZEN / "FROZEN_MANIFEST.json").read_text(encoding="utf-8"))
frozen_mismatches = []
for entry in frozen_manifest["files"]:
    p = FROZEN / entry["path"]
    actual = sha256(p)
    if actual != entry["sha256"]:
        frozen_mismatches.append({"path": entry["path"], "expected": entry["sha256"], "actual": actual})

verification = {
    "formal_change_failures": len(failure_rows),
    "failure_unique_roots": len({x["match_root"] for x in failure_rows}),
    "category_total_rows": sum(x["failure_rows"] for x in category_rows),
    "failure_raw_links": len(raw_links),
    "all_failures_have_correct_same_event_contrast": all(bool(x["correct_contrast_model"]) for x in failure_rows),
    "all_historical_raw_output_hashes_verified": all(bool(x["raw_output_hash_verified"]) for x in failure_rows),
    "other_wrong_destination_above_correct": sum(
        x["observable_category_code"] == "other_wrong_value" and x["new_pred_wickets"] > x["new_correct_wickets"]
        for x in failure_rows
    ),
    "dsh_summary": summary,
    "match_0003_source_class": source_checks["classification"],
    "frozen_manifest_hash_mismatches": frozen_mismatches,
    "status": "PASS" if len(failure_rows) == 12 and not frozen_mismatches and summary["dsh_score_record_differences"] == 0 else "FAIL",
}
(HERE / "verification.json").write_text(json.dumps(verification, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(json.dumps(verification, ensure_ascii=False, indent=2))
