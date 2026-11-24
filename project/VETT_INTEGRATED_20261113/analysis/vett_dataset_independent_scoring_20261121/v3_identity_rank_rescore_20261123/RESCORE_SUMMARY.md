# VETT 评分 v3：独立离线重评摘要

## 结论

- 24 条陈旧 N1 内嵌分数已用当前冻结金标重评：43 字段/条，共 1,032 格；旧分正确 266 格，新分正确 342 格，净增 76。逐行旧分→新分及变更字段见 `n1_old_to_new_diff.csv`。
- 5 场 N2 通知后排名需要与当前 manifest 区分：2 场成员退出（`match_0008`、`match_0010`），3 场仅重排（`match_0012`、`match_0015`、`match_0030`）。本版本不改冻结 manifest，只输出语义修订表。
- 16 条畸形 JSON 的严格格式分均为 0；恢复器可提取内容后，5 条的目标球员身份数值正确，但没有一条 43 字段全对。它们因此不能被报告成“格式正确”或“整表全对”。
- 4 个评分回归案例与 5 个恢复器单元测试全部通过。35 个来源文件已登记 SHA-256，原始 JSONL 和旧分数未改写。

## N1 旧分→新分

| 模型 | 行数 | 旧正确格 | 新正确格 | 差值 | 身份任务全对 | 含顺序全对 |
|---|---:|---:|---:|---:|---:|---:|
| gemma2:9b | 8 | 48 | 116 | +68 | 2 | 2 |
| llama3.1:8b | 8 | 109 | 113 | +4 | 3 | 2 |
| qwen2.5:7b-instruct-q4_K_M | 8 | 109 | 113 | +4 | 0 | 0 |
| **合计** | **24** | **266** | **342** | **+76** | **5** | **4** |

净增不表示每行都上升：5 行各下降 1 格，原因可在 CSV 的 `changed_gold_detail` 逐字段核对。`match_0003` 的 Qwen N1 是典型错人：模型第二行写 Mason Cooper，Connor Reed 缺失；按人物身份判错，不能把 Mason 的“2”当作 Connor 的答案。

## N2 通知后排名决定

| 比赛 | 当前 manifest 两行 | 通知后语义 top-2 | 处理 |
|---|---|---|---|
| match_0008 | Luke Barrett 2/30；Ryan Frost 4/37 | Ryan Frost 4/37；Evan Reed 2/27 | Luke 退出，修订成员与顺序 |
| match_0010 | Ryan Foster 2/48；Evan Turner 3/38 | Evan Turner 3/38；Luke Barrett 2/38 | Ryan 退出，修订成员与顺序 |
| match_0012 | Caleb Brooks 3/56；Lucas Vale 3/44 | Lucas Vale 3/44；Caleb Brooks 3/56 | 仅重排 |
| match_0015 | Noah Grant 3/62；Caleb Rourke 3/41 | Caleb Rourke 3/41；Noah Grant 3/62 | 仅重排 |
| match_0030 | Logan Vale 3/10；Owen Price 3/1 | Owen Price 3/1；Logan Vale 3/10 | 仅重排 |

## 16 条畸形 JSON

- 分布：全部来自 Gemma 整表回答；严格格式 0/16，均由不看金标的词法恢复器处理。15 条恢复出 43 个唯一键，`match_0010` N2 因混入额外键恢复出 70 个唯一键且仍缺 6 个目标字段。
- 目标身份数值可恢复正确的 5 条为：`match_0003` N0/N1、`match_0017` N0/N1、`match_0026` N0。
- 当前 16 条未发现实际重复键或冲突值；该行为由独立单元测试覆盖。未来一旦出现冲突，相关字段记未定而非择值。

## 最小诊断 q1/q4 的 `/72` 分布

| 输入 | 通知 | q1 batter | q4 old |
|---|---|---:|---:|
| 全文 | N0 | 0/24 | 22/24 |
| 全文 | N1 | 0/24 | 22/24 |
| 全文 | N2 | 11/24 | 0/24 |
| **全文合计** |  | **11/72** | **44/72** |
| 窗口 | N0 | 6/24 | 23/24 |
| 窗口 | N1 | 8/24 | 23/24 |
| 窗口 | N2 | 22/24 | 10/24 |
| **窗口合计** |  | **36/72** | **56/72** |

逐模型分布在 `minimal_diag_q1_q4_distribution.csv`：全文 q1 的 11 个正确全部来自 N2（Llama 6、Gemma 5）；全文 q4 的 44 个正确全部来自 N0/N1，且两臂各 22。窗口 q1 随 N0→N1→N2 为 6→8→22；窗口 q4 为 23→23→10。

## 可复核产物

- `fulltable_rescore_rows.csv`：72 条整表逐行的旧分、严格格式、恢复内容、身份/集合/顺序/总数状态。
- `n1_old_to_new_diff.csv`：24 条 N1 逐行旧分→新分和字段级差异。
- `n2_rank_revision.csv`：5 场排名决定。
- `malformed_json_rescore.csv`：16 条严格/恢复双分。
- `minimal_diag_q1_q4_rows.csv` 与 `minimal_diag_q1_q4_distribution.csv`：288 条底表及 12 行分布。
- `rescored_lines.jsonl`：新版本 72 条机器可读逐行结果；不替换任何原始 run JSONL。
- `SOURCE_INVENTORY.csv`、`SOURCE_HASHES.json`：只读来源及完整性凭据。
