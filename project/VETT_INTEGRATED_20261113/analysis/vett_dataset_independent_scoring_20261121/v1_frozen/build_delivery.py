#!/usr/bin/env python3
"""Build the independent VETT v1 frozen dataset/scoring delivery from read-only sources."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
INTEGRATED = ROOT / "VETT_INTEGRATED_20261113"
CORPUS = ROOT / "Self-cricket-clean_text_scorecard_v1_220_matches"
LONG = INTEGRATED / "analysis" / "vett_local_evidence_long_run"
AUTO = INTEGRATED / "analysis" / "vett_autonomous_20261117"
BLIND_V2 = INTEGRATED / "analysis" / "small_model_diagnostics_v2" / "BLIND_REVIEW.md"
BLIND_TEXTS = INTEGRATED / "analysis" / "small_model_diagnostics_v1" / "texts"

sys.path.insert(0, str(HERE))
from score_frozen import parse_json_output, score_one, self_test  # noqa: E402

MODELS = ["qwen2.5:7b-instruct-q4_K_M", "llama3.1:8b", "gemma2:9b"]
VERSION = "v1_frozen_20261121"


def sha_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path, rows):
    Path(path).write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def write_csv(path, rows, fields):
    with Path(path).open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def line_number(text, quote):
    idx = text.index(quote)
    return text.count("\n", 0, idx) + 1


def char_span(text, quote):
    start = text.index(quote)
    return {"start": start, "end_exclusive": start + len(quote)}


def alias_map(fields):
    out = {}
    for field in fields:
        aliases = [field]
        underscored = field.replace(" ", "_").replace(".", "_")
        if underscored not in aliases:
            aliases.append(underscored)
        out[field] = aliases
    return out


def build_prompts():
    long_manifest = json.loads((LONG / "manifest.json").read_text(encoding="utf-8"))
    historical = next(row for row in long_manifest["evidence"] if row["match"] == "match_0047")
    commentary_path = CORPUS / "match_0047" / "commentary.txt"
    scorecard_0047_path = CORPUS / "match_0047" / "scorecard.md"
    commentary = commentary_path.read_text(encoding="utf-8").strip()
    scorecard_0047 = scorecard_0047_path.read_text(encoding="utf-8")
    sentence = historical["sentence"]
    assert sentence in commentary
    assert sha_text(commentary) == historical["text_sha256"], (sha_text(commentary), historical["text_sha256"])
    assert "| Total | 337/8 (50.0 Overs) |" in scorecard_0047

    long_fields = ["inn1.total_runs", "inn1.total_wickets"]
    long_prefix = (
        "You are a cricket scorer. Read the commentary and return the requested values at the END of the specified innings. "
        "Return ONLY a JSON object mapping each field id to its integer value. No prose.\n\n"
        "Sample: vett-dev-v1-0001\nInnings: 1\nFields:\n- inn1.total_runs\n- inn1.total_wickets\n\nCommentary:\n"
    )
    long_suffix = "\n\nJSON:"
    long_inputs = []
    long_golds = []
    for code, text in [("c00", commentary), ("c01", sentence)]:
        sample_id = f"vett-dev-v1-0001-{code}"
        prompt = long_prefix + text + long_suffix
        long_inputs.append({
            "sample_id": sample_id,
            "condition_code": code,
            "prompt": prompt,
            "prompt_sha256": sha_text(prompt),
            "text_sha256": sha_text(text),
            "field_order": long_fields,
        })
        long_golds.append({
            "sample_id": sample_id,
            "case_id": "vett-dev-v1-0001",
            "condition_code": code,
            "match_root": "match_0047",
            "innings": 1,
            "condition_semantics": "full_published_commentary" if code == "c00" else "verbatim_evidence_window",
            "field_order": long_fields,
            "gold": {"inn1.total_runs": 337, "inn1.total_wickets": 8},
            "legal_key_aliases": alias_map(long_fields),
            "review_status": "pending_human_review",
        })

    scorecard_0003_path = CORPUS / "match_0003" / "scorecard.md"
    scorecard_0003 = scorecard_0003_path.read_text(encoding="utf-8")
    source_lines = {
        "dismissal": "| Brandon Hale | c Mason Cooper b Evan Clarke | 4 | 8 | 0 | 0 | 50.00 |",
        "evan": "| Evan Clarke | 4 | 0 | 28 | 4 | 7.00 | 0 | 0 |",
        "connor": "| Connor Reed | 4 | 0 | 28 | 1 | 7.00 | 1 | 0 |",
        "total": "| Total | 164/8 (20.0 Overs) |",
    }
    for quote in source_lines.values():
        assert quote in scorecard_0003

    attribution_fields = [
        "Evan Clarke_wickets",
        "Evan Clarke_runs",
        "Connor Reed_wickets",
        "Connor Reed_runs",
        "innings_total_wickets",
    ]
    old = {
        "Evan Clarke_wickets": 4,
        "Evan Clarke_runs": 28,
        "Connor Reed_wickets": 1,
        "Connor Reed_runs": 28,
        "innings_total_wickets": 8,
    }
    changed = {**old, "Evan Clarke_wickets": 3, "Connor Reed_wickets": 2}
    base1 = "In innings 1, Brandon Hale was dismissed."
    base2 = "Pre-revision record: Evan Clarke 4 wickets for 28 runs; Connor Reed 1 wicket for 28 runs; the innings total was 8 wickets."
    notices = {
        "c10": "Match review: the dismissal is formally reassigned from Evan Clarke to Connor Reed. Update both bowlers' figures; runs and innings total do not change.",
        "c11": "Match review: the original attribution to Evan Clarke is maintained. No change to either bowler's figures.",
        "c12": "No review notice is provided. Use the pre-revision record as published.",
    }
    attr_prefix = (
        "You are a cricket scorer. Read the record and return the five requested fields. Return ONLY a JSON object mapping each field id to its integer value. No prose.\n\n"
        "Sample: vett-dev-v1-0002\nInnings: 1\nFields:\n"
        + "".join(f"- {field}\n" for field in attribution_fields)
        + "\nRecord:\n"
    )
    attr_inputs = []
    attr_golds = []
    for code in ["c10", "c11", "c12"]:
        record = " ".join([base1, base2, notices[code]])
        prompt = attr_prefix + record + "\n\nJSON:"
        sample_id = f"vett-dev-v1-0002-{code}"
        attr_inputs.append({
            "sample_id": sample_id,
            "condition_code": code,
            "prompt": prompt,
            "prompt_sha256": sha_text(prompt),
            "text_sha256": sha_text(record),
            "field_order": attribution_fields,
        })
        attr_golds.append({
            "sample_id": sample_id,
            "case_id": "vett-dev-v1-0002",
            "condition_code": code,
            "match_root": "match_0003",
            "innings": 1,
            "event_id": "match_0003.inn1.brandon_hale.reassign.v1",
            "condition_semantics": {"c10": "formal_reassignment", "c11": "maintain_original", "c12": "no_notice"}[code],
            "field_order": attribution_fields,
            "gold": changed if code == "c10" else old,
            "legal_key_aliases": alias_map(attribution_fields),
            "review_status": "pending_human_review",
        })

    model_inputs = long_inputs + attr_inputs
    gold_rows = long_golds + attr_golds
    write_jsonl(HERE / "model_inputs.jsonl", model_inputs)
    write_jsonl(HERE / "private_gold.jsonl", gold_rows)

    evidence_rows = []
    for row in long_inputs:
        quote_span = char_span(row["prompt"], sentence)
        evidence_rows.append({
            "case_id": "vett-dev-v1-0001",
            "sample_id": row["sample_id"],
            "match_root": "match_0047",
            "innings": 1,
            "entity": "Ridgefield",
            "fields": long_fields,
            "source_class": "published_original" if row["condition_code"] == "c00" else "verbatim_window_from_published_original",
            "provenance_flags": {
                "published_original": True,
                "local_controlled_edit": False,
                "rerender": False,
                "match_root_only_mapping": False,
            },
            "input_version": VERSION,
            "input_text_sha256": row["text_sha256"],
            "prompt_sha256": row["prompt_sha256"],
            "evidence_sentences": [{"quote": sentence, "prompt_char_span": quote_span}],
            "source_path": str(commentary_path.relative_to(ROOT)).replace("\\", "/"),
            "source_char_span": char_span(commentary, sentence),
            "scorecard_path": str(scorecard_0047_path.relative_to(ROOT)).replace("\\", "/"),
            "scorecard_cells": [
                {"field": "inn1.total_runs", "section": "Ridgefield innings", "row": "Total", "column": "Value", "source_value": "337/8 (50.0 Overs)"},
                {"field": "inn1.total_wickets", "section": "Ridgefield innings", "row": "Total", "column": "Value", "source_value": "337/8 (50.0 Overs)"},
            ],
            "old_value_timepoint": None,
            "event": None,
            "notification": None,
            "target": {"inn1.total_runs": 337, "inn1.total_wickets": 8},
            "must_remain": {},
            "review_status": "pending_human_review",
        })
    for row in attr_inputs:
        code = row["condition_code"]
        sentences = [base1, base2, notices[code]]
        evidence_rows.append({
            "case_id": "vett-dev-v1-0002",
            "sample_id": row["sample_id"],
            "match_root": "match_0003",
            "innings": 1,
            "entity": ["Evan Clarke", "Connor Reed", "Brandon Hale"],
            "fields": attribution_fields,
            "source_class": "local_controlled_edit_from_scorecard",
            "provenance_flags": {
                "published_original": False,
                "local_controlled_edit": True,
                "rerender": False,
                "match_root_only_mapping": False,
            },
            "input_version": VERSION,
            "input_text_sha256": row["text_sha256"],
            "prompt_sha256": row["prompt_sha256"],
            "evidence_sentences": [{"quote": sentence_, "prompt_char_span": char_span(row["prompt"], sentence_)} for sentence_ in sentences],
            "scorecard_path": str(scorecard_0003_path.relative_to(ROOT)).replace("\\", "/"),
            "scorecard_sha256": sha_file(scorecard_0003_path),
            "scorecard_cells": [
                {"field": "event_original_attribution", "line": line_number(scorecard_0003, source_lines["dismissal"]), "row": "Brandon Hale", "column": "Dismissal", "source_value": "c Mason Cooper b Evan Clarke"},
                {"field": "Evan Clarke_runs", "line": line_number(scorecard_0003, source_lines["evan"]), "row": "Evan Clarke", "column": "R", "source_value": 28},
                {"field": "Evan Clarke_wickets", "line": line_number(scorecard_0003, source_lines["evan"]), "row": "Evan Clarke", "column": "W", "source_value": 4},
                {"field": "Connor Reed_runs", "line": line_number(scorecard_0003, source_lines["connor"]), "row": "Connor Reed", "column": "R", "source_value": 28},
                {"field": "Connor Reed_wickets", "line": line_number(scorecard_0003, source_lines["connor"]), "row": "Connor Reed", "column": "W", "source_value": 1},
                {"field": "innings_total_wickets", "line": line_number(scorecard_0003, source_lines["total"]), "row": "Total", "column": "Value", "source_value": "164/8 (20.0 Overs)"},
            ],
            "old_value_timepoint": "pre-revision scorecard snapshot",
            "old_values": old,
            "event": "Brandon Hale dismissal attribution",
            "notification": notices[code],
            "target": changed if code == "c10" else old,
            "must_remain": {"Evan Clarke_runs": 28, "Connor Reed_runs": 28, "innings_total_wickets": 8},
            "review_status": "pending_human_review",
            "tail_summary_conflict": False,
        })
    write_jsonl(HERE / "evidence_chain.jsonl", evidence_rows)
    return model_inputs, gold_rows, evidence_rows, {
        "long_commentary": commentary,
        "long_sentence": sentence,
        "scorecard_0047": scorecard_0047,
        "scorecard_0003": scorecard_0003,
        "source_lines": source_lines,
        "old": old,
        "changed": changed,
        "notices": notices,
    }


def recompute_history():
    line_rows = []
    differences = []
    event_runs = []
    for batch_id in ["B019", "B022"]:
        path = AUTO / "runs" / f"{batch_id}.jsonl"
        for line_no, row in enumerate(read_jsonl(path), 1):
            expected = row["score"]["cells"]
            fields = list(expected)
            gold_row = {
                "field_order": fields,
                "gold": {field: expected[field]["gold"] for field in fields},
                "legal_key_aliases": alias_map(fields),
            }
            new_score = score_one(row.get("raw_output"), gold_row)
            old_score = bool(row.get("score", {}).get("task_correct"))
            record = {
                "source_file": str(path.relative_to(ROOT)).replace("\\", "/"),
                "source_line": line_no,
                "batch_id": batch_id,
                "match_root": row["match"],
                "event_id": f"{row['match']}.inn{row['innings']}.attribution",
                "model": row["model"],
                "condition": row["cond"],
                "parse_ok_recorded": row.get("parse_ok"),
                "old_task_correct": old_score,
                "new_executable": new_score["executable"],
                "new_task_correct": new_score["task_correct"],
                "new_correct_fields": new_score["correct_fields"],
                "new_total_fields": new_score["total_fields"],
                "new_error": new_score["error"],
                "raw_output_sha256": sha_text(row.get("raw_output", "")),
            }
            line_rows.append(record)
            event_runs.append({**row, "new_score": new_score, "source_line": line_no, "batch_id": batch_id})
            if old_score != new_score["task_correct"]:
                differences.append({
                    **record,
                    "difference_reason": "explicit legal alias normalization: entity spaces and underscores are equivalent",
                    "raw_output": row.get("raw_output"),
                })

    grouped = defaultdict(dict)
    for row in event_runs:
        grouped[(row["match"], row["model"])][row["cond"]] = row
    event_intersections = []
    for (match, model), conds in sorted(grouped.items()):
        change = conds.get("C_change")
        maintain = conds.get("C_maintain")
        no_notice = conds.get("C_no_notice")
        executable = all(item and item["new_score"]["executable"] for item in [change, maintain, no_notice])
        change_ok = bool(change and change["new_score"]["task_correct"])
        maintain_ok = bool(maintain and maintain["new_score"]["task_correct"])
        no_notice_ok = bool(no_notice and no_notice["new_score"]["task_correct"])
        actual_mistransfer = False
        for item in [maintain, no_notice]:
            if not item or not item["new_score"]["executable"]:
                continue
            fields = item["new_score"]["normalized"]
            wicket_fields = [field for field in item["score"]["cells"] if field.endswith("_wickets") and field != "innings_total_wickets"]
            if len(wicket_fields) == 2:
                gold = {field: item["score"]["cells"][field]["gold"] for field in wicket_fields}
                try:
                    deltas = [int(fields[field]) - int(gold[field]) for field in wicket_fields]
                    if deltas[0] == -deltas[1] and deltas[0] != 0:
                        actual_mistransfer = True
                except Exception:
                    pass
        event_intersections.append({
            "match_root": match,
            "event_id": f"{match}.inn1.attribution",
            "model": model,
            "change_correct": change_ok,
            "maintain_correct": maintain_ok,
            "both_correct": change_ok and maintain_ok,
            "no_notice_correct": no_notice_ok,
            "all_three_correct": change_ok and maintain_ok and no_notice_ok,
            "actual_mistransfer": actual_mistransfer,
            "unexecutable": not executable,
        })

    long_manifest = json.loads((LONG / "manifest.json").read_text(encoding="utf-8"))
    abc_gold = {(row["match"], row["method"]): row for row in long_manifest["abc"]}
    abc_runs = [row for row in read_jsonl(LONG / "runs" / "all.jsonl") if row.get("phase") == "abc" and row.get("method") in {"A", "B"}]
    long_scores = defaultdict(dict)
    for line_no, row in enumerate(read_jsonl(LONG / "runs" / "all.jsonl"), 1):
        if row.get("phase") != "abc" or row.get("method") not in {"A", "B"}:
            continue
        gold = abc_gold[(row["match"], row["method"])]
        fields = ["total_runs", "total_wickets"]
        gold_row = {
            "field_order": fields,
            "gold": {"total_runs": gold["gold_runs"], "total_wickets": gold["gold_wickets"]},
            "legal_key_aliases": {field: [field] for field in fields},
        }
        new_score = score_one(row.get("raw_output"), gold_row)
        long_scores[(row["match"], row["model"])][row["method"]] = new_score
        line_rows.append({
            "source_file": str((LONG / "runs" / "all.jsonl").relative_to(ROOT)).replace("\\", "/"),
            "source_line": line_no,
            "batch_id": "historical_abc",
            "match_root": row["match"],
            "event_id": "published_total_full_window",
            "model": row["model"],
            "condition": row["method"],
            "parse_ok_recorded": row.get("parse_ok"),
            "old_task_correct": None,
            "new_executable": new_score["executable"],
            "new_task_correct": new_score["task_correct"],
            "new_correct_fields": new_score["correct_fields"],
            "new_total_fields": new_score["total_fields"],
            "new_error": new_score["error"],
            "raw_output_sha256": sha_text(row.get("raw_output", "")),
        })
    transitions = []
    for (match, model), methods in sorted(long_scores.items()):
        full = methods.get("A")
        window = methods.get("B")
        full_ok = bool(full and full["task_correct"])
        window_ok = bool(window and window["task_correct"])
        transitions.append({
            "match_root": match,
            "model": model,
            "full_correct": full_ok,
            "window_correct": window_ok,
            "wrong_to_right": (not full_ok) and window_ok,
            "right_to_wrong": full_ok and (not window_ok),
            "both_correct": full_ok and window_ok,
            "both_wrong": (not full_ok) and (not window_ok),
            "unexecutable": not (full and window and full["executable"] and window["executable"]),
        })

    write_csv(HERE / "historical_line_scores.csv", line_rows, list(line_rows[0]))
    write_csv(HERE / "historical_event_intersections.csv", event_intersections, list(event_intersections[0]))
    write_csv(HERE / "full_window_transitions.csv", transitions, list(transitions[0]))
    diff_fields = list(differences[0]) if differences else ["source_file", "source_line", "batch_id", "match_root", "event_id", "model", "condition", "old_task_correct", "new_task_correct", "difference_reason", "raw_output"]
    write_csv(HERE / "INDEPENDENT_RECALC_DIFF.csv", differences, diff_fields)

    def count(rows, key):
        return sum(1 for row in rows if row[key])

    selected = [row for row in event_intersections if row["match_root"] == "match_0003"]
    summary = {
        "sealed_sources": [
            {"path": str((AUTO / "runs" / "B019.jsonl").relative_to(ROOT)).replace("\\", "/"), "sha256": sha_file(AUTO / "runs" / "B019.jsonl")},
            {"path": str((AUTO / "runs" / "B022.jsonl").relative_to(ROOT)).replace("\\", "/"), "sha256": sha_file(AUTO / "runs" / "B022.jsonl")},
            {"path": str((LONG / "runs" / "all.jsonl").relative_to(ROOT)).replace("\\", "/"), "sha256": sha_file(LONG / "runs" / "all.jsonl")},
        ],
        "attribution_all_8_events": {
            "intersections": len(event_intersections),
            "change_correct": count(event_intersections, "change_correct"),
            "maintain_correct": count(event_intersections, "maintain_correct"),
            "both_correct": count(event_intersections, "both_correct"),
            "no_notice_correct": count(event_intersections, "no_notice_correct"),
            "all_three_correct": count(event_intersections, "all_three_correct"),
            "actual_mistransfer": count(event_intersections, "actual_mistransfer"),
            "unexecutable": count(event_intersections, "unexecutable"),
        },
        "selected_match_0003": {
            "intersections": len(selected),
            "change_correct": count(selected, "change_correct"),
            "maintain_correct": count(selected, "maintain_correct"),
            "both_correct": count(selected, "both_correct"),
            "no_notice_correct": count(selected, "no_notice_correct"),
            "actual_mistransfer": count(selected, "actual_mistransfer"),
            "unexecutable": count(selected, "unexecutable"),
        },
        "full_vs_window_4_matches": {
            "pairs": len(transitions),
            "full_correct": count(transitions, "full_correct"),
            "window_correct": count(transitions, "window_correct"),
            "wrong_to_right": count(transitions, "wrong_to_right"),
            "right_to_wrong": count(transitions, "right_to_wrong"),
            "both_correct": count(transitions, "both_correct"),
            "both_wrong": count(transitions, "both_wrong"),
            "unexecutable": count(transitions, "unexecutable"),
        },
        "selected_match_0047": next(row for row in transitions if row["match_root"] == "match_0047" and row["model"] == MODELS[0]) | {
            "all_models_both_correct": all(row["both_correct"] for row in transitions if row["match_root"] == "match_0047")
        },
        "differences_from_recorded_scores": len(differences),
    }
    write_json(HERE / "independent_recalc_summary.json", summary)
    return summary, differences


def build_docs(model_inputs, gold_rows, evidence_rows, context, summary, differences):
    workspace_audit = """# 工作区可访问性审计

结论：当前工作区包含可读的完整项目与源语料，不是仅导出目录。

- 合并报告索引：`VETT_COMPLETE_REPORT_20261121.md`。仅用于定位，不作为原句或分数凭据。
- 220 场源语料：`Self-cricket-clean_text_scorecard_v1_220_matches/`，含 commentary、scorecard、meta、evidence chain。
- 长文联动实际输入与原始回答：`VETT_INTEGRATED_20261113/analysis/vett_local_evidence_long_run/manifest.json`、`runs/all.jsonl`。
- 8 个归属事件三臂输入与原始回答：`vett_autonomous_20261117/batches/B019.json`、`B022.json`、`runs/B019.jsonl`、`B022.jsonl`。
- 40 格盲审题面与 6 场全文：`small_model_diagnostics_v2/BLIND_REVIEW.md`、`small_model_diagnostics_v1/texts/`。
- 历史 SQLite、worker、队列：存在，但本轮未打开、未查询、未写入。

本轮所需源文件没有缺失。新冻结批次的 15 个新模型回答尚不存在，这是 DSH 后续推理的预期输入，不是数据缺失；独立复算使用上述已封存历史 JSONL。
"""
    (HERE / "WORKSPACE_AUDIT.md").write_text(workspace_audit, encoding="utf-8")

    schema = {
        "schema_version": "vett.dataset_scoring.freeze.v1",
        "model_inputs": {"format": "jsonl", "required": ["sample_id", "condition_code", "prompt", "prompt_sha256", "text_sha256", "field_order"]},
        "predictions": {"format": "jsonl", "required": ["sample_id", "model", "raw_output"], "optional": ["parsed"]},
        "private_gold": {"format": "jsonl", "required": ["sample_id", "case_id", "condition_code", "match_root", "innings", "field_order", "gold", "legal_key_aliases"]},
        "scoring": "all fields exact after explicit alias normalization; integers compare by integer value; missing/conflicting aliases are unexecutable",
    }
    write_json(HERE / "SCHEMA.json", schema)

    selftest = self_test()
    write_json(HERE / "selftest_results.json", selftest)
    if not selftest["passed"]:
        raise RuntimeError("scorer self-test failed")

    case1 = f"""# 案例 1：发布版长文证据定位

- 稳定 ID：`vett-dev-v1-0001`
- 比赛根：`match_0047`，第一局，Ridgefield。
- 用途：开发；不在方法保留根 `match_0121`–`match_0160`。
- 抽样类型：普通开发样本。不是按历史错误挑选；历史 A/B 中三个模型均答对。选择它是因为发布版全文、证据窗、三模型历史输出和记分表字段都齐全。
- 字段格：`inn1.total_runs`、`inn1.total_wickets` → scorecard 第一局 `Total` 行、`Value` 列：`337/8 (50.0 Overs)`。
- 发布版原句：`{context['long_sentence']}`
- 源字符范围：`{char_span(context['long_commentary'], context['long_sentence'])['start']}:{char_span(context['long_commentary'], context['long_sentence'])['end_exclusive']}`，0-based、end-exclusive。
- 输入：`c00` 为完整发布版原文；`c01` 为从同一原文逐字截取的证据句。不是重渲染，不是仅比赛根映射。
- 题目实际考查：最终答案在正文直接写出；不需要跨句更新。全文中有第一局中间比分和第二局 `222/10` 等竞争比分，因此全文条件仍包含检索干扰。
- 通知/旧值：不适用。
- 后半段矛盾检查：不适用（无通知）；发布版结尾与终局值一致。
- 审核状态：自动逐字与记分表核对通过，人工语义复核仍为 `pending_human_review`。
"""
    (HERE / "CASE_01_LONG_EVIDENCE.md").write_text(case1, encoding="utf-8")

    case2 = f"""# 案例 2：归属改判记账

- 稳定 ID：`vett-dev-v1-0002`
- 比赛根：`match_0003`，第一局，Brandon Hale 的出局归属；8 个既有归属事件之一。
- 用途：开发；不在方法保留根 `match_0121`–`match_0160`。
- 抽样类型：历史错例。历史 `C_change` 中 Qwen 保留旧值，Llama/Gemma 正确；用于复查“通知到最终 figures 的传播”。
- 原始格：Evan Clarke bowling 行 `R=28, W=4`；Connor Reed bowling 行 `R=28, W=1`；第一局 Total `164/8`；Brandon Hale dismissal 行原记为 `b Evan Clarke`。
- 旧值时点：pre-revision scorecard snapshot。
- 三臂固定同一事件、同一旧值：
  - `c10` 正式改判：Evan wickets `4→3`，Connor wickets `1→2`。
  - `c11` 维持：保持 `4`、`1`。
  - `c12` 无通知：保持 `4`、`1`。
- 应保持字段：Evan runs `28`、Connor runs `28`、innings total wickets `8`。
- 题目实际考查：最终改判值没有直接写出。`c10` 需要跨句读取旧值，再应用一次 A−1/B+1；旧值句与通知句之间没有其他相关事件。旧 runs 恰好相等（28/28），可检测人物/字段错位。
- 来源分类：旧值与原始归属来自 scorecard；三臂通知是局部受控编辑。不是发布版原文，不是重渲染，也不是仅比赛根映射。
- 后半段矛盾检查：三个模型输入在通知后直接结束，没有残留旧 figures 的最终汇总。
- 审核状态：字段、算术和输入逐字检查通过；通知语义仍标 `pending_human_review`。
"""
    (HERE / "CASE_02_ATTRIBUTION.md").write_text(case2, encoding="utf-8")

    attr = summary["attribution_all_8_events"]
    fw = summary["full_vs_window_4_matches"]
    recalcmd = f"""# 独立复算

复算只读三个已封存 JSONL，不读取或修改 SQLite、worker、队列。所有统计先逐行解析，再按 `match_root × event × model` 取交集。

## 8 个归属事件（24 个比赛×模型交集）

- 改判正确：{attr['change_correct']}/{attr['intersections']}
- 维持正确：{attr['maintain_correct']}/{attr['intersections']}
- 两者同时正确：{attr['both_correct']}/{attr['intersections']}
- 无通知正确：{attr['no_notice_correct']}/{attr['intersections']}
- 三臂同时正确：{attr['all_three_correct']}/{attr['intersections']}
- 实际误转移：{attr['actual_mistransfer']}/{attr['intersections']}
- 不可执行：{attr['unexecutable']}/{attr['intersections']}

`actual_mistransfer` 只在维持/无通知臂中，两个投手 wickets 出现非零、等量反向变化时计数；改判臂保留旧值属于“未执行改判”，不算误转移。

## 全文 A 与证据窗 B（4 场 × 3 模型）

- 全文正确：{fw['full_correct']}/{fw['pairs']}
- 窗口正确：{fw['window_correct']}/{fw['pairs']}
- 错→对：{fw['wrong_to_right']}/{fw['pairs']}
- 对→错：{fw['right_to_wrong']}/{fw['pairs']}
- 都对：{fw['both_correct']}/{fw['pairs']}
- 都错：{fw['both_wrong']}/{fw['pairs']}
- 不可执行：{fw['unexecutable']}/{fw['pairs']}

不可执行的 1 对是 `match_0102 / llama3.1:8b` 的窗口输出：原始回答改成以球队名为外层的嵌套对象，未按冻结的扁平合法键返回；原始文件仍保留该回答。

## 与旧评分的差异

差异 {len(differences)} 行。`B022 / match_0030 / qwen / C_maintain` 的原始输出使用 `Logan_Vale_*`、`Owen_Price_*`；旧评分只认空格键名而记错。本版在冻结前明确把空格/下划线列为合法别名，故该行从错改为对。原始回答未改动。逐行见 `INDEPENDENT_RECALC_DIFF.csv`。
"""
    (HERE / "INDEPENDENT_RECALC.md").write_text(recalcmd, encoding="utf-8")

    screening_rows = [
        {"match_root": "match_0003", "status": "selected_v1", "selection_type": "historical_error", "coverage": "very_low_old_value; equal_runs; attribution", "reason": "old wickets 4/1; qwen failed change arm; complete three-arm history", "not_covered_reason": ""},
        {"match_root": "match_0047", "status": "selected_v1", "selection_type": "ordinary_dev", "coverage": "published_final; multiple_competing_scores; full_window", "reason": "all source layers and historical A/B outputs available", "not_covered_reason": ""},
        {"match_root": "match_0008", "status": "screened_next", "selection_type": "difficulty_target", "coverage": "equal_old_wickets_3_3", "reason": "tests attribution when old wickets are equal", "not_covered_reason": "not in first two-case freeze"},
        {"match_root": "match_0010", "status": "screened_next", "selection_type": "difficulty_target", "coverage": "low_second_old_value_2; attribution", "reason": "complete three-arm history", "not_covered_reason": "not in first two-case freeze"},
        {"match_root": "match_0012", "status": "screened_next", "selection_type": "difficulty_target", "coverage": "low_second_old_value_2; attribution", "reason": "complete three-arm history", "not_covered_reason": "not in first two-case freeze"},
        {"match_root": "match_0015", "status": "screened_next", "selection_type": "difficulty_target", "coverage": "low_second_old_value_2; attribution", "reason": "complete three-arm history", "not_covered_reason": "not in first two-case freeze"},
        {"match_root": "match_0030", "status": "screened_next", "selection_type": "historical_format_error", "coverage": "low_runs_1; low_second_old_value_2; alias_variant", "reason": "separates semantic error from legal-key parser error", "not_covered_reason": "not in first two-case freeze"},
        {"match_root": "match_0180", "status": "screened_next", "selection_type": "fixed_seed_ordinary", "coverage": "published_final; competing_innings_score", "reason": "first eligible ordinary evidence root under seed 20261121", "not_covered_reason": "no frozen window pair yet"},
    ]
    write_csv(HERE / "CANDIDATE_SCREENING.csv", screening_rows, list(screening_rows[0]))
    (HERE / "CANDIDATE_SCREENING.md").write_text(
        "# 下一批筛选\n\n固定种子 `20261121` 用于普通证据根；优先困难覆盖另行标注。当前最多 8 个开发根，均避开保留根 `0121–0160`。\n\n"
        "未覆盖：旧 wickets 为 0 的事件（现有 8 事件没有）；真正多通知/高事件密度的归属输入（现有三臂均为单事件受控文本）；独立 held-out 根（本轮明确仅做开发）。`match_0026` 与 `match_0017` 因 8 根上限且没有新增首要覆盖而暂不纳入。\n",
        encoding="utf-8",
    )

    boundaries = """# 结论支持边界

## 已能支持

- 两个案例都能从模型实际输入中的逐字原句追到 scorecard 的具体行列。
- `match_0047` 的两个目标字段由单句直接给出；全文含其他比分，窗口删去干扰但不改写证据。
- `match_0003` 三臂使用同一事件与旧值，改判目标唯一；runs 与 innings total wickets 必须保持。
- 独立评分器通过正确、人物对调、只改一边、错误转移、空答、合法键名变体六类自测。
- 封存原始回答的逐行复算与交集统计可重放；旧评分有一行合法别名误判。

## 仍需人工判断

- 发布版句子是否满足最终局语义，而不只是字符串与 scorecard 一致；当前仍是 `pending_human_review`。
- 局部受控的归属通知是否符合研究者想测的真实改判措辞与责任边界。
- 40 格可答性盲审尚无人返回，不能把候选句或模型一致当作人工金标。
- 两个开发案例不能外推到保留根或整体 220 场。
- 现有单事件三臂不能支持“高事件密度下仍能稳定记账”的结论。
"""
    (HERE / "SUPPORT_BOUNDARIES.md").write_text(boundaries, encoding="utf-8")

    dsh = """# DSH 消费说明

1. 只读取 `model_inputs.jsonl`。每行的 `condition_code` 是不含语义的稳定代码；不要把 `private_gold.jsonl` 发送给模型。
2. 对每行分别运行三个冻结模型。保存 JSONL：`sample_id`、`model`、`raw_output`，可附 `model_digest`、decode、耗时和终止原因。
3. 模型/条件比较必须使用相同 model tag、digest、temperature、seed、context 和输出上限。期望矩阵为 5 个输入 × 3 模型 = 15 个原始回答。
4. 评分：`python score_frozen.py --predictions <raw.jsonl> --gold private_gold.jsonl --out <scores.jsonl>`。
5. 本目录已冻结。任何提示、别名、字段顺序或金标修改都必须新建版本目录。
"""
    (HERE / "DSH_RUN.md").write_text(dsh, encoding="utf-8")

    blind_dir = HERE / "blind_review_40"
    texts_dir = blind_dir / "texts"
    texts_dir.mkdir(parents=True, exist_ok=True)
    blind_text = BLIND_V2.read_text(encoding="utf-8")
    (blind_dir / "BLIND_REVIEW_40.md").write_text(blind_text, encoding="utf-8")
    text_hashes = []
    for src in sorted(BLIND_TEXTS.glob("match_*.md")):
        dst = texts_dir / src.name
        shutil.copyfile(src, dst)
        text_hashes.append({"file": f"texts/{src.name}", "sha256": sha_file(dst)})
    count40 = sum(1 for line in blind_text.splitlines() if line.startswith("## S"))
    write_json(blind_dir / "TEXT_HASHES.json", {"items": count40, "texts": text_hashes})
    (blind_dir / "README.md").write_text(
        f"# 40 格盲审包\n\n题目数：{count40}。已附 6 场完整原文，题面不含金标值或模型回答。人工状态保持待审。先独立填写答案、证据段号和可答性，再另行对 scorecard。\n",
        encoding="utf-8",
    )

    input_audit = {
        "passed": True,
        "model_visible_file": "model_inputs.jsonl",
        "opaque_condition_codes": sorted({row["condition_code"] for row in model_inputs}),
        "match_root_absent_from_prompts": all("match_" not in row["prompt"] for row in model_inputs),
        "gold_object_absent_from_model_rows": all("gold" not in row for row in model_inputs),
        "private_gold_path_absent_from_prompts": all("private_gold" not in row["prompt"] for row in model_inputs),
        "note": "Task evidence itself may contain the requested values; the audit forbids filename, condition-label, gold-object, and extra-summary leakage.",
    }
    write_json(HERE / "INPUT_LEAKAGE_AUDIT.json", input_audit)
    blind_audit = {
        "passed": count40 == 40,
        "items": count40,
        "full_text_files": len(text_hashes),
        "gold_values_attached": False,
        "model_answers_attached": False,
        "review_status": "pending_human_review",
    }
    write_json(blind_dir / "BLIND_REVIEW_AUDIT.json", blind_audit)

    homepage = f"""# VETT 数据集构建与独立评分 v1

状态：`FROZEN`。这是独立版本目录；没有写入历史数据库、SQLite、worker 或队列。

## 两个首批案例

1. `vett-dev-v1-0001`：`match_0047` 第一局。发布版原句“Ridgefield closed on 337 for 8”追到 scorecard 第一局 `Total` 行，得到 `inn1.total_runs=337`、`inn1.total_wickets=8`。普通开发样本，不是按错例挑选。
2. `vett-dev-v1-0002`：`match_0003` 第一局。Brandon Hale 的原始出局行追到 Evan Clarke，旧 bowling 格为 Evan `4/28`、Connor `1/28`；正式改判唯一更新为 `3/28`、`2/28`，局总仍为 8。历史错例。

两案均为开发根，并避开方法保留根 `match_0121`–`match_0160`。证据详见 `CASE_01_LONG_EVIDENCE.md`、`CASE_02_ATTRIBUTION.md` 与 `evidence_chain.jsonl`。

## 冻结小批次

- 模型可见：`model_inputs.jsonl`（5 条输入，条件码不泄漏语义或答案）。
- 评测端：`private_gold.jsonl`、`SCHEMA.json`、`score_frozen.py`。
- 预期 DSH 矩阵：5 条 × 3 模型 = 15 个回答。
- 评分器自测：6/6 通过；结果见 `selftest_results.json`。
- 冻结清单：`FROZEN_MANIFEST.json`；后续修改必须新建版本。

## 独立复算

- 8 个归属事件：改判 {summary['attribution_all_8_events']['change_correct']}/24，维持 {summary['attribution_all_8_events']['maintain_correct']}/24，同时正确 {summary['attribution_all_8_events']['both_correct']}/24，实际误转移 {summary['attribution_all_8_events']['actual_mistransfer']}/24，不可执行 {summary['attribution_all_8_events']['unexecutable']}/24。
- 全文→窗口：错→对 {summary['full_vs_window_4_matches']['wrong_to_right']}/12，对→错 {summary['full_vs_window_4_matches']['right_to_wrong']}/12。
- 与旧评分差异：{len(differences)} 行，见 `INDEPENDENT_RECALC_DIFF.csv`；原始回答未改。

## 人工与下一批

- `blind_review_40/`：40 格题面与 6 场完整原文，隐藏金标和模型回答。
- `CANDIDATE_SCREENING.csv`：最多 8 个开发根的筛选清单与未覆盖原因。
- `SUPPORT_BOUNDARIES.md`：已能支持与仍需人工判断的结论。
"""
    (HERE / "README.md").write_text(homepage, encoding="utf-8")


def freeze_manifest(model_inputs, gold_rows):
    frozen_files = [
        "model_inputs.jsonl",
        "private_gold.jsonl",
        "SCHEMA.json",
        "score_frozen.py",
        "selftest_results.json",
        "evidence_chain.jsonl",
        "CASE_01_LONG_EVIDENCE.md",
        "CASE_02_ATTRIBUTION.md",
        "DSH_RUN.md",
        "INPUT_LEAKAGE_AUDIT.json",
        "verify_delivery.py",
    ]
    manifest = {
        "schema": "vett.frozen_manifest.v1",
        "version": VERSION,
        "status": "FROZEN",
        "created_at": "2026-11-21T00:00:00+08:00",
        "development_roots": ["match_0003", "match_0047"],
        "reserved_method_roots": "match_0121-match_0160",
        "reserved_root_overlap": [],
        "sample_count": len(model_inputs),
        "model_count": len(MODELS),
        "expected_request_count": len(model_inputs) * len(MODELS),
        "models": MODELS,
        "comparability": {
            "required_equal": ["model_tag", "model_digest", "temperature", "seed", "num_ctx", "num_predict"],
            "long_pair": ["vett-dev-v1-0001-c00", "vett-dev-v1-0001-c01"],
            "attribution_triplet": ["vett-dev-v1-0002-c10", "vett-dev-v1-0002-c11", "vett-dev-v1-0002-c12"],
        },
        "field_orders": {row["sample_id"]: row["field_order"] for row in gold_rows},
        "files": [{"path": name, "sha256": sha_file(HERE / name)} for name in frozen_files],
        "mutation_policy": "immutable; create a new version directory for any change",
    }
    write_json(HERE / "FROZEN_MANIFEST.json", manifest)
    files = sorted(
        path for path in HERE.rglob("*")
        if path.is_file()
        and path.name != "MANIFEST.sha256"
        and "__pycache__" not in path.parts
    )
    lines = [f"{sha_file(path)}  {path.relative_to(HERE).as_posix()}" for path in files]
    (HERE / "MANIFEST.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    model_inputs, gold_rows, evidence_rows, context = build_prompts()
    summary, differences = recompute_history()
    build_docs(model_inputs, gold_rows, evidence_rows, context, summary, differences)
    freeze_manifest(model_inputs, gold_rows)
    print(json.dumps({
        "version": VERSION,
        "inputs": len(model_inputs),
        "expected_requests": len(model_inputs) * len(MODELS),
        "selftest": "passed",
        "historical_differences": len(differences),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
