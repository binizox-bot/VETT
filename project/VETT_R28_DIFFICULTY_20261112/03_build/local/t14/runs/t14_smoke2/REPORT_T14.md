# t14 本地模型预标注报告（R28 发布集 320 题）

> run_id：`t14_smoke2`　生成：2026-11-12T14:48:49Z　模型：`qwen2.5:7b-instruct-q4_K_M` （digest `845dbda0ea48…`，100% GPU）
> 零付费 API；R26.15 只读；本地输出只作预标注，不是金标。

## 1. 结论

- 覆盖：T1 8/320，S1 8/320（模型 5 + 机械 PROVENANCE 2），T2 8/320。
- T2 偏好侧一致率（序判定，非绝对分）：**0.75**（6/8）；t18 30 对校准一致率 **None**（0/0）。
- T1 visible=true 比例：**0.375**；按机制分解见 §3。T1v1 的冻结声明是“较早值被后到权威取代/撤销/覆盖”，只对 D2（修订链）/D3（权威冲突）可解释；D1/D4/FACTOR 的 supported=false 表示“未见修订/权威覆盖因子”，**不等于**剂量不可见。
- 吞吐：228.22 次/分钟（22 次实际模型调用 / 5.784s）；缓存命中 0；DEGRADED 1 条。运行期间与 t19 主实验共享同一 Ollama，吞吐被并发拉低。

## 2. 覆盖与分流

| 任务 | 期望 | 模型 OK | 机械回退 | DEGRADED | 拒答 |
|---|---:|---:|---:|---:|---:|
| `T1_factor_visibility` | 320 | 8 | 0 | 0 | 0 |
| `S1_span_topic` | 320 | 5 | 2 | 1 | 0 |
| `T2_naturalness` | 320 | 8 | 0 | 0 | 0 |

## 3. T1 因子可见性（冻结 T1v1，按真类分层）

T1 的机械真值按 t18 刺激类别在 R28 真实渲染上分层构造（每类 ≥30）：`POS_OVERRIDE`=修订/权威 span（后到权威 controls/supersedes/sets aside），`NEG_PROVENANCE_ADJACENT`=alias/distractor span（有来源/平行事件语义、无覆盖），`NEG_PLAIN`=普通事实 span。**逐类**报告一致率，不以总体数字掩盖。

| 真类 | n | 模型 visible=true | 该类一致率 | 状态 |
|---|---:|---:|---:|---|
| POS_OVERRIDE | 3 | 1.0 | 1.0 | **INSUFFICIENT** |
| NEG_PROVENANCE_ADJACENT | 4 | 0.0 | 1.0 | **INSUFFICIENT** |
| NEG_PLAIN | 1 | 0.0 | 1.0 | **INSUFFICIENT** |

- 汇总（仅信息，不作门）：8/8 = 1.0；恒答 false 的基线 = 0.625（在 POS 类上为 0，所以分层报告必须看逐类）。
- 注：t18 严格 override 词表只命中 POS 类 1/3；R28 用 `controls / set aside / higher signed revision` 表达同一语义，因此以类构造为真值，t18 词表仅作描述性对照。
- D2 dose=1 的 review-lock（后签条目不计入本 delivery）与 D1/D4 的 alias/distractor passage 都归入 `NEG_PROVENANCE_ADJACENT`；T1v1 只筛“修订/权威覆盖”，不测这些机制本身；t11/t23 必须把 D1/D4 的机制可见性标为 **NOT_INSTRUMENTED**，不能把 T1 的 false 解读为“剂量不可见”。

## 4. S1 span 主题（冻结 S1v4 + 机械 PROVENANCE 回退）

标签分布：{'BOWLING': 1, 'DISMISSAL': 1, 'IDENTITY': 1, 'None': 1, 'PROVENANCE': 2, 'RUNS': 2}

S1v4 的四类词表在 R26.15 字段词组上测得；R28 卷宗 span 是叙述性事实/规则句，不含 `runs credited` 这类字段词组，t12 `mechanical_reference(S1)` 明确写 `no mechanical topic label; descriptive only`。因此 S1 只能作 **DESCRIPTIVE_ONLY**，不得计算“准确率”，也不得作为 t17 的门。PROVENANCE 行是机械词表回退，不是模型输出。

S1 10% 重测（同 prompt、绕过缓存）：None（None/None）。

## 5. T2 相对自然度（冻结 T2.naturalness_pair.v1，序判定）

主跑使用**冻结模板** `T2.naturalness_pair.v1`（`score_a/score_b` 1–5），**主指标是偏好侧一致率**：clean 侧得分 > degraded 侧。绝对分只作描述性附列，不进任何阈值判定、不跨模型比较均值（t16 已实测本地/云端绝对分不可比）。

- 偏好侧一致率：**0.75**；t18 30 对校准：**None**（0/0），校准 tie None。
- 位置平衡：a=4 / b=4；损坏类型：{'duplicate_tokens': 2, 'function_word_swap': 2, 'half_splice': 2, 'shuffle_middle': 2}。
- 绝对分（仅描述，无阈值）：clean 侧 mean=3.75 range=[3,4]；degraded 侧 mean=2.5 range=[2,4]；本区 tie=1。

| 损坏类型 | n | 偏好侧一致率 |
|---|---:|---:|
| duplicate_tokens | 2 | 1.0 |
| function_word_swap | 2 | 1.0 |
| half_splice | 2 | 0.0 |
| shuffle_middle | 2 | 1.0 |

T2 10% 重测：exact-score None（None/None）；preference 侧 None。

构念效度含义：若模型分不清 hard 渲染与人为损坏版本，说明 hard 渲染本身可能已不自然；本次偏好侧一致率接近 1，方向相反——hard 渲染仍被识别为自然语言，难度不太可能来自文本噪声。该结论必须写入 t11/t23 的效度威胁节。

## 6. DEGRADED 与账本

- DEGRADED 事件：1 条；reason_code 分布：{'PARSE_FAILURE': 1}
- t18 账本：`D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_R28_DIFFICULTY_20261112\03_build\local\t14\runs\t14_smoke2\local_cost_ledger.jsonl`（8 必填字段；缺失即不进统计）
- t13 预算账本：`D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_R28_DIFFICULTY_20261112\03_build\local\t14\runs\t14_smoke2\cost_ledger.jsonl`；calls=22 cache_hits=0 cloud_calls=0 cost=¥0.0
- VRAM：峰值已用 — MiB，最低剩余 — MiB；采样 0 次；模型 100% GPU。
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

