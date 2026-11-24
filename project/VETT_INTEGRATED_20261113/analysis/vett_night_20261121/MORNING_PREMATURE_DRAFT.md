# 夜间阶段验收报告（自动生成）

- 生成时间：2026-11-21T23:24:19+08:00
- 说明：本报告由本地脚本从 workflow.db 生成，不调用模型。

## 1. 昨晚实际跑了什么

- 核心比赛根：8；核心请求：144；核心完整配对（18/场）：24 组比赛×模型
- 整表回投请求：48；整表比赛×模型组：24
- 历史复用：0（本轮全部新请求）

## 2. 长文 vs 窗口（同事件）

| 比赛 | 模型 | 错→对 | 对→错 | 都对 | 都错 |
|---|---|---:|---:|---:|---:|
| match_0003 | Qwen | 0 | 1 | 2 | 0 |
| match_0003 | Llama | 1 | 0 | 2 | 0 |
| match_0003 | Gemma | 0 | 1 | 2 | 0 |
| match_0008 | Qwen | 1 | 0 | 1 | 1 |
| match_0008 | Llama | 2 | 0 | 0 | 1 |
| match_0008 | Gemma | 0 | 0 | 3 | 0 |
| match_0010 | Qwen | 0 | 0 | 2 | 1 |
| match_0010 | Llama | 2 | 0 | 0 | 1 |
| match_0010 | Gemma | 0 | 0 | 2 | 1 |
| match_0012 | Qwen | 0 | 0 | 2 | 1 |
| match_0012 | Llama | 0 | 0 | 2 | 1 |
| match_0012 | Gemma | 0 | 0 | 2 | 1 |
| match_0015 | Qwen | 1 | 0 | 1 | 1 |
| match_0015 | Llama | 0 | 0 | 0 | 3 |
| match_0015 | Gemma | 0 | 0 | 3 | 0 |
| match_0017 | Qwen | 0 | 0 | 2 | 1 |
| match_0017 | Llama | 3 | 0 | 0 | 0 |
| match_0017 | Gemma | 0 | 0 | 2 | 1 |
| match_0026 | Qwen | 0 | 1 | 2 | 0 |
| match_0026 | Llama | 0 | 0 | 2 | 1 |
| match_0026 | Gemma | 0 | 1 | 2 | 0 |
| match_0030 | Qwen | 0 | 0 | 3 | 0 |
| match_0030 | Llama | 0 | 0 | 0 | 3 |
| match_0030 | Gemma | 0 | 0 | 2 | 1 |

## 3. 错误分类

| 比赛 | 模型 | 条件 | 分类 | 原答片段 |
|---|---|---|---|---|
| match_0003 | Gemma | N2_W | only_new_plus1 | {"Evan Clarke_wickets": 4, "Evan Clarke_runs": 28, "Connor Reed_wickets": 2, "Co |
| match_0003 | Llama | N2_F | only_new_plus1 | ``` {   "Evan Clarke_wickets": 4,   "Evan Clarke_runs": 28,   "Connor Reed_wicke |
| match_0003 | Qwen | N2_W | only_new_plus1 | ```json {   "Evan Clarke_wickets": 4,   "Evan Clarke_runs": 28,   "Connor Reed_w |
| match_0008 | Llama | N0_F | both_old | ``` {   "Luke Barrett_wickets": 3,   "Luke Barrett_runs": 0,   "Ryan Frost_wicke |
| match_0008 | Llama | N1_F | both_old | ``` {   "Luke Barrett_wickets": 3,   "Luke Barrett_runs": 0,   "Ryan Frost_wicke |
| match_0008 | Llama | N2_F | other_value | ``` {   "Luke Barrett_wickets": 4,   "Luke Barrett_runs": 0,   "Ryan Frost_wicke |
| match_0008 | Llama | N2_W | other_value | ``` {   "Luke Barrett_wickets": 4,   "Luke Barrett_runs": 30,   "Ryan Frost_wick |
| match_0008 | Qwen | N1_F | both_old | ```json {   "Luke Barrett_wickets": 3,   "Luke Barrett_runs": 30,   "Ryan Frost_ |
| match_0008 | Qwen | N2_F | other_value | ```json {   "Luke Barrett_wickets": 4,   "Luke Barrett_runs": 30,   "Ryan Frost_ |
| match_0008 | Qwen | N2_W | only_new_plus1 | ```json {   "Luke Barrett_wickets": 3,   "Luke Barrett_runs": 30,   "Ryan Frost_ |
| match_0010 | Gemma | N2_F | only_new_plus1 | { "Ryan Foster_wickets": 3, "Ryan Foster_runs": 48, "Evan Turner_wickets": 3, "E |
| match_0010 | Gemma | N2_W | only_new_plus1 | {"Ryan Foster_wickets": 3, "Ryan Foster_runs": 48, "Evan Turner_wickets": 3, "Ev |
| match_0010 | Llama | N0_F | both_old | ``` {   "Ryan Foster_wickets": 3,   "Ryan Foster_runs": 0,   "Evan Turner_wicket |
| match_0010 | Llama | N1_F | both_old | ``` {   "Ryan Foster_wickets": 3,   "Ryan Foster_runs": 0,   "Evan Turner_wicket |
| match_0010 | Llama | N2_F | other_value | ``` {   "Ryan Foster_wickets": 4,   "Ryan Foster_runs": 0,   "Evan Turner_wicket |
| match_0010 | Llama | N2_W | other_value | ``` {   "Ryan Foster_wickets": 3,   "Ryan Foster_runs": 48,   "Evan Turner_wicke |
| match_0010 | Qwen | N2_F | other_value | ```json {   "Ryan Foster_wickets": 4,   "Ryan Foster_runs": 48,   "Evan Turner_w |
| match_0010 | Qwen | N2_W | other_value | ```json {     "Ryan Foster_wickets": 3,     "Ryan Foster_runs": 48,     "Evan Tu |
| match_0012 | Gemma | N2_F | only_new_plus1 | { "Caleb Brooks_wickets": 4, "Caleb Brooks_runs": 56, "Lucas Vale_wickets": 3, " |
| match_0012 | Gemma | N2_W | only_new_plus1 | {"Caleb Brooks_wickets": 4, "Caleb Brooks_runs": 56, "Lucas Vale_wickets": 3, "L |

## 4. 整表回投（目标两人 wickets）

| 比赛 | 模型 | 条件 | 两人 wickets（金标→预测） | 全队 total |
|---|---|---|---|---|
| match_0003 | Gemma | N1_F_fulltable |  | None→None |
| match_0003 | Gemma | N2_F_fulltable |  | None→None |
| match_0003 | Llama | N1_F_fulltable |  | None→None |
| match_0003 | Llama | N2_F_fulltable |  | None→None |
| match_0003 | Qwen | N1_F_fulltable |  | None→None |
| match_0003 | Qwen | N2_F_fulltable |  | None→None |
| match_0008 | Gemma | N1_F_fulltable |  | None→None |
| match_0008 | Gemma | N2_F_fulltable |  | None→None |
| match_0008 | Llama | N1_F_fulltable |  | None→None |
| match_0008 | Llama | N2_F_fulltable |  | None→None |
| match_0008 | Qwen | N1_F_fulltable |  | None→None |
| match_0008 | Qwen | N2_F_fulltable |  | None→None |

## 5. 结论与下一版建议

- 待人工判断：错误根因、窗口是否漏必要证据、整表其他字段是否改坏。
- 建议：只选一个优先项，等完整统计后再定。
