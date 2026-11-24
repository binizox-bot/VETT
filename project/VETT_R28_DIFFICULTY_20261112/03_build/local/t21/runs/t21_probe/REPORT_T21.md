# t21 本地模型审解释：证书逐句一致性 + 机械 FRE 可读性

> run：`t21_probe`　模型：`qwen2.5:7b-instruct-q4_K_M`；C1 ALLOW，R1 DENY。
> 零付费 API；R26.15 只读；本地输出是预标注，不是金标。

## 1. 结论

- 覆盖：**2 题 / 32 句**（每 item 8 个证书字段 × consistent/inconsistent）；模型 OK 32、DEGRADED 0。
- C1 一致率（机械真值）：**0.9375**；CONSISTENT 14/16，INCONSISTENT 16/16。
- 可读性：**全部机械 FRE**（n=32，mean=57.276，range=[18.94,66.4]，band 分布 {1: 1, 2: 3, 3: 4, 4: 24}）；**R1 本地模型调用 0 次**，fallback=flesch_reading_ease_band。
- 吞吐：279.21 次/分钟（66 次实际调用 / 14.183s）；缓存命中 0；DEGRADED 0。

## 2. 覆盖与路由

| 任务 | 路由 | 调用 | 结果 |
|---|---|---:|---|
| C1_cert_sentence_consistency | ALLOW（cap 2000） | 66 | OK 32 / DEGRADED 0 |
| R1_readability | **DENY** | **0** | 机械 FRE 分档；模型不参与 |

## 3. C1 逐句一致性

句子由证书 `decision_record_flat` 的 8 个字段机械构造：一致句使用记录值，不一致句使用确定性替换值；标签由记录值机械判定，不让模型自证。

| 字段 | n | 一致率 | field 回填准确率 |
|---|---:|---:|---:|
| batter_runs | 4 | 0.75 | 1.0 |
| bowler_runs | 4 | 1.0 | 1.0 |
| counts_in_over | 4 | 1.0 | 1.0 |
| delivery_status | 4 | 1.0 | 1.0 |
| dismissal | 4 | 0.75 | 1.0 |
| ledger.NO_BALL_EXTRA | 4 | 1.0 | 1.0 |
| ledger.WIDE_EXTRA | 4 | 1.0 | 1.0 |
| total_runs | 4 | 1.0 | 1.0 |

不一致样本（2 条）：

| item | sample | field | truth | predicted | sentence |
|---|---|---|---:|---:|---|
| r28q_0001 | r28q_0001:dismissal:C | dismissal | True | False | The certificate states that dismissal is "HIT_BALL_TWICE". |
| r28q_0001 | r28q_0001:batter_runs:C | batter_runs | True | False | The certificate states that batter_runs is 1. |

10% 重测：4 句，exact verdict agreement 1.0；full annotation agreement 1.0。
t18 C1 校准（30 句，机械真值）：30/30 = 1.0。

## 4. 可读性（R1 DENY → 机械 FRE）

R1 在 t18 能力矩阵为 DENY（agreement 0.667、ρ=−0.167、无区分度）。本任务**没有**让本地模型给可读性打分；所有可读性值来自 Flesch Reading Ease，按 `corpus.readability_band` 分档（1–5）。

- n=32；mean=57.276；min=18.94；max=66.4；band 分布={1: 1, 2: 3, 3: 4, 4: 24}。
- 机械来源：`local_inference.corpus.flesch_reading_ease` + `readability_band`；每行 `r1_model_call=false`, `fallback_used=flesch_reading_ease_band`。

## 5. 与云端 t16 的分歧

- 云端 t16 标注文件 `03_build/local/annotations/cloud_alpha.jsonl` 的任务计数：{'T3_adjudication': 12, 'T1_factor_visibility': 48, 'T2_naturalness': 16}；**没有 C1**。
- 状态：`NO_CLOUD_C1_IN_T16`；C1 云端分歧清单为空（不是 0 分歧，而是无同任务云端标签）。

## 6. DEGRADED 与账本

- DEGRADED 0 条；reason_code 分布 {}；fallback_used={}。
- t18 账本 `D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_R28_DIFFICULTY_20261112\03_build\local\t21\runs\t21_probe\local_cost_ledger.jsonl`；t13 预算账本 `D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_R28_DIFFICULTY_20261112\03_build\local\t21\runs\t21_probe\cost_ledger.jsonl`；cloud_calls=0、¥0。
- VRAM：peak=6002 MiB，free_min=2016 MiB；`ollama ps` 100% GPU。

## 7. 协议说明（诚实边界）

- C1 走 t18 已实测的 direct prompt（`tasks.build_prompt`）与冻结模板 `C1.cert_sentence_consistency.v1`；未改 temperature/seed。
- 冻结 `judge_protocol.canonical_record` 拒绝 bool 字段（`counts_in_over`），因此 C1 的 `build_blind_packet` 路径对 R28 12 字段记录不可用；t21 未修改 `02_design`，沿用 t18 C1 矩阵的 direct prompt。该协议缺口应报 t12/t17。
- 只读 `private/<id>/certificate.json`（被审对象）；未读 `private_gold.json` / `dossier_evidence.json`；不写真实金标。

## 8. 复现

```powershell
cd 03_build/local/t21
python t21_runner.py --run-id t21_main --execute
python t21_runner.py --run-id t21_main --acceptance
```
