# E 阶段移交清单（人工核验执行手册）

**前置：** t24 就绪包已完成；本文件不执行标注，只定义“一旦有数据与标注者，按什么顺序做”。
**上位：** `ANNOTATION_PROTOCOL.md`、`SAMPLING_PLAN.md`、`VETT-R28-CONTRACT-20261112-v1` v1.1.0、`VETT-R28-PREREG-20261112-v1` v1.1.0。
**当前状态：** `NOT_EXECUTED`。没有数据、没有标注者、没有人工金标。

---

## 1. 前置条件（缺一不可）

| ID | 条件 | 责任方 | 检查方式 |
|---|---|---|---|
| P1 | R28 候选构建已冻结（320 题 / 64 场；64 个独立 dossier） | t5/t6 | `MANIFEST.json` + 构建报告 |
| P2 | 构建发布 `build_index.json`：每题含 `item_id` + `block` +（`cell` 或 `mechanism`+`dose`） | t5/t6 | `schema/build_index.schema.json`；`make_design.py resolve --strict` 通过 |
| P2b | 若构建只发布 `published/<id>/private_gold.json`（含 block/cell/doses）而未发布 consolidated index，可先派生：`make_design.py index --build-dir <candidate> --out build_index.json` | 数据管理员 | 派生索引必须逐题来自 payload 元数据，不猜 cell/dose || P3 | `solver_facts` + `decision_record_flat` 逐字节 twin identity 320/320（HA8） | t6/t8 | t8 报告 |
| P4 | gold 证书 100% 可重推（HA7）；泄漏审计 PASS（HA11） | t6/t8 | t8 报告 |
| P5 | 合同/预注册哈希与冻结一致 | t8 | `check_baseline.py`（本包已内置） |
| P6 | A/B 两名标注者通过资格测试；C 仲裁者就位并签署利益冲突声明 | captain/用户 | `qualification_<A|B>.json` 均 pass=true |
| P7 | 数据使用与保密协议已签署；离线环境可用（浏览器 file:// 或 CLI） | captain/用户 | 签字记录 |

> **P2 是最容易漏的一条。** 仅靠 `doses` 配置无法区分剂量阶梯的 4 个 `level=0` 格（配置全 0），所以必须保留 `mechanism`。若构建只提供配置，`make_design.py resolve --strict` 会以 `BUILD_INDEX_INCOMPLETE` 退出，这是预期行为，不得绕过。

---

## 2. 执行顺序（逐条命令）

设 `$KIT = "VETT_R28_DIFFICULTY_20261112\04_verify\human_verification_kit"`，`$BUILD = "<t6 构建目录>"`，`$WORK = "$KIT\out\run_<date>"`。

### 2.1 绑定（数据管理员）

```powershell
New-Item -ItemType Directory -Force $WORK | Out-Null
& "D:\Conda\python.exe" "$KIT\scripts\make_design.py" resolve `
  --index "$BUILD\build_index.json" `
  --sample "$KIT\sample_ids.json" `
  --out "$WORK\sample_ids_bound.json" `
  --receipt "$WORK\BINDING_RECEIPT.json" --strict
```

**验收：** 100 个唯一 `item_id`；28 层全覆；`BINDING_RECEIPT.json` 的 `coverage.dead_ball` 与合法 dismissal 覆盖被如实记录（缺就写警告，不补题）。

### 2.2 生成 bundle（数据管理员）

```powershell
& "D:\Conda\python.exe" "$KIT\scripts\build_bundle.py" `
  --build-dir "$BUILD" `
  --sample "$WORK\sample_ids_bound.json" `
  --out-dir "$WORK\bundle"
```

**验收：** `BUNDLE_RECEIPT.json` 的 `n_items=100`、`leak_screen.verdict=PASS`、public/gold 两个文件哈希不同、gold 每题证书 `minimum_evidence_spans` 非空。

### 2.3 预标注（可选；本地模型）

```powershell
& "D:\Conda\python.exe" "$KIT\scripts\preannotate.py" `
  --bundle "$WORK\bundle\bundle_public.json" `
  --out-dir "$WORK\preannotation" --adapter local --max-spans-per-item 40
```

**验收：** `PREANNOTATION_COVERAGE.json` 给出 OK/DEGRADED 覆盖；`DEGRADED` 必须计入覆盖率缺口；**任何输出都不是金标**（`usable_as_gold=false`）。若本地服务不可用，全 DEGRADED 也可接受，不得阻塞流程。

### 2.4 资格测试（A/B 各自独立）

1. 用 `make_synthetic.py qualification` 生成 20 道合成校准题 bundle（本包 `fixtures/` 已含示例；E 阶段可重新生成以刷新）。
2. 每人跑 `annotate_cli.py derive` + `verify`（或 HTML 工具），得到 `qual_<X>_derived.jsonl` / `qual_<X>_verify.jsonl`。
3. 运行：

```powershell
& "D:\Conda\python.exe" "$KIT\scripts\qualification.py" `
  --derived "$WORK\qual_ann_<x>_derived.jsonl" --verify "$WORK\qual_ann_<x>_verify.jsonl" `
  --gold-bundle "$WORK\qualification\qualification_bundle\bundle_gold.json" `
  --annotator-id <A|B> --items "$WORK\qualification\qualification_ids.json" `
  --out "$WORK\qualification_<a|b>.json"
```

**验收：** 每维确认准确率 ≥98%、12 字段准确率 ≥98%、关键错误 0；不通过 → 重训（最多 2 次）→ 更换标注者。

### 2.5 阶段 1：盲推导（A/B 独立）

浏览器：打开 `tool/annotate.html` → 阶段 ① → 只加载 `bundle_public.json` → 逐题填写 → 锁定 → 导出 `annotations_derived_<X>.jsonl`。
CLI 等价：`annotate_cli.py derive --annotator-id <X> --bundle ... --out ...`（交互式）。

**强制：** 此阶段不得加载 `bundle_gold.json`。若提前查看，该标注者数据作废重做。

### 2.6 密封并校验 DERIVED

```powershell
& "D:\Conda\python.exe" "$KIT\scripts\seal_export.py" --kind DERIVED `
  --file "$WORK\annotations_derived_A.jsonl" --out "$WORK\sealed_derived_A.jsonl" `
  --public-bundle "$WORK\bundle\bundle_public.json" --receipt "$WORK\seal_derived_A.json"

& "D:\Conda\python.exe" "$KIT\scripts\validate_export.py" --kind DERIVED `
  --file "$WORK\sealed_derived_A.jsonl" --public-bundle "$WORK\bundle\bundle_public.json" `
  --sample "$WORK\sample_ids_bound.json" --out "$WORK\validate_derived_A.json"
```

**验收：** `ok=true`，`counts.missing=0`、`counts.extra=0`；引用的每个 proof span 都存在于 public 卷宗。

### 2.7 阶段 2：金标揭示与判定（A/B 独立）

浏览器：阶段 ② → 加载 `bundle_gold.json` + 密封 DERIVED → 逐题判定 → 导出 `annotations_verify_<X>.jsonl`。
CLI 等价：`annotate_cli.py verify ...`。

**注意：** 判定对象是“金标是否正确”，不是“我的派生是否被采纳”；两者不同是正常信息。

### 2.8 密封并校验 VERIFY

```powershell
& "D:\Conda\python.exe" "$KIT\scripts\seal_export.py" --kind VERIFY `
  --file "$WORK\annotations_verify_A.jsonl" --out "$WORK\sealed_verify_A.jsonl" `
  --public-bundle "$WORK\bundle\bundle_public.json" --gold-bundle "$WORK\bundle\bundle_gold.json" `
  --derived "$WORK\sealed_derived_A.jsonl" --receipt "$WORK\seal_verify_A.json"

& "D:\Conda\python.exe" "$KIT\scripts\validate_export.py" --kind VERIFY `
  --file "$WORK\sealed_verify_A.jsonl" --public-bundle "$WORK\bundle\bundle_public.json" `
  --gold-bundle "$WORK\bundle\bundle_gold.json" --derived "$WORK\sealed_derived_A.jsonl" `
  --sample "$WORK\sample_ids_bound.json" --out "$WORK\validate_verify_A.json"
```

对 B 重复 2.5–2.8。

### 2.9 一致性统计

```powershell
& "D:\Conda\python.exe" "$KIT\scripts\agreement.py" `
  --a "$WORK\sealed_verify_A.jsonl" --b "$WORK\sealed_verify_B.jsonl" `
  --derived-a "$WORK\sealed_derived_A.jsonl" --derived-b "$WORK\sealed_derived_B.jsonl" `
  --sample "$WORK\sample_ids_bound.json" --out-dir "$WORK\agreement"
```

**输出：** `agreement_report.json`、`disagreements.jsonl`、`AGREEMENT_SUMMARY.md`。检查 H1：每维 `agreement_rate ≥ 0.98` 且 `coverage.complete=true`。

### 2.10 和解（仅分歧）

A/B 各自看对方在分歧条目上的标签与理由，提交书面解释；不得直接改阶段 2 标签（若双方书面确认同一修正，必须在仲裁理由中记录）。

### 2.11 仲裁（C）

浏览器阶段 ③ 加载 A/B VERIFY + gold → 逐条分歧给出 `final_label` + `attribution` + 理由 → 导出 `adjudications.jsonl`。
或者手写 JSONL（`schema/adjudication.schema.json`），关键错误必须 `GOLD_DEFECT`，UNDECIDABLE 必须 `UNRESOLVED`。

### 2.12 合并与裁决

```powershell
& "D:\Conda\python.exe" "$KIT\scripts\adjudicate.py" `
  --a "$WORK\sealed_verify_A.jsonl" --b "$WORK\sealed_verify_B.jsonl" `
  --gold-bundle "$WORK\bundle\bundle_gold.json" --out-dir "$WORK\verification" `
  --adjudications "$WORK\adjudications.jsonl" --sample "$WORK\sample_ids_bound.json" `
  --derived-a "$WORK\sealed_derived_A.jsonl" --derived-b "$WORK\sealed_derived_B.jsonl" `
  --qual-a-derived "$WORK\qual_ann_a_derived.jsonl" --qual-a-verify "$WORK\qual_ann_a_verify.jsonl" `
  --qual-b-derived "$WORK\qual_ann_b_derived.jsonl" --qual-b-verify "$WORK\qual_ann_b_verify.jsonl" `
  --qual-gold "$WORK\qualification\qualification_bundle\bundle_gold.json" `
  --qual-items "$WORK\qualification\qualification_ids.json"
```

**输出：** `HUMAN_VERIFICATION_REPORT.json`（`PASS`/`FAIL`）、`final_labels.jsonl`、`gold_defects.jsonl`（如有）。
**验收：** 只有 `PASS` 才能写“人工双标核验通过”；`FAIL` 时按 §3 处理。

---

## 3. 金标缺陷路径（H2 FAIL）

1. `gold_defects.jsonl` 中的 item 标 `GOLD_QUARANTINED`，在数据卡/论文中列为不可用于确认性分析。
2. 由 t5/t6 重推 solver、重生成证书；**不得手改金标值**；修复记录 append 到缺陷清单。
3. 仅对修复后的 item 重新执行阶段 1–2–4（可只重标缺陷子集），并在报告中标注 `reverified_at_utc`。
4. 若缺陷 >2/100 或同一机制 ≥2 题：停止发布，升级为设计/构建问题（合同 amendment）。
5. 不得把缺陷题从 100 题中剔除后重算 H1 并声称 PASS。

---

## 4. 时间与角色

| 活动 | 人 | 预计 |
|---|---|---|
| 绑定 + bundle + 预标注 | 数据管理员 | 0.5–1 天 |
| 资格测试（含培训） | A/B | 0.5 天/人 |
| 阶段 1（100 题） | A/B | 8–12 小时/人 |
| 阶段 2（100 题） | A/B | 4–6 小时/人 |
| 和解 + 仲裁 | A/B/C | 2–4 小时 |
| 统计 + 报告 | 数据管理员 | 0.5 天 |

合计约 **3–5 个工作日**（不含缺陷修复轮次）。预算：0 付费 API；本地推理仅用于可选的预标注提示。

---

## 5. 停机规则（遇到即停，不得绕过）

| 情况 | 动作 |
|---|---|
| 合同/预注册哈希漂移 | 停；`check_baseline.py` 已会报错 |
| `build_index.json` 缺失/不完整 | 停；要求构建方补齐，不得猜测绑定 |
| 绑定 item 数 ≠100 或层容量不符 | 停；不得跨层替换 |
| bundle 泄漏筛查 FAIL | 停；报 t8；不得标注 |
| 标注者提前看 gold | 该标注者数据作废，重做 |
| 导出未密封/校验失败 | 停；修工具或重导，不得手工补哈希 |
| H1 <98% | 停；分析是协议理解问题还是标注者问题；重训后重标（记录轮次） |
| H2 有确认缺陷 | 隔离、修复、重验；不得声称通过 |
| H3 不通过 | 该标注者不得进入正式样本 |
| 发现数据泄露 | 立即停；报告 captain/t8 |

---

## 6. 移交接收检查表（打印后逐项签字）

- [ ] 已读 `ANNOTATION_PROTOCOL.md` §1（术语消歧）与 §3（四维判定）。
- [ ] 已读 `SAMPLING_PLAN.md` §3–§4（抽样与绑定规则）。
- [ ] 已确认 `sample_ids.json` 的 100 个 slot 覆盖 28 层（`make_design.py validate` exit 0）。
- [ ] 已确认构建发布 `build_index.json`（含 block/cell 或 mechanism/dose）。
- [ ] 已运行 `run_selftest.py` 且 `ok=true`（工具/统计在合成数据上可用）。
- [ ] 已确认 P1–P7 全部满足。
- [ ] 已签署保密与利益冲突声明。
- [ ] 已理解：本阶段不产生人工金标；PASS 之前论文必须列“人工双标未执行”为阻断项。

---

## 7. 结尾声明

> 本移交包**不产生人工金标**。真实 R28 数据上 `adjudicate.py` 返回 `PASS` 之前，论文必须把“金标未经独立人工双标核验”列为发表阻断项。
