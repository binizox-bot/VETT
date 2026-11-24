# R28 人工双标一致性报告（自动生成）

- 生成时间：2026-11-12T11:59:05Z
- 标注者 A：100 题；标注者 B：100 题
- 共同题数：100；样本完整：True
- 门槛：每维原始一致率 ≥ 98%；H1 = **True**

## 逐维一致率

| 维度 | n | 原始一致率 | Cohen κ | κ 95% CI | PABAK | 正例一致率 | 分歧数 | 门 |
|---|---:|---:|---:|---|---:|---:|---:|:--:|
| value | 100 | 98.0000% | 0.3289 | [0.000, 0.497] | 0.9700 | 98.0000% | 2 | PASS |
| scope | 100 | 98.0000% | -0.0101 | [-0.025, 0.000] | 0.9700 | 98.0000% | 2 | PASS |
| rule_version | 100 | 99.0000% | 0.0000 | [0.000, 0.000] | 0.9850 | 99.0000% | 1 | PASS |
| proof | 100 | 98.0000% | -0.0050 | [-0.012, 0.000] | 0.9750 | 98.0000% | 2 | PASS |

## 逐字段值一致率（12 字段）

| 字段 | 一致率 | 分歧数 |
|---|---:|---:|
| batter_runs | 99.0000% | 1 |
| bowler_runs | 100.0000% | 0 |
| counts_in_over | 100.0000% | 0 |
| delivery_status | 100.0000% | 0 |
| dismissal | 100.0000% | 0 |
| ledger.BATTER | 100.0000% | 0 |
| ledger.BYE | 100.0000% | 0 |
| ledger.LEG_BYE | 100.0000% | 0 |
| ledger.NO_BALL_EXTRA | 100.0000% | 0 |
| ledger.PENALTY | 100.0000% | 0 |
| ledger.WIDE_EXTRA | 100.0000% | 0 |
| total_runs | 99.0000% | 1 |

- 四维全同题比例：93.0000%
- 分歧总数：9（其中字段级 2）

## 解释与限制

- Cohen's kappa is reported but is not the gate when agreement is near the ceiling; PABAK and raw agreement are shown for transparency.
- A kappa of null means both raters used one identical category for every item (expected agreement 1); this is a mathematical ceiling, not a disagreement.
- The disagreement list is the adjudication queue; no item may be declared verified while a critical disagreement is pending.

> 本报告只统计一致性，不产生人工金标；金标始终是确定性 solver 输出。
> 本文件由 `scripts/agreement.py` 生成，禁止手改；分歧清单见 `disagreements.jsonl`。
