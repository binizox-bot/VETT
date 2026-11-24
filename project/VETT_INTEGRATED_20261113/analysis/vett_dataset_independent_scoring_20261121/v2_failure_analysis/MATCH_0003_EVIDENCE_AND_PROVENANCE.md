# match_0003 失败案例与输入来源

## 历史失败

- 失败行：`VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117/runs/B019.jsonl:1`，模型 `qwen2.5:7b-instruct-q4_K_M`。
- 历史模型实际回答：Evan Clarke `4/28`，Connor Reed `2/28`，全队 wickets `8`。
- 正确值：Evan Clarke `3/28`，Connor Reed `2/28`，全队 wickets `8`。
- 可观察分类：只改新投手。单次输出不能区分是漏减、复制旧值还是其他机制，原因保持不确定。

历史输入原句：

> In inn1, Brandon Hale was dismissed. Pre-revision record: Evan Clarke 4 wickets for 28 runs; Connor Reed 1 wickets for 28 runs; the innings total was 8 wickets. Match review: the dismissal is formally reassigned from Evan Clarke to Connor Reed. Update both bowlers' figures; runs and innings total do not change.

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

> In innings 1, Brandon Hale was dismissed. Pre-revision record: Evan Clarke 4 wickets for 28 runs; Connor Reed 1 wicket for 28 runs; the innings total was 8 wickets. Match review: the dismissal is formally reassigned from Evan Clarke to Connor Reed. Update both bowlers' figures; runs and innings total do not change.

通知语义仍沿用冻结交付的 `pending_human_review` 状态。
