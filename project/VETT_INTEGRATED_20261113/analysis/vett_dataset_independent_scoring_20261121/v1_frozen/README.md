# VETT 数据集构建与独立评分 v1

状态：`FROZEN`。这是独立版本目录；没有写入历史数据库、SQLite、worker 或队列。

## 两个首批案例

1. `vett-dev-v1-0001`：`match_0047` 第一局。发布版原句“Ridgefield closed on 337 for 8”追到 scorecard 第一局 `Total` 行，得到 `inn1.total_runs=337`、`inn1.total_wickets=8`。普通开发样本，不是按错例挑选。
2. `vett-dev-v1-0002`：`match_0003` 第一局。Brandon Hale 的原始出局行追到 Evan Clarke，旧 bowling 格为 Evan `4/28`、Connor `1/28`；正式改判唯一更新为 `3/28`、`2/28`，局总仍为 8。历史错例。

两案均为开发根，并避开方法保留根 `match_0121`–`match_0160`。证据详见 `CASE_01_LONG_EVIDENCE.md`、`CASE_02_ATTRIBUTION.md` 与 `evidence_chain.jsonl`。

## 冻结小批次

- 模型可见：`model_inputs.jsonl`（5 条输入，条件码不泄漏语义或答案）。
- 评测端：`private_gold.jsonl`、`SCHEMA.json`、`score_frozen.py`。
- 预期 DSH 矩阵：5 条 × 3 模型 = 15 个回答。
- 评分器自测：6/6 通过；结果见 `selftest_results.json`。
- 冻结清单：`FROZEN_MANIFEST.json`；后续修改必须新建版本。

## 独立复算

- 8 个归属事件：改判 12/24，维持 24/24，同时正确 12/24，实际误转移 0/24，不可执行 0/24。
- 全文→窗口：错→对 3/12，对→错 0/12。
- 与旧评分差异：1 行，见 `INDEPENDENT_RECALC_DIFF.csv`；原始回答未改。

## 人工与下一批

- `blind_review_40/`：40 格题面与 6 场完整原文，隐藏金标和模型回答。
- `CANDIDATE_SCREENING.csv`：最多 8 个开发根的筛选清单与未覆盖原因。
- `SUPPORT_BOUNDARIES.md`：已能支持与仍需人工判断的结论。
