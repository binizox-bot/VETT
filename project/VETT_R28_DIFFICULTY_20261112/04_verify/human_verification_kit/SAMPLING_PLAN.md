# R28 人工核验分层抽样方案（SAMPLING_PLAN v1）

**任务：** t24（人工核验就绪包；不执行人工标注）
**抽样对象：** R28 发布集（`development` split，一题一记录、一题一族）
**样本量：** **100 题**（固定）
**随机种子：** **20261112**（固定）
**清单文件：** `sample_ids.json`（当前为 100 个设计 slot；构建后绑定真实 `item_id`）
**框架版本：** `VETT-R28-CONTRACT-20261112-v1` **v1.1.0**（AMEND-001，`n_published = 320`）

> **关于任务书中的“160 题”**：t24 任务书写于合同 v1.0.0（N=160）。AMEND-001 已由用户在 t25 确认门授权把 `n_published` 改为 320。本方案以冻结合同 v1.1.0 为准生成 **100/320**；同一 100 题分配对 N=160 也成立（因为因子核每格 4≥3、剂量阶梯每格 8≥5），因此额外生成 `sample_ids_n160_legacy.json` 作为历史兼容件。论文/报告必须引用当前冻结合同（N=320）的 `sample_ids.json`。

---

## 1. 抽样框

R28 发布集由合同 §5 的两块组成（N=320）：

| 块 | n | 结构 | 格数 | 每格容量 |
|---|---:|---|---:|---:|
| 因子核 `factor_core` | 128 | 2⁴ 全因子（D1–D4 各 0/1） | 16 | 8 |
| 剂量阶梯 `dose_ladder` | 192 | 4 机制 × 3 剂量，其余机制固定 0 | 12 | 16 |
| **合计** | **320** | 64 场 × 5 题 | **28** | — |

- 一题一记录（互异率 = 1.0）；一题一族；`variants/` 的 320 份对照渲染**不在**样本框内（双渲染一致性由 HA8 机器检查）。
- held-out 40 题（16 因子格×1 + 12 剂量格×2）**不在**样本框内；资格测试使用合成校准题，不消耗 held-out。
- 抽样框的权威定义是 `design_manifest_n320.json`（由冻结合同派生，320 个 slot），不是“文件系统里碰巧有多少文件”。

---

## 2. 分层变量（28 层）

**层 = 一个设计格。** 这样定义的原因是：合同的剂量语义是“每实例独立赋值”，因子核的层是 (D1,D2,D3,D4) 的**剂量向量**，不是单一机制；剂量阶梯的层是 (机制, 剂量)。两层不能混成 12 个“机制×剂量”而不丢失因子核信息。

| 层 ID 形式 | 数量 | 配置 | 层内题数（N=320） |
|---|---:|---|---:|
| `FC:<4bit>`，如 `FC:0101` | 16 | D1..D4 = 各位（0/1） | 8 |
| `DL:<Dk>=<level>`，如 `DL:D3=2` | 12 | 仅 Dk = level（0/1/2），其余 = 0 | 16 |

> 注意：剂量阶梯的四个 `level=0` 层（`DL:D1=0` … `DL:D4=0`）配置全为 0，但它们是**四个不同的设计格**（分别对应“以 D1/D2/D3/D4 为主机制、剂量 0”），在构建元数据中必须保留 `mechanism` 字段才能区分；`build_index.json` 的 schema 已强制这一点（`schema/build_index.schema.json`）。

**覆盖检查：** 100 个 slot 覆盖全部 28 层；因子核每格 2–3 题，剂量阶梯每格 5 题。

---

## 3. 分配（allocation）

| 块 | 样本量 | 每层分配 | 理由 |
|---|---:|---|---|
| 因子核 | **40** | 16 格：`D1==D2` 的 8 格各 3 题，其余 8 格各 2 题 | 每格 ≥2，且四个机制在样本内各保持 20/20（0/1）平衡；与因子核占总体 40% 成比例 |
| 剂量阶梯 | **60** | 12 格 × 5 | 机制×剂量每格 5 题，保证每个 (机制,剂量) 都有覆盖；与 60% 成比例 |
| **合计** | **100** | 28 层全部覆盖，最小 2 题/层 | — |

- `D1==D2` 的 8 格是自补集合：四个机制在其中有 4 个 1、4 个 0，因此加 1 后每个机制仍保持 20/20。若简单按格索引奇偶交替 3/2，D4 会因等于格索引奇偶而变成 24/16 —— 该不平衡在自检的历史版本中被发现并修正。
- 该分配对 N=160 也合法：因子核每格容量 4 ≥3，剂量阶梯每格容量 8 ≥5。
- 不使用“按状态/驳回/账本分层”的第二套分层：这些是**记录属性**，不是设计变量；用它们分层会把“抽样”与“配额”混为一谈，且构建后属性可能偏离计划。样本代表性用事后边际检查（§6）描述，不用于加权。

---

## 4. 层内选择与确定性

### 4.1 构建前的 slot 抽样

在 `design_manifest` 的每层内，对 slot 计算：

```
key = sha256(f"{seed}|{stratum_id}|{slot_id}")
```

按 key 的十六进制字符串升序排序，取前 `sample_n` 个 slot。**不使用 Python `random`**，因此：

- 不受 `PYTHONHASHSEED` 影响；
- 不受字典/集合迭代顺序影响；
- 把 manifest 的 slots/strata 顺序完全反转后重跑，结果必须逐项相同（自检已覆盖）。

**实现：** `scripts/make_design.py sample`。

### 4.2 构建后的 item 绑定（必做）

`sample_ids.json` 在构建前只有 slot，没有 `item_id`（`status = PROVISIONAL_PENDING_ITEM_ID_BINDING`）。构建发布 `build_index.json` 后：

```
python scripts/make_design.py resolve \
  --index <build>/build_index.json \
  --sample sample_ids.json \
  --out sample_ids_bound.json \
  --receipt BINDING_RECEIPT.json --strict
```

层内真实 item 的选择顺序（**先确定性包含，再哈希**）：

1. **确定性包含（certainty inclusion）**：优先选携带稀有属性的 item，保证人工核验覆盖结构天花板与关键记录形态：
   - `DEAD_REBALL`（发布集仅 1 题）；
   - 合法送达型 dismissal：`BOWLED`、`LBW`、`CAUGHT`、`STUMPED`（各仅 2/2/2/4 题）；
   - 合同 §7.2 的 5 个“未共存事实组合”（各 ≥1 题）。
   这些 item 是 100 题内的**子集**，不是额外加题。
2. 其余位置按 `sha256(f"{seed}|{stratum_id}|{item_id}")` 升序补齐。
3. `--strict` 要求：`item_id` 100 个互异；每层 item 数 = 合同格容量（8/16）；每层候选数 ≥ sample_n；否则报错退出（exit 4），不得降级、不得静默换层。

绑定结果写入 `sample_ids_bound.json`（`status = BOUND`）与 `BINDING_RECEIPT.json`（含 build index 哈希、逐层选择、稀有覆盖、警告）。绑定后**不得**更换 item；若构建重建导致 item_id 变化，必须重新绑定并记录新 receipt。

### 4.3 稀有覆盖的已知限制

- 若 DEAD_REBALL 所在层在 100 个 slot 中未被抽到，certainty 规则无法把它塞进样本（不得跨层替换）；`BINDING_RECEIPT.json` 的 `coverage.warnings` 会报告。此时必须在限制中写明“样本未覆盖 DEAD_REBALL”，不得声称覆盖。
- 合法 dismissal 合计仅 10 题；100 题样本按 31.25% 抽样期望约 3 题。certainty 规则会在同层内优先选择，但**不保证**四类都进样本。报告必须列出实际覆盖，不得事后补题。

---

## 5. 样本量的推断与限制

### 5.1 这个 100 题能回答什么

人工双标的目标是**金标质量**，不是模型准确率。令 `p` = 发布集 320 题中“存在关键金标缺陷”的题目比例。若 100 题分层样本中关键缺陷数为 0：

- 二项 95% 上界（忽略有限总体校正）：`1 − 0.05^(1/100) ≈ 2.95%`；
- 有限总体（N=320，无放回）近似：允许总体缺陷数约 ≤10 题（约 **3.1%**）；
- 结论只能写成：“在 100 题样本中未发现关键金标缺陷；95% 置信上界约 3%，不是 0 缺陷的证明。”

若发现 1 个缺陷，不能据此估计总体率（区间极宽）；必须按 §8 隔离并修复/重验。

### 5.2 这个 100 题不能回答什么

- **不能**按层/机制估计缺陷率：每层 2–5 题，任何层内比例都无统计意义；只做描述性清单。
- **不能**替代 held-out 的模型评测；人工样本不进入模型选择，也不改变预注册端点。
- **不能**声称“金标已被完全验证”；只能声称“该样本内未发现/发现了缺陷”。
- **不能**把 100 题当独立样本外推到 R26.15（不同数据、不同记录空间）。

### 5.3 为什么不是 200 题

- 100 题是任务书规定的人工工作量上限（2 名标注者 × 2 阶段 ≈ 10–15 小时/人；200 题会翻倍且不改变“是否存在系统性缺陷”的定性判断）。
- 31.25% 的抽样比例 + 28 层全覆盖 + 稀有形态定向包含，已足以发现“系统性、成片”的金标缺陷；对 3% 以下的稀疏缺陷只能给出上界，不能保证发现。该限制必须写入论文的 Threats to Validity。
- 若后续要求更严格（例如 95% 上界 ≤1%），需要 300 题级别样本或全量核验；这属于下一阶段，不在 t24 范围。

---

## 6. 代表性检查（描述性，不改变样本）

绑定后由 `BINDING_RECEIPT.json` 与报告给出：

1. 28 层覆盖：每层实际题数 = 计划 sample_n（严格）。
2. 稀有形态：`DEAD_REBALL`、四类合法 dismissal、5 个未共存组合的实际覆盖（有/无，逐项列出）。
3. 记录边际（若 build index 提供 `status` / `dismissal` / `ledger_nonzero`）：
   - 样本 vs 发布集的 `delivery_status`、`dismissal`、`ledger.BYE/LEG_BYE/PENALTY` 非零比例；
   - 只报告差值，不做显著性检验（样本是分层抽样，不是简单随机样本；层内不独立）。
4. 若某边际差值 >15pp 且不是 design 分层造成，需在限制中说明；**不得**通过加权或换题“修好”样本。

---

## 7. 复现命令

在 `VETT_R28_DIFFICULTY_20261112/04_verify/human_verification_kit` 下：

```powershell
$py = "D:\Conda\python.exe"
& $py scripts\make_design.py manifest --n 320 --out design_manifest_n320.json
& $py scripts\make_design.py manifest --n 160 --out design_manifest_n160_legacy.json
& $py scripts\make_design.py sample --manifest design_manifest_n320.json --out sample_ids.json
& $py scripts\make_design.py sample --manifest design_manifest_n160_legacy.json --out sample_ids_n160_legacy.json
& $py scripts\make_design.py validate --sample sample_ids.json --manifest design_manifest_n320.json
```

- 两次运行 `sample` 必须产生相同的 `slots` 与 `strata`（只有 `generated_at_utc` 不同）。
- 绑定（构建后）：

```powershell
& $py scripts\make_design.py resolve --index <build_index.json> --sample sample_ids.json --out sample_ids_bound.json --receipt BINDING_RECEIPT.json --strict
```

- 自检（包含抽样确定性、绑定、kicker 全链路）：

```powershell
& $py scripts\run_selftest.py
```

---

## 8. 清单文件字段（`sample_ids.json`）

| 字段 | 含义 |
|---|---|
| `schema` | `vett.r28.human_kit.sample_ids.v1` |
| `status` | `PROVISIONAL_PENDING_ITEM_ID_BINDING`（构建前）或 `BOUND`（绑定后） |
| `frame.n_published` | 320（当前冻结合同） |
| `frame.contract_sha256` | 冻结合同文件哈希（绑定冻结） |
| `sampling.seed` | 20261112 |
| `sampling.algorithm` | `sha256-rank-v1` |
| `sampling.allocation` | `{factor_core:40, dose_ladder:60}` |
| `strata[]` | 28 层的 `stratum_id`、`block`、`cell`、`config`、`n_items`、`sample_n` |
| `slots[]` | 100 个 slot：`slot_id`、`stratum_id`、`block`、`cell`、`config`、`rank_in_stratum`、`selection_key_sha256` |
| `item_ids` | `null`（构建前）；绑定后 100 个真实 id |
| `binding.command` / `binding.receipt` | 绑定命令与 receipt 路径/摘要 |

**禁止：** 手改 `sample_ids.json`、事后增删 slot、用别的种子重抽来“修复”覆盖、把未绑定 slot 当作真实 item 去生成 bundle。

---

## 9. 失败模式与停机规则

| 情况 | 动作 |
|---|---|
| 合同/预注册哈希漂移 | 停机（`make_design.py` 直接报 `CONTRACT_DRIFT`） |
| 构建 item 数 ≠ 320 或层容量 ≠ 8/16 | `resolve --strict` 报错；不得降级绑定 |
| `build_index.json` 缺少 block/cell/mechanism/dose | 报 `BUILD_INDEX_INCOMPLETE`；要求 t5/t6 补齐后重试 |
| 绑定后 item_id 重复/缺失 | 报错；不得用顺序猜测 |
| 样本层覆盖不足 | 报错；不得跨层替换 |
| 稀有形态未覆盖 | 记录 warning + 论文限制；不得补题 |

---

## 10. 结尾声明

> 本抽样方案只为人格核验准备样本，**不产生人工金标**。100 题样本是金标质量的分层审计样本，不是模型评测集，也不是“金标已验证”的证明。
> 在真实数据上 `adjudicate.py` 返回 `PASS` 之前，论文必须把“金标未经人工双标核验”列为发表阻断项。
