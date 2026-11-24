# SCORECARD_RESCORE_V4：258 字段

日期：2026-11-13。0 次模型调用。

## 1. 可答性

- V4 为 79/258（30.6%）：在 V3 73 格基础上，修正球队名后缀匹配（去掉 XI/Women/CC），新增 6 格。
- 新增例：match_0008 inn1.total_wickets 由 Coral Coast finished on 262 for eight 支持；V3 因球队名写成 Coral Coast XI 未匹配，V4 记 direct。
- 185 格中 6 格转 direct，其余 179 待核。
- 40 格盲审沿用 v1 全文本；人工未返回。

## 2. 同分母 79

| 模型 | 可答答对 | 分母 | 准确率 |
|---|---:|---:|---:|
| Qwen | 33 | 79 | 41.8% |
| Gemma | 38 | 79 | 48.1% |
| Llama | 26 | 73 | 35.6%（V4 79 未重算） |

Llama 的 V4 分母未重算：0008 空答、5 条嵌套 JSON 可恢复；当前只保留 V3 的 26/73，不能与 79 直接比较。

## 3. 逐场（Qwen/Gemma）

| match | 可答 V4 | Qwen | Gemma |
|---|---:|---:|---:|
| 0003 | 16 | 10 | 10 |
| 0008 | 13 | 6 | 6 |
| 0010 | 12 | 1 | 3 |
| 0012 | 11 | 4 | 6 |
| 0015 | 11 | 5 | 3 |
| 0017 | 11 | 4 | 5 |

## 4. 格式与闭合

- Qwen/Gemma 6/6 解析；Llama 旧协议 0/6，展平 5/6，0008 空。
- 闭合约束仍不可检查（schema 缺 extras 合计/bat_sum）。
- 旧口径 73/258 保留为历史对照；V4 79 的 6 格变化逐条在 FIELD_ANSWERABILITY_V4.jsonl 的 change_reason_v4。
