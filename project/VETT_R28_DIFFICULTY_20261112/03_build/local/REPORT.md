# R28 本地推理服务固化 · 能力矩阵 · 路由卡 · 成本账本（t18）

> 生成时间：2026-11-12T10:33:43Z　模型：`qwen2.5:7b-instruct-q4_K_M`（Q4_K_M / 7.6B / digest `845dbda0ea48…`）
> 角色：`local_operator`（t18）　零付费 API　R26.15 零字节改动

## 1. 一句话结论

本地 7B 在 4 类白名单任务上达到机械真值一致率 ≥0.85（T1_factor_visibility, T2_naturalness, S1_span_topic, C1_cert_sentence_consistency）；1 类未达标并已 DENY（R1_readability）。它被固化为**标注劳动力**，不是求解器：12 字段推导、置信度、仲裁与统计推断全部 DENY。

## 2. 服务固化

| 项 | 值 |
|---|---|
| 模型 tag | `qwen2.5:7b-instruct-q4_K_M` |
| 量化 / 参数量 | Q4_K_M / 7.6B |
| 模型 digest | `845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e` |
| Ollama 版本 | 0.40.16 |
| GPU | NVIDIA GeForce RTX 3070 (8192 MiB) |
| 驻留 | 100.0% GPU（size_vram=5148633988 B） |
| 解码 | temperature=0.0, seed=20261112, num_ctx=8192, keep_alive=30m |
| 超时 / 重试 | 180.0s / 2 retries（指数退避 [1.0, 2.0]s） |
| 启动检查 | ollama exe · HTTP · 模型 tag/quant · VRAM ≥1536 MiB · `ollama ps` 必须 100% GPU |

## 3. 数据完整性（只读源）

- R26.15：165 文件 / 93346177 字节，聚合 `343afde4c91d7785f42296074ecea685d5d466260674ab5a8c3bc37323d851bd`，`unchanged=True`
- 矩阵运行前后两次校验一致；测前即断言基线未被改动，否则拒绝测量。

## 4. 能力矩阵（E6，机械真值）

协议：seed=20261112，每任务 n≥30，阈值 0.85，温度 0；样本来自 R26.15 只读语料，真值由构造决定（非模型自评）。

| 任务 | n | 一致率 | 阈值 | 判定 | p50 / p95 (s) | 解析失败率 | 附加指标 |
|---|---:|---:|---:|---|---:|---:|---|
| `T1_factor_visibility` | 30 | 0.933 | 0.85 | **ALLOW** | 0.19 / 0.89 | 0.000 |  |
| `T2_naturalness` | 30 | 1.000 | 0.85 | **ALLOW** | 0.21 / 0.24 | 0.000 | retest=1.0 (n=10) |
| `S1_span_topic` | 32 | 1.000 | 0.85 | **ALLOW** | 0.15 / 0.16 | 0.000 |  |
| `C1_cert_sentence_consistency` | 30 | 1.000 | 0.85 | **ALLOW** | 0.22 / 0.24 | 0.000 |  |
| `R1_readability` | 30 | 0.667 | 0.85 | **DENY** | 0.31 / 0.42 | 0.000 | τ=1 exact=0.2333 ρ=-0.1672 distinct=3 |

逐组一致率：

- `T1_factor_visibility`：NEG_PLAIN=1.0(n=10), NEG_PROVENANCE_ADJACENT=1.0(n=10), POS_OVERRIDE=0.8(n=10)
- `T2_naturalness`：duplicate_tokens=1.0(n=8), function_word_swap=1.0(n=7), half_splice=1.0(n=7), shuffle_middle=1.0(n=8)
- `S1_span_topic`：BOWLING=1.0(n=8), DISMISSAL=1.0(n=8), IDENTITY=1.0(n=8), RUNS=1.0(n=8)
- `C1_cert_sentence_consistency`：CONSISTENT=1.0(n=15), INCONSISTENT=1.0(n=15)
- `R1_readability`：BAND_1=0.3333(n=6), BAND_2=0.6(n=10), BAND_3=1.0(n=10), BAND_4=0.5(n=4)

- **R1_readability DENY**：agreement 0.667 on n=30 (threshold 0.85); discrimination_ok=False rho=-0.1672; failed checks: agreement_ge_threshold, discrimination_ok

## 5. 路由卡（ALLOW / DENY）

| 任务 | 判定 | 输入上限（token） | 期望耗时 p50 | 校验方 | 失败回退 |
|---|---|---:|---:|---|---|
| `C1_cert_sentence_consistency` | **ALLOW** | 2000 | 0.22 | mechanical_truth | deterministic_solver_certificate |
| `D1_12_field_record_derivation` | **DENY** | — | — | none | deterministic solver / private gold |
| `D2_confidence_output` | **DENY** | — | — | none | discard confidence; calibrate mechanically if needed |
| `D3_kappa_arbitration` | **DENY** | — | — | none | judge_architect / measurement_auditor |
| `D4_statistical_inference` | **DENY** | — | — | none | deterministic statistics code |
| `D5_contract_or_code_design` | **DENY** | — | — | none | data_designer / data_engineer / pipeline_engineer |
| `D6_input_over_8k_tokens` | **DENY** | 8192 | 17.70 | hard refusal (no silent truncation) | reject with InputCapExceeded / DEGRADED |
| `D7_draft_without_solver_check` | **DENY** | 8192 | — | deterministic solver must verify every draft | solver check; reject unverified drafts |
| `D8_T3_adjudication` | **DENY** | — | — | cloud annotator + judge | annotator_alpha (cloud, sampled) |
| `R1_readability` | **DENY** | 2000 | 0.31 | mechanical_truth+retest | flesch_reading_ease_band |
| `S1_span_topic` | **ALLOW** | 1000 | 0.15 | mechanical_truth | mechanical_lexicon_rule |
| `T1_factor_visibility` | **ALLOW** | 3000 | 0.19 | mechanical_truth | mechanical_lexicon_rule |
| `T2_naturalness` | **ALLOW** | 2000 | 0.21 | retest_consistency+mechanical_truth | mechanical_corruption_proxy |

DENY 依据（实测，不是猜测）：

- 12 字段推导：40K 下信息字段 4.20/9 **低于**常数先验 4.77/9；80K 仅 4.55/9 且 17.7 s/题 → 模型是劳动力不是求解器。
- 置信度：均值 60.53（应在 0–1），输出不可用 → 一律丢弃，不得进入校准/risk–coverage/统计。
- 长上下文：80K 输入 17.7 s 且无增益 → 硬上限 8K token；超限拒绝，绝不静默截断。
- 仲裁 / 统计 / 合同 / 代码设计：属角色隔离与统计推断，本地模型无资格。

## 6. 成本账本与吞吐

- 账本：`D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_R28_DIFFICULTY_20261112\03_build\local\cost_ledger.jsonl`，457 条调用记录，完整 457 条，可用 457 条，被排除 0 条（缺任一必填字段即不得进入统计）
- 必填字段：`input_sha256 / prompt_template_version / temperature / seed / model_tag / raw_output / parsed_output / wall_clock`
- 成本：¥0.0（本地 GPU，零付费 API；账本记录 token 数用于容量规划）
- 矩阵吞吐：207.89 次/分钟；实际调用 162，缓存命中 0，失败 0
- VRAM：峰值已用 6388 MiB，最低剩余 1630 MiB；全程 100% GPU：True

## 7. 降级接口（供 t13）

- `local_inference.api.annotate(task, sample)`：ALLOW 任务返回 `status=OK` + 完整账本条目；不达标/超限/服务故障/解析失败返回 `status=DEGRADED` 并写 `DEGRADED_EVENTS.jsonl`。
- 能力门在调用时从 `capability_matrix.json` 重新判定；未测或 <0.85 一律 fail-safe DENY。
- 自检：PASS；覆盖 8 条路径，reason codes = ['CAPABILITY_BELOW_THRESHOLD', 'CAPABILITY_UNMEASURED', 'INPUT_CAP_EXCEEDED', 'MEASURED_BELOW_PRIOR', 'NO_INPUT', 'PARSE_FAILURE', 'SERVICE_UNAVAILABLE']
- 生产 DEGRADED 事件：0 条（若无 t13 调用则为 0，符合预期）

## 8. 这次哪些任务交给了本地模型、哪些没给

**给了（仅白名单）**：`T1_factor_visibility`、`T2_naturalness`、`S1_span_topic`、`C1_cert_sentence_consistency`

**没给（DENY）**：12 字段记录推导、置信度输出、kappa/仲裁、统计推断、合同与代码设计、>8K token 输入、T3 提报裁定、未经 solver 校验的草稿发布。

## 9. 可重跑

```powershell
# 1) 启动检查 + 100% GPU 驻留验证
python -m local_inference preflight
# 2) 能力矩阵（固定 seed；调用自动缓存，重跑不再消耗 GPU）
python -m local_inference matrix
# 3) 由矩阵生成路由卡
python -m local_inference routing
# 4) 独立一致性校验（含 cache-only 矩阵重建 + DEGRADED 自检）
python -m local_inference verify
```

矩阵摘要 `summary_digest = d3fac3cf2f1390d04b3198773d6d26dd19dd98a51254d43b887099ccf171c8b4`；cache-only 重建必须得到同一 digest（verify 第 9 项）。

独立第二次重跑：digest 相同 = True，一致率/判定相同 = True；第二次仅实调用 10 次（T2 retest），缓存命中 152 次。证据：`D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_R28_DIFFICULTY_20261112\03_build\local\runs\repro\rerun_evidence.json`

## 10. 验收对照

`verify`：17/17 项通过，overall PASS。

| 检查 | 结果 |
|---|---|
| `matrix_present` | PASS |
| `matrix_dataset_unchanged` | PASS |
| `dataset_still_unchanged` | PASS |
| `matrix_gate_consistent` | PASS |
| `matrix_digest_stable` | PASS |
| `routing_card_present` | PASS |
| `routing_card_matches_code` | PASS |
| `routing_task_set` | PASS |
| `routing_allow_measured` | PASS |
| `deny_reasons_cite_evidence` | PASS |
| `runtime_assertions_match_card` | PASS |
| `ledger_fields_complete` | PASS |
| `ledger_frozen_parameters` | PASS |
| `matrix_prompts_cached_and_ledgered` | PASS |
| `matrix_rebuild_from_cache_identical` | PASS |
| `degraded_interface_selftest` | PASS |
| `service_snapshot_recorded` | PASS |

## 11. 局限（如实声明）

- 五类任务的机械真值是**构造代理**：T1=修订/权威覆盖因子可见性（模板族构造），T2=干净句 vs 确定性损坏句的配对序，S1=单字段词组 span 的四类主题真值（RUNS/DISMISSAL/BOWLING/IDENTITY；provenance/修订类由 T1 覆盖），C1=证书句与记录的一致性构造，R1=Flesch Reading Ease 分档（±1 容差）。它们检验的是“能否稳定做闭环判断”，不等价于人类语义判断。
- R1 仅覆盖 R26.15 文本的 FRE 1–4 档（无第 5 档样本），因此只声称该区间的可辨识性。
- 本地 7B 的任何输出都不构成金标；金标仍由确定性 solver / 机械真值提供。
- **确定性边界**：temperature=0 + 固定 seed 在 Ollama 会话间不是逐位确定；独立两次运行中 152 个样本有 1 个 5 分制分数移动 1 分（判定未变，gate_unchanged=True）。因此 `summary_digest` 覆盖门判定/一致率/分组/样本集，不覆盖单条分数诊断；单条 raw output 仍在账本中逐条可重放。证据：`D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_R28_DIFFICULTY_20261112\03_build\local\runs\repro\nondeterminism_evidence.json`

