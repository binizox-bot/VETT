# R28 本地推理服务（Qwen2.5-7B / Ollama）— 固定、可测、可降级

> 角色：`local_operator`（t18）　模型：`qwen2.5:7b-instruct-q4_K_M`（RTX 3070 8 GB，100% GPU）
> 零付费 API　R26.15 只读　所有调用可重放

这套代码把本地 7B 固化成流水线里的**标注劳动力**：先测能力、再发白名单；白名单外的活一律
`DEGRADED`，不伪造、不静默截断、不进统计。

## 目录

| 文件 | 作用 |
|---|---|
| `local_inference/service.py` | 启动检查 / 模型 tag+量化记录 / temperature=0 + 固定 seed / 超时与重试 / 100% GPU 断言 |
| `local_inference/ledger.py` | 每次调用落盘 8 个必填字段到 `cost_ledger.jsonl`；缺字段的输出不得进入统计 |
| `local_inference/corpus.py` | R26.15 只读加载 + 机械真值构造（可复现口径 `vett-tree-aggregate-v1`） |
| `local_inference/tasks.py` | 5 类任务 prompt / 解析 / 机械评分（模板版本冻结） |
| `local_inference/matrix.py` | 能力矩阵运行器（固定 seed、内容寻址缓存、VRAM 采样） |
| `local_inference/policy.py` | 路由策略单一来源：ALLOW/DENY、输入上限、运行时断言、路由卡生成 |
| `local_inference/api.py` | 供 t13 调用的唯一入口：`annotate()` → OK 或 DEGRADED |
| `local_inference/verify.py` | 17 项独立一致性校验 + DEGRADED 自检 + cache-only 矩阵重建 |
| `local_inference/report.py` | 生成 `REPORT.md` |
| `routing_card.json` | 机器可读路由卡（由 matrix+code 生成，verify 保证不漂移） |
| `capability_matrix.json` | 5 类任务 × ≥30 样本的机械真值测量结果 |
| `service_snapshot.json` | 模型 digest / 量化 / GPU / 100% 驻留 / 参数快照 |
| `cost_ledger.jsonl` | 每次调用的完整账本（含 raw_output、parsed_output、wall_clock） |
| `DEGRADED_EVENTS.jsonl` | 降级事件（仅当 t13 触发不达标任务时产生） |
| `runs/` | 每次矩阵运行的逐样本原始记录、缓存、校验与自检产物 |
| `tools/` | 只读诊断脚本（语料分布、真值提取、pilot 错误分析） |

## 快速开始

```powershell
cd "D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_R28_DIFFICULTY_20261112\03_build\local"
$py = "C:\Users\PC\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"

& $py -m local_inference preflight     # 启动检查（模型/量化/VRAM/100% GPU）
& $py -m local_inference matrix        # 能力矩阵（固定 seed；有缓存则秒级重放）
& $py -m local_inference routing       # 由矩阵生成 routing_card.json
& $py -m local_inference verify        # 17 项一致性校验（exit 0/4）
& $py -m local_inference report        # 生成 REPORT.md
& $py -m local_inference selftest      # 只测降级接口，不碰 GPU
```

也可以直接用 `serve_local.ps1 -Action all`（自动选择 `$env:VETT_PYTHON` 或本机 bundled python）。

## 当前结论（2026-11-12，seed=20261112）

| 任务 | n | 机械真值一致率 | 判定 | p50 |
|---|---:|---:|---|---:|
| `T1_factor_visibility` | 30 | 0.933 | **ALLOW** | 0.19 s |
| `T2_naturalness` | 30 | 1.000（retest 1.0） | **ALLOW** | 0.25 s |
| `S1_span_topic` | 32 | 1.000 | **ALLOW** | 0.15 s |
| `C1_cert_sentence_consistency` | 30 | 1.000 | **ALLOW** | 0.22 s |
| `R1_readability` | 30 | 0.667（ρ=-0.20） | **DENY** | — |

DENY（静态、带实测依据）：12 字段记录推导、置信度、kappa/仲裁、统计推断、合同/代码设计、
>8K token 输入、T3 提报裁定、未经 solver 校验的草稿。依据见 `routing_card.json.deny_evidence`。

## 硬约束（代码里断言，不靠自觉）

- 模型 tag 必须命中 `qwen2.5:7b-instruct-q4_K_M`，量化必须记录为 `Q4_K_M`。
- `temperature=0.0`、`seed=20261112`、`num_ctx=8192`，每次调用写入账本；漂移即 verify 失败。
- `ollama ps` 必须 100% GPU；不足则直接报警（不静默降级到 CPU）。
- 开跑前 VRAM 剩余 <1536 MiB 即报警；矩阵每次调用后采样 VRAM 峰值。
- 任一任务输入超过其路由卡上限（T1 3K / T2 2K / S1 1K / C1 2K / R1 2K token）即拒绝；
  任何 >8K token 输入一律拒绝，绝不静默截断。
- 超过 8K 的活、需要推导/概率/统计/仲裁/设计的活，一律不在本服务里实现。

## 给 t13 的一句话

```python
from local_inference import api
result = api.annotate("T1_factor_visibility", {"passage": evidence_text})
if result["status"] == "DEGRADED":
    ...  # 用 result["degraded"]["fallback"]，并在报告里如实标覆盖率
```

详见 `INTERFACE.md`。

## 复现口径

- 样本由 `seed=20261112` 确定性构造；同 seed 同版本必然生成同一批 `sample_id`。
- 缓存键 = `sha256(template_version | model_tag | temperature | seed | num_ctx | num_predict | prompt)`；
  重跑命中缓存不产生新 GPU 调用，`verify` 的 cache-only 重建必须得到同一 `summary_digest`。
- 账本按调用追加；矩阵逐样本原始记录在 `runs/matrix_<UTC>_full/<task>.jsonl`。

## 边界

本地 7B 的输出不是金标。它只做"看一眼就能判断"的封闭式标注；正确性锚点始终是确定性 solver /
机械真值。R1 的 DENY 就是这条原则的实例：当模型分数无法跟随机械可读性标尺时，回退机械规则，
而不是把模型分数当真理。
