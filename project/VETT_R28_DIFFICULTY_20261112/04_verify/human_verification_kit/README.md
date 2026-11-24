# R28 人工核验就绪包（human_verification_kit）

**Kit 版本：** `VETT-R28-HUMAN-VERIFICATION-KIT-20261112-v1`
**任务：** t24 —— 人工核验就绪包（**本轮不执行人工标注**）
**运行根：** `VETT_R28_DIFFICULTY_20261112/04_verify/human_verification_kit/`
**上位文件：** 合同 `VETT-R28-CONTRACT-20261112-v1` v1.1.0（N=320）；预注册 `VETT-R28-PREREG-20261112-v1` v1.1.0

> **状态：READY_FOR_HANDOFF = true ｜ READY_TO_ANNOTATE = false**
>
> 工具、协议、抽样、统计、仲裁与自检全部就绪，并已在**合成 R28 形状数据**上端到端跑通（含 kappa、双标、仲裁、PASS/FAIL 两条路径）。
> 真实标注**尚未执行**，原因是：(1) R28 构建尚不存在；(2) 构建必须发布 `build_index.json` 才能把 100 个设计 slot 绑定到真实 `item_id`；(3) 没有标注者。
>
> **本 kit 不产生人工金标。** 在 `adjudicate.py` 对真实 R28 数据返回 `PASS` 之前，论文必须把“金标未经独立人工双标核验”列为**发表阻断项**。

---

## 1. 这个包解决什么问题

审稿人可以直接质疑：**R28 的金标是 solver 生成的，谁来保证它是对的？**
本包不声称已经解决，而是把“一旦有标注者就能立刻执行”的全部材料准备好：

- 双标协议（四维判定、冲突处理、仲裁、98% 合格线）；
- 100 题分层样本（28 个设计格全覆盖，固定种子，确定性可复现）；
- 单文件离线 HTML 工具（盲推导 → 金标揭示 → 判定 → 仲裁）+ CLI 等价路径；
- 一致性统计（Cohen's κ + 逐维原始一致率 + 分歧清单）；
- 预标注包（只用本地模型做允许的提示任务；DEGRADED 计入覆盖率；**不得作为金标**）；
- 端到端自检（合成数据上跑通，并验证 κ 与独立实现一致、R26.15 零漂移）。

## 2. 文件树

```
human_verification_kit/
├─ README.md                      ← 本文件
├─ ANNOTATION_PROTOCOL.md         ← 双标协议（四维判定 / 冲突 / 仲裁 / 合格线）
├─ SAMPLING_PLAN.md               ← 分层抽样方案（28 层 / 100 题 / 种子 / 绑定）
├─ E_PHASE_HANDOFF.md             ← E 阶段移交清单（前置条件、步骤、门、时间）
├─ STATUS.json                    ← 机器可读就绪状态与阻断项（由自检生成）
├─ KIT_MANIFEST.json              ← 全包逐文件 sha256 + 聚合（由自检生成）
├─ sample_ids.json                ← 100 个设计 slot（构建前 PROVISIONAL）
├─ sample_ids_n160_legacy.json    ← 任务书旧口径（N=160）兼容件
├─ design_manifest_n320.json      ← 320 个设计 slot（由冻结合同派生）
├─ design_manifest_n160_legacy.json
├─ schema/                        ← bundle / annotation / adjudication / build_index 契约
├─ scripts/
│  ├─ common.py                   ← 12 字段常量、记录一致性、泄漏筛查、κ
│  ├─ make_design.py              ← manifest / sample / resolve / validate
│  ├─ build_bundle.py             ← 构建 public + hidden gold bundle（含泄漏筛查）
│  ├─ annotate_cli.py             ← 两阶段 CLI 标注器（derive / verify）
│  ├─ seal_export.py              ← 浏览器导出密封（补哈希）
│  ├─ validate_export.py          ← 导出校验（12 字段/标签/span 存在性/覆盖率）
│  ├─ agreement.py                ← 逐维一致率 + Cohen's κ + 分歧清单
│  ├─ qualification.py            ← 资格测试（20 道合成校准题）
│  ├─ adjudicate.py               ← 合并 + H1/H2/H3 + HUMAN_VERIFICATION_REPORT
│  ├─ preannotate.py              ← 预标注包（本地模型提示；DEGRADED 允许）
│  ├─ make_synthetic.py           ← 合成 R28 形状构建与答案脚本（自检/资格用）
│  ├─ check_baseline.py           ← R26.15 零漂移 + 合同/预注册冻结绑定
│  └─ run_selftest.py             ← 一键端到端自检
├─ tool/annotate.html             ← 单文件离线标注/仲裁工具（无网络、无外部资源）
├─ fixtures/                      ← 合成构建（320 题）与索引；供自检/资格
├─ preannotation/                 ← 预标注策略与产出（DEGRADED 演示）
└─ out/selftest/                  ← 自检产物（SELFTEST_RESULT.json、报告、κ 等）
```

## 3. 快速开始（三条命令，先看自检）

```powershell
$KIT = "VETT_R28_DIFFICULTY_20261112\04_verify\human_verification_kit"
& "D:\Conda\python.exe" "$KIT\scripts\run_selftest.py"
# 期望：exit 0；out/selftest/SELFTEST_RESULT.json 的 ok=true
& "D:\Conda\python.exe" -c "import json; print(json.load(open(r'$KIT\out\selftest\SELFTEST_RESULT.json'))['n_pass'], json.load(open(r'$KIT\out\selftest\SELFTEST_RESULT.json'))['ok'])"
```

自检用**合成 R28 形状数据 + 真实 R28 schema 适配器**跑通 14 步：设计 manifest → 分层样本 → 绑定 → bundle → 两阶段标注 → 浏览器导出密封/校验 → κ/分歧 → 资格（PASS/FAIL）→ 仲裁（PASS/FAIL）→ 预标注 DEGRADED/本地适配器 → R26.15/冻结绑定。

## 4. 真实数据上的执行顺序（E 阶段）

完整清单见 `E_PHASE_HANDOFF.md`；最短路径：

1. **构建**（t5/t6）发布 `build_index.json`：每题必须带 `block` + `cell`（因子核）或 `block` + `mechanism` + `dose`（剂量阶梯）。
2. **绑定**：`make_design.py resolve ... --strict` → `sample_ids_bound.json` + `BINDING_RECEIPT.json`。
3. **bundle**：`build_bundle.py --build-dir <candidate> --sample sample_ids_bound.json --out-dir <bundle>`。
4. **资格**：A/B 各自在 20 道合成校准题上跑 `qualification.py`，必须 PASS。
5. **双标**：A/B 各自阶段 1（盲推导）→ 密封 → 阶段 2（金标判定）→ 密封 → `validate_export.py`。
6. **统计**：`agreement.py` → `agreement_report.json` + `disagreements.jsonl`。
7. **仲裁**：仅分歧；`annotate.html` 仲裁页或 JSONL → `adjudicate.py`。
8. **裁决**：`HUMAN_VERIFICATION_REPORT.json` 必须 `PASS`；否则按 §8 隔离金标、修复、重验。

## 5. 门与判定（与协议一致）

| 门 | 条件 | 失败后果 |
|---|---|---|
| H1 | 样本完整；每维原始一致率 ≥98% | 不可声称人工核验通过；重训/重标 |
| H2 | 确认金标缺陷 = 0；无未裁决项 | 金标隔离、修复、重验；不得剔除缺陷题后声称通过 |
| H3 | A/B 资格测试各维 ≥98% 且关键错误 = 0 | 该标注者不得进入正式样本 |

- κ 会报告（含 bootstrap 95% CI、PABAK），但**不是门**：金标高度正确时 κ 的期望一致率趋 1，分母趋 0，κ 不稳定；门用原始一致率。
- 关键错误 = 值 `MISMATCH`、scope `SCOPE_ERROR`、规则版本 `VERSION_ERROR`、证明 `INSUFFICIENT`/`FABRICATED`；`NOT_MINIMAL` 非关键。
- 所有判定都必须可机械复核；`UNDECIDABLE` 必须写缺什么，不得为了“通过”强行正向。

## 6. 预标注包（本地模型）

- 只允许 `S1_span_topic` / `T1_factor_visibility` 两类 ALLOW 任务，输出**可编辑提示**；
- **绝不**输出 12 字段记录/scope/规则版本/证明（合同 §10.10 禁止模型生成金标；用 solver 输出做提示又属循环）；
- 每次调用写账本；`DEGRADED` 必须计入覆盖率缺口；
- 本轮未调用本地模型（不属 t24 授权），演示输出全部为 `DEGRADED / RULE_BASELINE_ONLY`；真实运行在 R28 数据存在后由 E 阶段执行。

详见 `preannotation/PREANNOTATION_POLICY.md`。

## 7. 不可越过的边界

- 本包**不写入** R26.15 数据集、不写入 `analysis/`、`eval_configs/`、`eval_runs/`、不写入 `src/` 或既有测试。
- 不联网、不调用付费 API、不读取 `.secrets`。
- 不修改合同/预注册；若协议与预注册冲突，以预注册为准。
- 人工标签只确认/隔离 solver 金标；**不产生新金标**。
- 论文在真实数据 `PASS` 之前必须列“人工双标未执行”为发表阻断项（合同 RISK-6、PROPOSAL §5.5）。

## 8. 验证证据

- `out/selftest/SELFTEST_RESULT.json`：14 步结果、命令、耗时；
- `out/selftest/agreement/agreement_report.json`：逐维一致率 + κ + bootstrap CI + 分歧；
- `out/selftest/adjudication_clean/HUMAN_VERIFICATION_REPORT.json`：干净路径 PASS；
- `out/selftest/adjudication_defect/HUMAN_VERIFICATION_REPORT.json`：模拟金标缺陷路径 FAIL（验证 H2 真的会拦）；
- `out/selftest/BASELINE_CHECK.json`：R26.15 338 文件逐字节重算 + 合同/预注册冻结绑定；
- `KIT_MANIFEST.json`：全包逐文件 sha256 + `vett-tree-aggregate-v1` 聚合。

> 兼容性说明：自检的 `real_r28_schema_adapter` 步骤覆盖真实 R28 schema（`dossier.documents`、`certificate.minimum_evidence_spans`、剂量格 `D1-1`、以及 `LEGAL` 且 `counts_in_over=false`/`batter_runs=11` 的真实记录）。作者另用 t5 的 10 题样例做过一次端到端冒烟（适配器/CLI/κ/门均可跑通），但该冒烟不是人工标注，其报告**不作为交付物保留**，以免被误读为“人工核验 PASS”。

## 9. 限制（必须进论文）

1. **没有人工金标**：本包只是就绪，真实双标未执行。
2. **样本是 100/320（31.25%）**：零缺陷时 95% 上界约 3%，不是“无缺陷证明”；不能按层做推断。
3. **合成自检不等于真实数据验证**：合成构建只证明工具/协议/统计可运行。
4. **预标注未真实运行**：本地模型路径代码就绪，本轮全 DEGRADED。
5. **标注者间一致性 ≠ 金标正确**：H1 只排除“双方看到不同事实”；H2 才是金标质量门；两者都过才算 PASS。
