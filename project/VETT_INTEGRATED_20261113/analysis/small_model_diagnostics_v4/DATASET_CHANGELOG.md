# DATASET_CHANGELOG：v4

| 错例 | 改动 | 验收 |
|---|---|---|
| Qwen 0044 被旧表误记 | 逐条 rescore，Qwen 0044 恢复正确 | 数值 10/12 |
| Qwen 4 条 retain decision 矛盾 | 按归属推导可重放为 retain | 维持 4→8 |
| Gemma 4 条旧值 UNKNOWN | 仍无法执行；新增旧值完整性要求 | 8/12 不可执行 |
| 新提示去 decision 后 Qwen other 旧值 UNKNOWN | 保留 decision 不是关键；两名旧值才是 | 新提示维持仍 4/12 |
| 0008 total 漏判 | 队名后缀归一化 | 73→79 |

下一版：retain 题面必须给出两人旧值；评分把“漏抽”和“合理 UNKNOWN”分开。
