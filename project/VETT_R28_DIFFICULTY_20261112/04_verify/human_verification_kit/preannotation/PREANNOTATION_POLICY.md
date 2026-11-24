# 预标注包策略（PREANNOTATION_POLICY v1）

**定位：** 只减轻标注者的“找 span / 看主题”负担，**不产生金标、不产生 12 字段记录、不参与 κ、不参与 H1/H2/H3**。
**本地模型：** t18 服务（Ollama + `qwen2.5:7b-instruct-q4_K_M`），零付费 API、零云调用。
**当前状态：** 本轮**未调用**本地模型（不属 t24 授权）；演示输出全部为 `DEGRADED / RULE_BASELINE_ONLY`。真实运行在 R28 数据与本地服务可用后由 E 阶段执行。

---

## 1. 允许与禁止

| 内容 | 本地模型 | 说明 |
|---|---|---|
| `S1_span_topic`（RUNS / DISMISSAL / BOWLING / IDENTITY） | ✅ ALLOW | 只是把 span 粗分类，帮助标注者定位；`candidate` 可编辑 |
| `T1_factor_visibility`（supported true/false） | ✅ ALLOW | 因子可见性提示，仅 triage |
| 证书逐句一致性 `C1` | ✅ ALLOW（可选） | 只在仲裁阶段对“已有记录”做辅助，不产出记录 |
| 12 字段记录 / scope / 规则版本 / 证明集合 | ❌ **禁止** | 合同 §10.10 禁止语言模型生成事实/金标/证书；用 solver 输出做提示又属循环论证 |
| 任何“金标候选” / 自动通过 | ❌ **禁止** | 人工核验的价值在于独立，模型不能替代 |
| 云端 / 付费 provider / 上传数据 | ❌ **禁止** | 硬约束 |

## 2. 输出契约（JSONL，一行一个候选）

```json
{
  "schema": "vett.r28.human_kit.preannotation.v1",
  "kit_version": "VETT-R28-HUMAN-VERIFICATION-KIT-20261112-v1",
  "item_id": "…",
  "span_id": "s_…",
  "task": "S1_span_topic",
  "candidate": {"topic": "RUNS"},
  "provenance": {
    "adapter": "local_inference",
    "model_tag": "qwen2.5:7b-instruct-q4_K_M",
    "status": "OK",
    "reason_code": null,
    "template_version": "S1.span_topic.v4",
    "input_sha256": "…"
  },
  "usable_as_gold": false,
  "not_gold": true,
  "editable": true,
  "note": "local model hint; ALLOW only means agreement with mechanical truth on its own task, not correctness of gold",
  "created_at_utc": "…"
}
```

- `usable_as_gold` 必须恒为 `false`；`not_gold` 必须恒为 `true`；代码会断言。
- `candidate` 的键只允许 `topic` / `supported` / `evidence`；**不得**出现 12 字段名。
- `DEGRADED` 行必须有 `reason_code`（`SERVICE_UNAVAILABLE` / `CAPABILITY_BELOW_THRESHOLD` / `INPUT_CAP_EXCEEDED` / `RULE_BASELINE_ONLY` 等）并计入覆盖率缺口。

## 3. 覆盖率口径

`PREANNOTATION_COVERAGE.json` 按 task 给出 `attempted / ok / degraded / ok_rate` 与 `degraded_reason_counts`。
报告必须写“覆盖率缺口”，不得静默丢弃 DEGRADED 行；DEGRADED 不能作为“已完成预标注”的证据。

## 4. 运行

```powershell
# 离线 stub（无需模型；全部 DEGRADED；用于演示与自检）
& "D:\Conda\python.exe" scripts\preannotate.py `
  --bundle out\annotation_bundle\bundle_public.json `
  --out-dir out\preannotation --adapter stub --max-spans-per-item 40

# 本地模型（E 阶段；需 t18 服务与 Ollama）
& "D:\Conda\python.exe" scripts\preannotate.py `
  --bundle out\annotation_bundle\bundle_public.json `
  --out-dir out\preannotation --adapter local --tasks S1_span_topic --max-spans-per-item 40
```

- 输入上限按 t18 路由卡：S1 1000 tokens、T1 3000 tokens；超限必须 DEGRADED。
- 每次调用写 t18 账本（`input_sha256` / `model_tag` / `template_version` / temperature=0 / seed=20261112），可重放。
- 若本地服务不可用：全 DEGRADED、流程继续，不阻塞人工标注。

## 5. 与人工标注的关系

- 预标注只是**可编辑提示**；标注者可以完全忽略或改写。
- 人工阶段 1 仍然必须独立从卷宗推导 12 字段；工具不预填记录值。
- 预标注不参与 `agreement.py` 的 κ、不参与 `qualification.py` 的资格判定、不参与 `adjudicate.py` 的门。

## 6. 当前产物

- `out/selftest/preannotation/preannotations.jsonl`：stub 演示，全部 `DEGRADED / RULE_BASELINE_ONLY`；
- `out/selftest/preannotation/PREANNOTATION_COVERAGE.json`：覆盖率与原因计数；
- `out/selftest/preannotation_local_missing/`：本地服务缺失时的降级路径（100% DEGRADED，不崩溃）。

> 本包**不产生人工金标**。真实数据 `PASS` 之前，论文必须列“人工双标未执行”为发表阻断项。
