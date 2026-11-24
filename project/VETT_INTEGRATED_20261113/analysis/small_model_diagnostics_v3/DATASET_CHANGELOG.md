# DATASET_CHANGELOG：v3

| 错例 | 改动 | 验收 |
|---|---|---|
| 正式改判 Qwen 0044 只改一侧 | 保留直接/两步配对，主指标两字段 | 两步 12/12 |
| retain Qwen 4 条决定矛盾 | schema 要求 retain 时 final=original | 程序拒绝，未误改 |
| retain Gemma 4 条旧值 UNKNOWN | 有旧汇总时 UNKNOWN 记漏抽 | 8/12 无法执行 |
| 直接 retain 11/12 | 保留直接组作为正控 | 反例 0042 Qwen |
| match_0008 total 漏判 | 队名去 XI/Women/CC 后比分句匹配 | 73→79，+6 |

下一版重点：retain 抽取协议与跨通知配对。
