# t14 本地模型预标注（R28 发布集 320 题）

> 执行者：`local_operator`　模型：`qwen2.5:7b-instruct-q4_K_M`（RTX 3070，100% GPU）
> 范围：`03_build/local/t14/`（只读 R28 数据集 / t18 服务 / t13 缓存与账本 / t12 盲包审计）
> 零付费 API、零网络；本地输出只作**预标注**，不是金标。

## 1. 三个任务

| 任务 | 输入 | 模型输出 | 机械真值 / 指标 |
|---|---|---|---|
| `T1_factor_visibility` | 单条证据 passage | `{supported:bool, evidence:str}` → 映射 `visible` | **按真类分层**：`POS_OVERRIDE` / `NEG_PROVENANCE_ADJACENT` / `NEG_PLAIN`，每类 ≥30；逐类一致率 |
| `S1_span_topic` | 证书首条 minimum-evidence span | `{topic}` ∈ BOWLING/DISMISSAL/IDENTITY/RUNS | 无机械主题真值 → **DESCRIPTIVE_ONLY**；PROVENANCE 由机械词表回退 |
| `T2_naturalness` | hard 渲染片段 + 确定性损坏配对（位置平衡） | `{score_a, score_b}` 1–5（冻结 `T2.naturalness_pair.v1`） | **序判定**：clean 侧得分 > degraded 侧；绝对分只作描述性附列 |

### 1.1 T1 真类分层（修复“恒定真值”）

R28 真实渲染上的 320 条 passage 按 t18 刺激类别构造：

| 真类 | n | 构造 |
|---|---:|---|
| `POS_OVERRIDE` | 48 | D2 dose≥2 的 revision_version（含 t18 override 词 `supersedes`）；D3 dose>0 的 authority_policy（controls/set aside/outranks） |
| `NEG_PROVENANCE_ADJACENT` | 80 | D2 dose=1 的 temporal review lock（later entry excluded，方向相反，**不是** POS）；D1 dose>0 的 alias locator/bridge；D4 dose>0 的 distractor |
| `NEG_PLAIN` | 192 | 普通 fact span（无 override / authority / provenance 标记） |

每类 ≥30；报告逐类一致率。若某类不足 30，报告标 `INSUFFICIENT`，不用其他类凑数。
D1/D4 的机制本身**不被 T1v1 覆盖**（T1v1 只筛修订/权威覆盖），报告须标 `NOT_INSTRUMENTED`。
D2 dose=1 的 review-lock 语义是“后签条目不计入本 delivery”，与 t18 的“较早值被后到权威取代”方向相反，
因此不能算 POS——这是 fake-execute 测试抓到的真值错误，已修正。

### 1.2 T2 冻结模板（回退 captain 裁决）

- 使用冻结协议模板 `T2.naturalness_pair.v1`：`score_a/score_b` 1–5；**不用**任何二选一/绝对阈值变体。
- 主指标 = **有效腐蚀对**上的偏好侧一致率（`clean_score > degraded_score`）；tie 单列。
- 绝对分只作描述性附列（clean/degraded 均值与范围），不进任何阈值判定，不跨模型比较均值。
- 損坏器沿用 t18 四种：`duplicate_tokens / function_word_swap / half_splice / shuffle_middle`，每类 80 条；位置 a/b 各 160，shuffle 由固定 seed 决定，记录在案、可重放。
- **腐蚀器有效性（captain 约束）**：每条 pair 记录机械代理 `syntax_break_delta`（主，词序敏感）与 `bigram_delta`（R28 语料 bigram log-prob drop，次），FRE 差值仅记录不作门（词序不变）。`INEFFECTIVE_CORRUPTION` = degraded==natural 或 `syntax_break_delta<=0` 且 `bigram_delta<0.05`；这类 pair **从该类型分母剔除，不计模型失败**。
- **half_splice 修正**：多句 excerpt 上交换两半常退化成 B+A（仍自然）；修复后 half_splice 只取**单句长 span**（中点 token 必须小写），全量 80/80 有效。其余三种損坏算法一字未改。
- 修复前后 8 题 smoke：6/8（half 0/2）→ 7/8（half 1/2）；若通过率上升，明确归因于**腐蚀器变更**，不是模型能力变化。

## 2. 工程链路

- 读题：`03_build/dataset_r28/build_index.json` 的 320 条 `split=development`。
- 盲包：`judge_protocol.build_blind_packet` + `audit_packet`（payload 白名单、40+ 禁用键、7 条内容正则）；salt 只存在 `runs/<run_id>/config.json`，不进任何报告/证据。
- 门：`judge_protocol.assert_local_allowed`（ALLOW 集合 + 任务 token 上限 + 8192 硬顶；超限拒绝，不截断）。
- 缓存/账本：t13 `ContentAddressedCache`（vett-judge-cache/v1，model_digest 绑定）+ `BudgetLedger`（`cost_ledger.jsonl`，cloud cap=0）；t18 `ledger.build_entry` 落 `local_cost_ledger.jsonl`（8 必填字段 + raw_output + input_sha256）。
- DEGRADED：路由 DENY / 超限 / 服务不可用 / 解析失败 / 盲包违规 → `judge_protocol.make_degraded` 事件（`validate_degraded` 通过）写入 `DEGRADED_EVENTS.jsonl`，不静默跳过。
- 重测：10% 样本绕过缓存重发（R-Q5），报 exact repeat 与 preference repeat。
- 校准：冻结 T2v1 在 t18 的 30 对能力样本上复测偏好侧一致率。

## 3. 运行

```powershell
cd 03_build/local/t14
$py = "C:\Users\PC\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"

& $py t14_audit.py                       # 无 GPU：864 包审计 + 損坏确定性 + T1 分层计数
& $py t14_runner.py --run-id t14_main --dry-run   # 计划 + 盲包/token 审计，不调用模型
& $py t14_runner.py --run-id t14_smoke2 --execute --items <8 ids>   # 分层 smoke（t19 结束后）
& $py t14_runner.py --run-id t14_main --execute   # 全量 1086 次调用（t19 结束后）
& $py t14_runner.py --run-id t14_main --acceptance
```

运行顺序由 captain 裁定：**t19 独占 GPU → t14 smoke（8 题）→ captain 复核 → t14 全量 → t21**。
t19 运行期间不得发起任何本地推理；VRAM 事件见 `evidence/VRAM_EVENT_20261112.json`。

## 4. 无 GPU 审计（已通过）

- 盲包：864 个 packet（T1 320 + S1 模型 224 + T2 320）`audit_packet` 违规 **0**；S1 机械回退 96 条无 packet。证据：`evidence/BLIND_PACKET_AUDIT.json`，复现命令 `python t14_audit.py`。
- T2 确定性：320 对全部 `corrupt_text` 两次逐字节相同、与落盘 degraded 相同、sha 相同；位置 160/160；四种损坏各 80。证据：`evidence/T2_DETERMINISM_AUDIT.json`。
- T1 分层：64 / 64 / 192，全部 ≥30。证据：`evidence/T1_STRATIFIED_TRUTH.json`。
- token 上限：T1 max 341 / S1 max 691 / T2 max 406，分别低于 3000/1000/2000。证据：`evidence/BLIND_PACKET_AUDIT.json`。

## 5. 吞吐口径（写进方法节）

能力矩阵 207.89 calls/min 是**短输出**（`num_predict` ≤128）；t19 E1 要生成完整 12 字段记录
（实测 mean eval_count ≈245.7），只有 **8.97 calls/min**，差约 **23×**。t14 与 t19 共享 GPU 时
smoke 实测 3.29 calls/min。**不得用 200+/min 估算长生成任务工期**。证据：`evidence/THROUGHPUT_GAP.json`。

## 6. VRAM 事件（如实记录）

- 观测峰值：used **7763 MiB / 8192**，free **255 MiB**，低于 1536 MiB 下限；`ollama ps` 仍 100% GPU，无 CPU 回退。
- 触发：t14 4 题 smoke 的 preflight 在 free=310 MiB 时正确拒绝；captain 随后裁定串行、t19 独占 GPU。
- 披露：该 4 题 smoke（12 次调用 / 218.6 s / 3.29 calls/min）在串行命令到达**之前**已启动并完成；
  命令到达后**未再发起任何 GPU 调用**。证据：`evidence/VRAM_EVENT_20261112.json`。

## 7. 产物

```
t14/
  t14_runner.py / t14_report.py / t14_audit.py / recon.py
  evidence/                       # 无 GPU 审计 + VRAM + 吞吐证据
  runs/t14_main/                  # 全量 run（config 含私盐；cache/；annotations_*.jsonl；
                                  #  t2_pairs.json；t1_analysis.json；s1_analysis.json；
                                  #  calibration_T2.json；repeats.json；local_cost_ledger.jsonl；
                                  #  cost_ledger.jsonl；DEGRADED_EVENTS.jsonl；acceptance.json；
                                  #  REPORT_T14.md；run_manifest.json）
  REPORT.md / acceptance.json     # 全量完成后
```

标注行关键字段：`item_id`、`item_handle`、`status`（OK / MECHANICAL_FALLBACK / DEGRADED）、
`input_sha256`、`raw_output`（模型行）、`prompt_template_version`、`parsed_output`、`cache_hit`、
`truth_class`/`mechanical_truth`（T1）、`clean_position`/`corruptor`/`score_a`/`score_b`/`preference`（T2）。

## 8. 边界

- 本地 7B 输出不是金标；T1 只对 D2/D3 可解释，S1 只描述性，T2 只用序判定。
- 不得把 T14 的 T1/T2 与 t18 矩阵或云端 t16 的绝对分直接比较；可比的是同一冻结模板下的序指标。
- 任何 `DEGRADED` 都计入覆盖缺口，不得从报告中删除。
