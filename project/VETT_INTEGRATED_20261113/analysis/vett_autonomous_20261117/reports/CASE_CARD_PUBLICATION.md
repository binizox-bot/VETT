# 案例卡：改判数值传播（发布版关联）

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


## 附加：直接发布版文本链接（CASE_COV_0001_LLAMA_E_WICKETS）

- match_root: match_0001；source_version: commentary-v1；source_type: published_commentary
- innings: 1；field_ids: inn1.total_wickets
- evidence: Stoneford eventually reached 144 all out in 35.3 overs
- gold: total_wickets=10；pred: 35
- answerability_status: explicit_total_present
- diagnostic_variant_ids: O, E
- verification_status: auto_checked_source_explicit
- full_task_validation: 覆盖组 E vs O 同根配对；该格 O 对、E 错
- R28 来源：无直接 R28 题；这是 220 场发布文本的直接证据链接，与 R28 改判样本分开。
