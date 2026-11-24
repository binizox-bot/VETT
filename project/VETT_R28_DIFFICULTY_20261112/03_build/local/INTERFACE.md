# t13 集成接口（local_inference）

**唯一入口**：`local_inference.api.annotate(task_id, sample, ...)`。
白名单任务 → `status="OK"` + 一条完整账本条目；不达标 / 超限 / 服务故障 / 解析失败 →
`status="DEGRADED"` + 一条 append-only 事件。**没有第三种结果，也不会伪造标注。**

## 1. 接入

```python
import sys
LOCAL = r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_R28_DIFFICULTY_20261112\03_build\local"
sys.path.insert(0, LOCAL)                      # 或把 LOCAL 加进 PYTHONPATH
from local_inference import api, policy
```

依赖：Python 3.10+ 标准库；本机 Ollama（`127.0.0.1:11434`）与
`qwen2.5:7b-instruct-q4_K_M`。不联网、无付费 SDK、无第三方包。

## 2. 五类任务的 sample 结构

`sample` 是普通 dict；除下列字段外可携带任意元数据（不会进入 prompt，便于回填 id）。

| task_id | sample 必填字段 | 典型来源 |
|---|---|---|
| `T1_factor_visibility` | `passage: str`（单条证据 span，≤3K token） | R28 证据 span |
| `T2_naturalness` | `natural_text: str`、`degraded_text: str`、`clean_position: "a"\|"b"`（两段渲染配对） | V+/V−/V0 双渲染 |
| `S1_span_topic` | `span_text: str`（≤1K token） | R28 证据 span |
| `C1_cert_sentence_consistency` | `sentence: str`、`record: dict`（12 字段 flat 记录） | solver 证书句 + 记录 |
| `R1_readability` | `passage: str` | **DENY**，调用必得 DEGRADED |

`T2` 是**配对**任务：它被测量的是"干净渲染应比机械损坏渲染得分高"。单段文本的自然度**不在**
ALLOW 范围内（无测量依据），请传配对；R28 的 V+/V−/V0 孪生天然满足。

## 3. 返回值

### OK

```json
{
  "schema_version": "vett-local-annotation-envelope/v1",
  "task": "T1_factor_visibility",
  "status": "OK",
  "annotation": {"supported": true, "evidence": "..."},
  "degraded": null,
  "ledger_entry": {
    "input_sha256": "...", "prompt_template_version": "T1.factor_visibility.v1",
    "temperature": 0.0, "seed": 20261112, "model_tag": "qwen2.5:7b-instruct-q4_K_M",
    "wall_clock": 0.19, "raw_output_sha256": "..."
  },
  "route": {"verdict": "ALLOW", "validator": "mechanical_truth", "input_cap_tokens": 3000, "fallback": "mechanical_lexicon_rule"},
  "replayable": true
}
```

完整 `raw_output` / `parsed_output` / 调用参数在 `cost_ledger.jsonl`（按 `input_sha256` 可重放）。
t13 若需要自己的账本文件，用 `api.annotate(..., ledger_path=...)` 或环境变量
`VETT_LOCAL_LEDGER`。

### DEGRADED

```json
{
  "schema_version": "vett-local-annotation-envelope/v1",
  "task": "R1_readability",
  "status": "DEGRADED",
  "annotation": null,
  "degraded": {
    "schema_version": "vett-degraded-event/v1",
    "timestamp_utc": "2026-11-12T10:29:08Z",
    "task": "R1_readability",
    "status": "DEGRADED",
    "reason_code": "CAPABILITY_BELOW_THRESHOLD",
    "reason": "agreement 0.667 on n=30 (threshold 0.85); ...",
    "source": "t13",
    "fallback": "flesch_reading_ease_band",
    "model_tag": "qwen2.5:7b-instruct-q4_K_M",
    "evidence": {"measured": {"agreement": 0.667, "n": 30, "threshold": 0.85}}
  },
  "replayable": false
}
```

`reason_code` 取值：`TASK_DENIED` / `CAPABILITY_BELOW_THRESHOLD` / `CAPABILITY_UNMEASURED` /
`INPUT_CAP_EXCEEDED` / `SERVICE_UNAVAILABLE` / `MODEL_MISMATCH` / `PARSE_FAILURE` / `NO_INPUT`
以及静态 DENY 的具体码（`MEASURED_BELOW_PRIOR` / `UNUSABLE_OUTPUT` / `ROLE_ISOLATION` /
`NOT_A_MODEL_TASK` / `HARD_INPUT_CAP` / `UNVERIFIED_GENERATION`）。

事件写到 `DEGRADED_EVENTS.jsonl`（可用 `api.annotate(..., degraded_path=...)` / 环境变量
`VETT_LOCAL_DEGRADED` 改路径）。**每次 DEGRADED 都必须在报告里体现为覆盖率缺口**，不得静默丢弃样本。

## 4. 运行时门

- `api.annotate` 每次调用都重新读取 `capability_matrix.json` 判定 verdict（fail-safe：文件缺失/任务缺失 → DENY）。
- 输入上限按路由卡：T1 3000 / T2 2000 / S1 1000 / C1 2000 token；任何 >8192 token 一律拒绝。
  估算口径保守（UTF-8 字节 / 3.0），实际 `prompt_eval_count` 也写入账本。
- 模型 tag / quant / temperature / seed 与账本不一致时 `verify` 会失败；t13 不需要自己校验，
  但必须保留 `ledger_entry` 以便事后审计。
- `allow_degraded=False` 时，DEGRADED 路径改为抛 `LocalServiceError`（供"绝不允许降级"的阶段使用）。

## 5. 批量

```python
results = api.annotate_batch("S1_span_topic", samples, caller="t13")
```

逐条串行、逐条落账本；任何一条 DEGRADED 不影响其余条目。建议每 ≤50 条落盘一次（t13 侧负责）。

## 6. 只读查询

```python
policy.route("T1_factor_visibility")     # 当前 resolved route（ALLOW/DENY + 上限 + 校验方 + deny_reason）
api.capability_snapshot()                # 5 类任务的 verdict / agreement / n / p50 / deny_reason
policy.load_matrix()                     # 完整矩阵原始 JSON
```

## 7. 自检（t13 可当作门）

```powershell
python -m local_inference selftest      # 8 条 DEGRADED 路径，exit 0/4
python -m local_inference verify        # 17 项一致性校验，exit 0/4
```

`selftest` 不需要 GPU / Ollama，可在 CI 里跑；`verify` 的 cache-only 重建同样不需要 GPU。

## 8. 注意

- 不要绕过 `api` 直接调 `service.generate`：那会跳过能力门与账本，属于违规使用。
- 不要把本地输出当金标；ALLOW 只表示"与该任务机械真值的逐样本一致率 ≥0.85"，
  仍应由 t17 J 门/云端抽样复核。
- `routing_card.json` 是派生产物：改代码后必须重跑 `matrix → routing → verify`，否则 verify 失败。
