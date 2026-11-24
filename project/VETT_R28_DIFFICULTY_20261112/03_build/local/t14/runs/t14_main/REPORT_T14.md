# t14 本地模型预标注报告（R28 发布集 320 题）

> run_id：`t14_main`　生成：2026-11-12T15:15:03Z　模型：`qwen2.5:7b-instruct-q4_K_M` （digest `845dbda0ea48…`，100% GPU）
> 零付费 API；R26.15 只读；本地输出只作预标注，不是金标。

## 1. 结论

- 覆盖：T1 320/320，S1 320/320（模型 207 + 机械 PROVENANCE 96 + DEGRADED 17），T2 320/320。
- T2 偏好侧一致率（仅有效腐蚀对；序判定，非绝对分）：**0.9905**（314/317；`INEFFECTIVE_CORRUPTION` 已剔除 3 条）；t18 30 对校准 **1.0**（30/30）。
- T1 visible=true 比例：**0.125**；按机制分解见 §3。T1v1 的冻结声明是“较早值被后到权威取代/撤销/覆盖”，只对 D2（修订链）/D3（权威冲突）可解释；D1/D4/FACTOR 的 supported=false 表示“未见修订/权威覆盖因子”，**不等于**剂量不可见。
- 吞吐：277.27 次/分钟（905 次实际模型调用 / 195.836s）；缓存命中 71；DEGRADED 17 条。本次全量在 t19 结束后独占 GPU；此前 8 题 smoke 与 t19 并发时实测 3.29 calls/min（见 evidence/THROUGHPUT_GAP.json）。

## 2. 覆盖与分流

| 任务 | 期望 | 模型 OK | 机械回退 | DEGRADED | 拒答 |
|---|---:|---:|---:|---:|---:|
| `T1_factor_visibility` | 320 | 320 | 0 | 0 | 0 |
| `S1_span_topic` | 320 | 207 | 96 | 17 | 0 |
| `T2_naturalness` | 320 | 320 | 0 | 0 | 0 |

## 3. T1 因子可见性（冻结 T1v1，按真类分层）

T1 的机械真值按 t18 刺激类别在 R28 真实渲染上分层构造（每类 ≥30）：`POS_OVERRIDE`=修订/权威 span（后到权威 controls/supersedes/sets aside），`NEG_PROVENANCE_ADJACENT`=alias/distractor span（有来源/平行事件语义、无覆盖），`NEG_PLAIN`=普通事实 span。**逐类**报告一致率，不以总体数字掩盖。

| 真类 | n | 模型 visible=true | 该类一致率 | 状态 |
|---|---:|---:|---:|---|
| POS_OVERRIDE | 48 | 0.8333 | 0.8333 | OK |
| NEG_PROVENANCE_ADJACENT | 80 | 0.0 | 1.0 | OK |
| NEG_PLAIN | 192 | 0.0 | 1.0 | OK |

- 汇总（仅信息，不作门）：312/320 = 0.975；恒答 false 的基线 = 0.85（在 POS 类上为 0，所以分层报告必须看逐类）。
- 注：t18 严格 override 词表只命中 POS 类 16/48；R28 用 `controls / set aside / higher signed revision` 表达同一语义，因此以类构造为真值，t18 词表仅作描述性对照。
- D2 dose=1 的 review-lock（后签条目不计入本 delivery）与 D1/D4 的 alias/distractor passage 都归入 `NEG_PROVENANCE_ADJACENT`；T1v1 只筛“修订/权威覆盖”，不测这些机制本身；t11/t23 必须把 D1/D4 的机制可见性标为 **NOT_INSTRUMENTED**，不能把 T1 的 false 解读为“剂量不可见”。
- **机制归因（必须写死）**：POS 的 8 个错误来自 ['D3_authority_policy'] 变体；t18 严格 override 词表在这些错误上命中 0/8。T1 总体 0.975 相对 constant-false 基线 0.85 的余量只有 **+0.125**，来自**词表/模式匹配**，不能解读为“本地模型读懂了证据”。NEG 两类的 1.0 同样是“词表未命中即 false”的直接结果。
- T1 分歧样本（8 条）：

| item_id | 真类 | selection | model visible |
|---|---|---|---:|
| r28q_0242 | POS_OVERRIDE | D3_authority_policy | False |
| r28q_0248 | POS_OVERRIDE | D3_authority_policy | False |
| r28q_0250 | POS_OVERRIDE | D3_authority_policy | False |
| r28q_0253 | POS_OVERRIDE | D3_authority_policy | False |
| r28q_0254 | POS_OVERRIDE | D3_authority_policy | False |
| r28q_0264 | POS_OVERRIDE | D3_authority_policy | False |
| r28q_0271 | POS_OVERRIDE | D3_authority_policy | False |
| r28q_0272 | POS_OVERRIDE | D3_authority_policy | False |

## 4. S1 span 主题（冻结 S1v4 + 机械 PROVENANCE 回退）

标签分布：{'BOWLING': 30, 'DISMISSAL': 40, 'IDENTITY': 40, 'None': 17, 'PROVENANCE': 96, 'RUNS': 97}

S1v4 的四类词表在 R26.15 字段词组上测得；R28 卷宗 span 是叙述性事实/规则句，不含 `runs credited` 这类字段词组，t12 `mechanical_reference(S1)` 明确写 `no mechanical topic label; descriptive only`。因此 S1 只能作 **DESCRIPTIVE_ONLY**，不得计算“准确率”，也不得作为 t17 的门。PROVENANCE 行是机械词表回退，不是模型输出。

S1 10% 重测（同 prompt、绕过缓存）：1.0（18/18）。
- S1 DEGRADED 17 条：reason_code=PARSE_FAILURE，fallback_used=mechanical；ids：r28q_0066, r28q_0068, r28q_0071, r28q_0074, r28q_0080, r28q_0101, r28q_0103, r28q_0105, r28q_0147, r28q_0152, r28q_0153, r28q_0161, r28q_0163, r28q_0169, r28q_0172, r28q_0173, r28q_0175

## 5. T2 相对自然度（冻结 T2.naturalness_pair.v1，序判定）

主跑使用**冻结模板** `T2.naturalness_pair.v1`（`score_a/score_b` 1–5），**主指标是有效腐蚀对上的偏好侧一致率**：clean 侧得分 > degraded 侧。绝对分只作描述性附列，不进任何阈值判定、不跨模型比较均值。

- 有效对 **317**，`INEFFECTIVE_CORRUPTION` 剔除 **3**；偏好侧一致率 **0.9905**；t18 30 对校准 **1.0**（30/30；tie 0）。
- `INEFFECTIVE_CORRUPTION` ids：r28q_0067, r28q_0099, r28q_0159；原因均为 function_word_swap 在某些句子上未引入可测断裂（syntax_break_delta=0 且 bigram_delta<0.05），已剔除出分母，不计模型失败。
- T2 有效对分歧（3 条）：r28q_0172(half_splice, clean=2, degraded=4)；r28q_0204(half_splice, clean=2, degraded=3)；r28q_0240(half_splice, clean=3, degraded=4)
- 位置平衡：a=160 / b=160；损坏类型：{'duplicate_tokens': 80, 'function_word_swap': 80, 'half_splice': 80, 'shuffle_middle': 80}。
- 绝对分（仅描述，无阈值）：clean 侧 mean=4.262 range=[2,5]；degraded 侧 mean=2.057 range=[1,4]；有效区 tie=0。

| 损坏类型 | 全部 n | 有效 n | 偏好侧一致率 | ineffective |
|---|---:|---:|---:|---:|
| duplicate_tokens | 80 | 80 | 1.0 | 0 |
| function_word_swap | 80 | 77 | 1.0 | 3 |
| half_splice | 80 | 80 | 0.9625 | 0 |
| shuffle_middle | 80 | 80 | 1.0 | 0 |

机械代理（每条 pair 记录；`INEFFECTIVE_CORRUPTION` = degraded==natural 或 `syntax_break_delta<=0` 且 `bigram_delta<0.05`）：

| 损坏类型 | n | syntax_break_delta min/med/max | bigram_delta min/med/max | FRE delta med | ineffective |
|---|---:|---:|---:|---:|---:|
| duplicate_tokens | 80 | 3.0 / 10.0 / 17.0 | 0.235385 / 0.342309 / 0.613439 | 3.971 | 0 |
| function_word_swap | 80 | 0.0 / 3.0 / 6.0 | -0.31016 / 0.543084 / 1.323573 | -9.196 | 3 |
| half_splice | 80 | 1.0 / 1.0 / 1.0 | -0.02363 / 0.048156 / 0.3301 | -11.673 | 0 |
| shuffle_middle | 80 | -2.0 / 2.0 / 6.0 | 0.198999 / 1.235214 / 2.423076 | 0.0 | 0 |

**修复前后对照（同一 8 题 smoke）**：

| 版本 | 总偏好侧一致率 | half_splice |
|---|---:|---:|
| 修复前（多句 half_splice） | 6/8 | 0/2 |
| 修复后（单句 half_splice，仅有效对） | 7/8 | 1/2 |

**仪器变更披露**：修复前 6/8 中的 2 个失败来自多句 `half_splice` 退化为 B+A（文本仍自然）；修复后若通过率上升，上升来自**腐蚀器变更**，不是模型能力变化。逐损坏类型的前后对照：

| 损坏类型 | 修复前 | 修复后（有效对） |
|---|---:|---:|
| duplicate_tokens | 2/2 | 2/2 |
| function_word_swap | 2/2 | 2/2 |
| half_splice | 0/2 | 1/2 |
| shuffle_middle | 2/2 | 2/2 |

T2 10% 重测：exact-score 1.0（32/32）；preference 侧 1.0。

构念效度含义：若模型在有效腐蚀对上分不清 hard 渲染与损坏版本，说明 hard 渲染本身可能已不自然；本次有效对偏好侧一致率见上。**附录经验（腐蚀器设计）**：对多句 excerpt，`half_splice` 在句界交换半段只得到 B+A，语义与句法都仍自然，是无效负对照；`half_splice` 必须取单句长 span，并用 `syntax_break_delta` 验证。FRE 对词序不变，不能作该損坏的机械代理。该教训写入 t11/t23 效度威胁节。

## 6. DEGRADED 与账本

- DEGRADED 事件：17 条；reason_code 分布：{'PARSE_FAILURE': 17}；fallback_used 分布：{'mechanical': 17}
- t18 账本：`D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_R28_DIFFICULTY_20261112\03_build\local\t14\runs\t14_main\local_cost_ledger.jsonl`（8 必填字段；缺失即不进统计）
- t13 预算账本：`D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_R28_DIFFICULTY_20261112\03_build\local\t14\runs\t14_main\cost_ledger.jsonl`；calls=976 cache_hits=71 cloud_calls=0 cost=¥0.0
- VRAM：峰值已用 6056 MiB，最低剩余 1962 MiB；采样 0 次；模型 100% GPU。
- **吞吐口径（方法节）**：t18 能力矩阵 207.89 calls/min 是短输出（`num_predict` ≤128）；t19 E1 生成完整 12 字段（约 225 tokens）实测约 9 calls/min，差约 23×。用 200+/min 估算长生成任务会严重偏低；本次与 t19 共享 GPU 时 t14 也降到个位数 calls/min。证据见 `evidence/THROUGHPUT_GAP.json` 与 `evidence/VRAM_EVENT_20261112.json`。

## 7. 与 t16/t17/t21 的接口

- 标注文件：`annotations_T1.jsonl` / `annotations_S1.jsonl` / `annotations_T2.jsonl`；每行含 `item_id`、`item_handle`、`input_sha256`、`raw_output`（模型行）、`prompt_template_version`、`parsed_output`、`status`。
- `t2_pairs.json` 含 natural/degraded 文本与 corruptor/位置，可字节级重放；`t1_analysis.json` / `s1_analysis.json` 含机制分层（不含金标）。
- t17 J 门可直接用本目录；但 S1 只能 DESCRIPTIVE_ONLY，T1 只对 D2/D3 可解释。

## 8. 复现

```powershell
cd 03_build/local/t14
python t14_runner.py --dry-run      # 只构造/审计盲包与 token 预算
python t14_runner.py --execute      # 全量（缓存命中则零推理）
python t14_runner.py --acceptance   # 重算验收
```

