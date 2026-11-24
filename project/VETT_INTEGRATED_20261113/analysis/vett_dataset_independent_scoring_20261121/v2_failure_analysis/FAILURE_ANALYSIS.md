# 正式改判失败：12 条逐行复核

筛选规则：`historical_line_scores.csv` 中 `condition=C_change` 且 `new_task_correct=False`。共 12 条，均已按 `source_file + source_line` 回到 B019/B022 原始回答。分类只描述可观察输出，不把单次输出解释为内部原因。

| 比赛 | 模型 | 旧值（原→新投手） | 正确新值 | 模型值 | 全队 wickets 旧/正确/模型 | 分类 | 同事件正确对照 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| match_0003 | qwen2.5:7b-instruct-q4_K_M | Evan Clarke 4/28 → Connor Reed 1/28 | 3/28 → 2/28 | 4/28 → 2/28 | 8/8/8 | 只改新投手 | gemma2:9b |
| match_0010 | llama3.1:8b | Ryan Foster 3/48 → Evan Turner 2/38 | 2/48 → 3/38 | 2/48 → 4/38 | 10/10/10 | 其他错值 | gemma2:9b |
| match_0010 | qwen2.5:7b-instruct-q4_K_M | Ryan Foster 3/48 → Evan Turner 2/38 | 2/48 → 3/38 | 2/48 → 4/38 | 10/10/10 | 其他错值 | gemma2:9b |
| match_0012 | llama3.1:8b | Caleb Brooks 4/56 → Lucas Vale 2/44 | 3/56 → 3/44 | 3/56 → 4/44 | 10/10/10 | 其他错值 | gemma2:9b |
| match_0012 | qwen2.5:7b-instruct-q4_K_M | Caleb Brooks 4/56 → Lucas Vale 2/44 | 3/56 → 3/44 | 4/56 → 4/44 | 10/10/10 | 其他错值 | gemma2:9b |
| match_0015 | llama3.1:8b | Noah Grant 4/62 → Caleb Rourke 2/41 | 3/62 → 3/41 | 3/62 → 4/41 | 10/10/10 | 其他错值 | gemma2:9b |
| match_0015 | qwen2.5:7b-instruct-q4_K_M | Noah Grant 4/62 → Caleb Rourke 2/41 | 3/62 → 3/41 | 3/62 → 4/41 | 10/10/10 | 其他错值 | gemma2:9b |
| match_0017 | qwen2.5:7b-instruct-q4_K_M | Miles Carter 5/18 → Liam Brooks 3/27 | 4/18 → 4/27 | 4/18 → 6/27 | 10/10/10 | 其他错值 | gemma2:9b |
| match_0026 | llama3.1:8b | Dylan Cole 5/5 → Ben Carter 2/5 | 4/5 → 3/5 | 4/5 → 4/5 | 10/10/10 | 其他错值 | gemma2:9b |
| match_0026 | qwen2.5:7b-instruct-q4_K_M | Dylan Cole 5/5 → Ben Carter 2/5 | 4/5 → 3/5 | 4/5 → 4/5 | 10/10/10 | 其他错值 | gemma2:9b |
| match_0030 | llama3.1:8b | Logan Vale 4/10 → Owen Price 2/1 | 3/10 → 3/1 | 3/10 → 4/1 | 10/10/10 | 其他错值 | gemma2:9b |
| match_0030 | qwen2.5:7b-instruct-q4_K_M | Logan Vale 4/10 → Owen Price 2/1 | 3/10 → 3/1 | 4/10 → 4/1 | 10/10/10 | 其他错值 | gemma2:9b |

## 分类汇总

| 分类 | 失败条数 | 独立比赛根 | 模型 |
| --- | ---: | ---: | --- |
| 沿用旧值 | 0 | 0 | — |
| 只改原投手 | 0 | 0 | — |
| 只改新投手 | 1 | 1 | qwen2.5:7b-instruct-q4_K_M |
| 方向反转 | 0 | 0 | — |
| 其他错值 | 11 | 6 | llama3.1:8b;qwen2.5:7b-instruct-q4_K_M |
| 信息不足 | 0 | 0 | — |

可观察到的集中形态：11 条“其他错值”全部把新投手 wickets 报得高于正确值，其中 10 条高 1、`match_0017` 高 2；9/11 同时把原投手正确减 1。剩余 1 条（`match_0003` Qwen）正确增加新投手，却沿用原投手旧值。该形态支持设计对照题，不足以单独判断模型为什么这样算。

逐行值、原始输出、哈希和行号见 `formal_change_failures_12.csv`；原始回答的结构化副本见 `historical_failure_raw_links.jsonl`。
