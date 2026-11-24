
import json, sqlite3
from pathlib import Path
c=sqlite3.connect("state/workflow.db"); c.row_factory=sqlite3.Row
raw=c.execute("SELECT r.model,r.raw_output,r.parsed_json,r.score_json FROM results r JOIN tasks t USING(task_key) WHERE r.batch_id='B021' AND t.cond='NEI_OI' ORDER BY r.created_at LIMIT 1").fetchone()

card1 = """# 案例卡：改判数值传播（发布版关联）

- case_id: CASE_B019_0003_C_CHANGE
- match_root: match_0003
- source_version: attribution-followup-v1
- source_type: scorecard_rerender（受控重渲染，不是真实赛果更正）
- innings: 1
- entity_ids: match_0003, Brandon Hale, Evan Clarke, Connor Reed
- field_ids: Evan Clarke_wickets, Evan Clarke_runs, Connor Reed_wickets, Connor Reed_runs, innings_total_wickets
- evidence_spans: 控制记录（出局者 Brandon Hale；原投手 Evan Clarke 4/28；新投手 Connor Reed 1/28；本局 8 wickets）
- answerability_status: explicit_record_with_formal_notice
- diagnostic_variant_ids: C_change, C_maintain, C_no_notice
- verification_status: auto_checked_against_task_gold
- candidate_patch: none_for_data; 记录为通知到数值传播失败
- full_task_validation: B019 176/180；C_change 56/60；C_maintain 60/60；C_no_notice 60/60

## 原始回答 vs gold（C_change, qwen）

- gold: Evan Clarke_wickets=3, Evan Clarke_runs=28, Connor Reed_wickets=2, Connor Reed_runs=28, innings_total_wickets=8
- pred: Evan Clarke_wickets=4, Evan Clarke_runs=28, Connor Reed_wickets=2, Connor Reed_runs=28, innings_total_wickets=8

## 最早可确认的错误层

1. 通知：正式改判通知存在（应把 A 改记到 B）→ 模型没有表示没看到。
2. 人物/旧值：Brandon Hale、Evan Clarke 4/28、Connor Reed 1/28 均正确 → 未错。
3. 两方更新：A 应 4→3，B 应 1→2；模型 A 仍为 4（未减 1），B 正确为 2 → **最早错误在此层**。
4. 应保持的值：runs 28/28、total 8 均正确 → 未错。

## R28 来源

- 数据来自 VETT_INTEGRATED_20261113/analysis/attribution_followup/samples.json。
- 这是 R28 关联的改判/归属诊断样本（scorecard 重渲染），不是 R28 直接题面；不得写成 R28 直接证据。
- 人工未复核，状态 pending_human_review。
"""
Path("reports/CASE_CARD_PUBLICATION.md").write_text(card1, encoding="utf-8")

card2 = f"""# 案例卡：长度匹配非证据删除反例

- case_id: CASE_B021_0002_NEI_CONTROL
- match_root: match_0002
- source_version: commentary-v1
- source_type: controlled_rewrite
- innings: 2
- entity_ids: match_0002
- field_ids: inn2.total_runs, inn2.total_wickets
- evidence_spans: 目标终局句在 O/WI/OI/NEI 中均保留；NEI_OI 删除 313 字无关句，NEI_WI 删除 251 字无关句
- answerability_status: explicit_total_present_in_all_variants
- diagnostic_variant_ids: O, WI, OI, NEI_OI, NEI_WI
- verification_status: auto_checked_source_diff
- candidate_patch: do_not_claim_OI_specific_effect；保留为未定，扩展匹配对照
- full_task_validation: B021 0/6；B003 O 0/6、OI 3/6

## 配对结果

- O: 0/6
- OI: 3/6
- NEI_OI: 0/6
- NEI_WI: 0/6
- 删除长度：WI 269、OI 364、NEI_OI 313、NEI_WI 251

## 原始回答样例（B021 NEI_OI, {raw['model'] if raw else 'n/a'}）

- raw: {(raw['raw_output'] if raw else 'n/a')[:500]}
- parsed: {raw['parsed_json'] if raw else 'n/a'}

## 结论

- 删除长度匹配的非证据句也会让模型全错；
- B003 的 OI +3 未被 NEI 复现，不能当作“删另一局比分”的特异收益；
- 人工未复核，pending_human_review。
"""
Path("reports/CASE_CARD_COUNTEREXAMPLE.md").write_text(card2, encoding="utf-8")
print("cards written", bool(raw))
