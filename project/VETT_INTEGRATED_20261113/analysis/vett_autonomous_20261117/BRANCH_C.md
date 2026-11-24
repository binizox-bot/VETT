
# 分支 C：同一事件的三通知条件（R28 关联）

构建日期：2026-11-18。数据源：VETT_INTEGRATED_20261113/analysis/attribution_followup/samples.json。
外部 API 0；事件为 scorecard 重渲染后的受控改判，不是真实赛果更正。

## 1. 条件

| 条件 | 通知 | gold |
|---|---|---|
| C_change | 正式改判：从 A 改记到 B；A−1、B+1，runs/total 不变 | 新值 |
| C_maintain | 维持原判：仍记 A，不改 | 旧值 |
| C_no_notice | 无通知，只有改判前记录 | 旧值（按已发布记录） |

每样本 3 条件 × 3 模型 = 9 任务；4 样本 = 36 任务。

## 2. 样本与旧值方向

| match | 局 | 出局者 | A 旧 | B 旧 | 新 A | 新 B | 旧值方向 |
|---|---|---|---:|---:|---:|---:|---|
| match_0003 | inn1 | Brandon Hale | Evan Clarke 4/28 | Connor Reed 1/28 | 3 | 2 | A 高、B 低 |
| match_0008 | inn2 | Noah Brooks | Luke Barrett 3/30 | Ryan Frost 3/37 | 2 | 4 | A/B 相等，改后 B 高 |
| match_0017 | inn2 | Liam Reed | Miles Carter 5/18 | Liam Brooks 3/27 | 4 | 4 | A 高、B 低，改后相等 |
| match_0026 | inn2 | Ryan Hale | Dylan Cole 5/5 | Ben Carter 2/5 | 4 | 3 | A 高、B 低 |

覆盖了 A 旧值高、A/B 相等、改后相等三种方向；runs 两两相等。

## 3. 字段与评分

五字段：A_wickets、A_runs、B_wickets、B_runs、innings_total_wickets。

- 主指标：A_wickets、B_wickets、innings_total_wickets 三项同时正确。
- 另报：两个 runs 同时正确；五字段同时正确。
- 错误分类：两人都旧值；只给 B+1；只给 A−1；两人都改但值错；wicket 对但 total/runs 错。

## 4. 与 B013 的区别

B013 是 220 场 commentary 的跨局删除对照；分支 C 是 scorecard 重渲染事件的通知条件。
两者都回链 match_root，但 source_type 分别为 controlled_rewrite 与 published_commentary，报告中不混算。

## 5. 当前批次

B019 C_adjudication，36 任务，36 个唯一键；gold 存在 tasks.gold_json，worker 直接读取，不依赖 scorecard 重新解析。


## 6. 首轮结果（B019，36 任务）

| 条件 | 五字段全对任务 | 主指标（A/B wickets + total） | 格准确率 |
|---|---:|---:|---:|
| C_change | 8/12 | 8/12 | 56/60 |
| C_maintain | 12/12 | 12/12 | 60/60 |
| C_no_notice | 12/12 | 12/12 | 60/60 |

- 总体 176/180 = 0.9778；模型：qwen 0.95、llama 0.9833、gemma 1.0。
- 错误全部集中在 C_change：正式改判后未把 A 的 wickets 减 1（qwen 4 vs gold 3），或 B 加多。
- C_maintain 与 C_no_notice 全对，说明“读旧记录”不是瓶颈；“正式改判后的传播”才是。
- 单批 4 事件、36 任务，不能外推为稳定效应。

## 7. 全样本批 B022

- 其余 4 个事件 × 3 条件 × 3 模型 = 36 任务，已冻结并在 B019 之后运行；与 B019 合计覆盖 8 个事件。

## 8. 8 事件合并结果（B019 + B022）

| 条件 | 任务全对 | 格正确 |
|---|---:|---:|
| C_change | 12/24 | 106/120 |
| C_maintain | 23/24 | 116/120 |
| C_no_notice | 24/24 | 120/120 |

- C_change 12/24，C_maintain 23/24，C_no_notice 24/24。
- 错误集中在正式改判后的 A−1/B+1 传播；C_maintain 仅有 1 次空答（match_0030 qwen null）。
- 结论：通知理解与旧值抽取不是主要瓶颈；正式改判后的数值传播才是。
