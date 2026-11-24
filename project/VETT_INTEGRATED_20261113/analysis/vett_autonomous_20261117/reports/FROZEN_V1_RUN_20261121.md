# Codex v1_frozen 首批运行报告（B212）

- 运行目录：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_dataset_independent_scoring_20261121\run_dsh_v1
- 批次：B212（独立运行目录 run_dsh_v1；工作流队列 0，批次边界接入）
- 冻结版本：v1_frozen_20261121；FROZEN_MANIFEST sha256：e53c21f498295ea8348ee4db53c8c23950725ac6e53af8a58c3a59fde53230c3

## 5 个输入

| sample_id | 比赛 | 局 | 条件 | 文本版本 | 配对 |
|---|---|---:|---|---|---|
| vett-dev-v1-0001-c00 | match_0047 | 1 | full_published_commentary | 发布版 commentary 全文（8789 字符） | 长文-窗口配对（全文） |
| vett-dev-v1-0001-c01 | match_0047 | 1 | verbatim_evidence_window | 同一原文逐字证据窗（442 字符） | 长文-窗口配对（同源窗口） |
| vett-dev-v1-0002-c10 | match_0003 | 1 | formal_reassignment | scorecard 旧值快照 + 正式改判通知 | 三臂（正式改判） |
| vett-dev-v1-0002-c11 | match_0003 | 1 | maintain_original | scorecard 旧值快照 + 维持通知 | 三臂（维持） |
| vett-dev-v1-0002-c12 | match_0003 | 1 | no_notice | scorecard 旧值快照，无通知 | 三臂（无通知） |

## 计数

| 计划 | 复用 | 新增 | 收到响应 | 可评分 | 缺失 | 完整配对 |
|---:|---:|---:|---:|---:|---:|---|
| 15 | 0 | 15 | 15 | 15 | 0 | 3 长文配对 + 3 三臂组 |

- 任务全对：15/15；字段正确：57/57。
- 截断：0；done_reason=stop：15/15。
- prompt_sha 不符：0；模型名不符：0；digest 不符：0；decode 不符：0。

## 导出

- D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_dataset_independent_scoring_20261121\export_to_codex_v1\frozen_v1_B212_export.zip
- raw.jsonl / scores.jsonl / RUN_MANIFEST.json / SHA256SUMS.txt
