# t14 本地模型预标注报告（R28 发布集 320 题）

> run_id：`t14_smoke`　生成：2026-11-12T12:56:37Z　模型：`qwen2.5:7b-instruct-q4_K_M` （digest `845dbda0ea48…`，100% GPU）
> 零付费 API；R26.15 只读；本地输出只作预标注，不是金标。

## 1. 结论

- 覆盖：T1 4/320，S1 4/320（模型 4 + 机械 PROVENANCE 0），T2 4/320。
- T2 选干净版本比例：**1.0**（4/4）；t18 30 对校准一致率 **None**（0/0）。
- T1 visible=true 比例：**0.0**；按机制分解见 §3。T1v1 的冻结声明是“较早值被后到权威取代/撤销/覆盖”，只对 D2（修订链）/D3（权威冲突）可解释；D1/D4/FACTOR 的 supported=false 表示“未见修订/权威覆盖因子”，**不等于**剂量不可见。
- 吞吐：3.31 次/分钟（12 次实际模型调用 / 217.742s）；缓存命中 0；DEGRADED 0 条。运行期间与 t19 主实验共享同一 Ollama，吞吐被并发拉低。

## 2. 覆盖与分流

| 任务 | 期望 | 模型 OK | 机械回退 | DEGRADED | 拒答 |
|---|---:|---:|---:|---:|---:|
| `T1_factor_visibility` | 320 | 4 | 0 | 0 | 0 |
| `S1_span_topic` | 320 | 4 | 0 | 0 | 0 |
| `T2_naturalness` | 320 | 4 | 0 | 0 | 0 |

## 3. T1 因子可见性（冻结 T1v1）

| 机制 | n | visible=true 比例 |
|---|---:|---:|
| FACTOR | 4 | 0.0 |

`T1v1` 与两种机械读数的对照（描述性，不是门）：

- 与 t18 严格 override 词表（R26.15 口径）：4/4；与 R28 authority 词表（supersedes/controls/set aside…）：4/4。
- D1/D4/FACTOR 的 passage 来自 alias/distractor/事实 span，冻结声明不覆盖这些机制；t11/t23 必须把它们标为 **NOT_INSTRUMENTED**，不能解读为“剂量不可见”。

## 4. S1 span 主题（冻结 S1v4 + 机械 PROVENANCE 回退）

标签分布：{'BOWLING': 2, 'RUNS': 2}

S1v4 的四类词表在 R26.15 字段词组上测得；R28 卷宗 span 是叙述性事实/规则句，不含 `runs credited` 这类字段词组，t12 `mechanical_reference(S1)` 明确写 `no mechanical topic label; descriptive only`。因此 S1 只能作 **DESCRIPTIVE_ONLY**，不得计算“准确率”，也不得作为 t17 的门。PROVENANCE 行是机械词表回退，不是模型输出。

S1 10% 重测（同 prompt、绕过缓存）：None（None/None）。

## 5. T2 相对自然度（hard 渲染 vs 确定性损坏）

**没有绝对自然度打分**：prompt 只要求二选一 `which is clean`，输出字段仅 `clean`。

- 干净版本选择率：**1.0**；t18 30 对校准：**None**（0/0）。
- 位置平衡：a=2 / b=2；损坏类型：{'duplicate_tokens': 1, 'function_word_swap': 1, 'half_splice': 1, 'shuffle_middle': 1}。

| 损坏类型 | n | 选对率 |
|---|---:|---:|
| duplicate_tokens | 1 | 1.0 |
| function_word_swap | 1 | 1.0 |
| half_splice | 1 | 1.0 |
| shuffle_middle | 1 | 1.0 |

T2 10% 重测：None（None/None）。

构念效度含义：若模型分不清 hard 渲染与人为损坏版本，说明 hard 渲染本身可能已不自然；本次选择率接近 1，方向相反——hard 渲染仍被识别为自然语言，难度不太可能来自文本噪声。该结论必须写入 t11/t23 的效度威胁节。

## 6. DEGRADED 与账本

- DEGRADED 事件：0 条；reason_code 分布：{}
- t18 账本：`D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_R28_DIFFICULTY_20261112\03_build\local\t14\runs\t14_smoke\local_cost_ledger.jsonl`（8 必填字段；缺失即不进统计）
- t13 预算账本：`D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_R28_DIFFICULTY_20261112\03_build\local\t14\runs\t14_smoke\cost_ledger.jsonl`；calls=12 cache_hits=0 cloud_calls=0 cost=¥0.0
- VRAM：峰值已用 — MiB，最低剩余 — MiB；采样 0 次；模型 100% GPU。

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

