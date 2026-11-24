# R28 合同复核包（人工确认门 t25）

**2026-11-12**｜复核对象：预注册 `VETT-R28-PREREG-20261112-v1`（`fdd744b8…0f11`，endpoint `0ee0a5fc…82ccf`）+ 数据合同 `VETT-R28-CONTRACT-20261112-v1`（`d0b2fc1d…2988`，冻结 11:01:32Z）
**状态：已确认并放行（用户 2026-11-12 在 t25 确认门给出结论）。** 已执行 AMEND-001：预注册与合同均升级为 **v1.1.0（N=320）**；t5/t12/t13/t24 解锁。合同自检 117/117、预注册自检 123/123 PASS（含 R26.15 零漂移）。

## ✔ 确认结果（2026-11-12，t25 人工门）

| 问题 | 用户决定 | 已落地的改动 |
|---|---|---|
| Q1 功效/样本量 | **B2：n_published=320** | 预注册 v1.1.0：N=320、640 次 E1、功效锚 10pp 80.7%/MDE 9.91pp/CI ±6.93pp、有效 n 320/320/320；合同 v1.1.0：blocks 128/192、scenes 64 |
| Q2 结构天花板 | **接受，但合法 dismissal 封顶 ≤11、禁止简单乘 2** | 配额表 N=320：合法 dismissal 10 + DEAD 1 = **11**；新增题位给 NONE/RUN_OUT/OBS/HIT；NONE=124/320=**38.75%**（未回弹 48%）；HA18 与 CEIL-5 写死；数据卡将披露"这是 solver 表达力限制，不是抽样偏差" |
| Q3 renderer 扩展 | **接受，但必须证明生效** | 合同要求：revision chain 可逐步回放（版本身份+生效时间可核）、≥2 冲突源可裁决到同一 solver_facts；证不出的部分标 PRESENTATION_ONLY、不得计入机制/更难主张 |

**新冻结指纹：** 预注册 `5e0056e1…122`（endpoint `67c171a9…b3af`，11:29:17Z）｜合同 `7f10f983…94b`（quota digest `edbe23de…70c`，HA digest `21a30b98…ef74`，11:30:51Z）。AMEND-001 已写入 `prereg_amendments.jsonl` 与 `02_contract/contract_amendments.jsonl`（含用户授权声明与 before/after）。

## ① 需要你拍板的 3 个问题

**Q1（第一问题）功效不足——N=160 检不出 10pp，是否扩量？**
预注册要求点估计 ≥10pp 且两个 95% CI 下界 >0；但 n=160、40% 不一致率下 SE=5.0pp、CI ±9.8pp → **10pp 功效仅 51.6%（80% MDE≈14.01pp）**。记录空间已实测可扩（下界 761），瓶颈是功效不是算力（本地 ¥0）。

| 选项 | N | 10pp 功效 | 80% MDE | 互异记录需求* | E1 推理 | 后果 |
|---|---:|---:|---:|---:|---:|---|
| **A 保持** | 160 | **51.6%** | 14.01pp | 216 | 320 | 最省；10pp 大概率只报"方向一致" |
| **B 扩量** | 240 | **68.8%** | 11.44pp | 304 | 480 | 需 amendment+t8+你签字；仍不保证 10pp |
| **B2 扩量** | 320 | **80.7%** | 9.91pp | 392 | 640 | 达 80% 功效的最小值；工作量约翻倍 |
| **C 改口径** | 160 | 51.6% | 14.01pp | 216 | 320 | 结论限定"可可靠检出 ≥14pp"，最诚实最弱 |

\* 含 40 题 held_out + 10% 余量。B/B2 的预注册 amendment 只需改 `n_published` 一个参数（块/配额/功效自动派生）；**未决策默认 A，执行方不得自行扩量**。

**Q2 记录形态结构天花板是否接受？** solver 限制：`DEAD_REBALL` 仅 **1 条**可达记录；`BOWLED/LBW/CAUGHT` 各 **2 条**、`STUMPED` 4 条（合法 dismissal 合计 **≤10 题**）；`WIDE` 下 BYE/LEG_BYE 恒 0。合同据此把"四类都有量"改为 **"四类都出现"**（DEAD_REBALL=1）并披露。**接受 / 要求扩 solver（推迟到 R29+ 且改金标语义）？**

**Q3 是否接受 D2/D3 新增 renderer + 每题独立紧凑 dossier？** D2 现有 `temporal_joins` 只加 1 个 bridge span，**需 t5 实现真 revision chain**（2→3 版本、沿链回放）；D3 现有仅 1 个冲突源，**需扩展到 ≥2 冲突 + masked cell**；每题独立 dossier、**prompt ≤7000 tokens**（8192 上下文；长上下文已判 REJECTED）。**接受 / 缩减 D2/D3 为二元（改因子设计，需 amendment）？**

## ② 机制先例（写死）

**VERIFIED 0 ｜ UNTESTED 6 ｜ REJECTED 3 —— 当前没有任何机制被证实能提高难度**；R28"更难"只能由 E2 建立。
- **推翻 1：** "63.3/60.0/51.7 等级落差 ⇒ 剂量杠杆已验证"——那是整级宏准确率；同事实组逐对 **10 对 = 5 降/4 升/1 平，均值 −3.3pp，p=0.50** → 改为 HYP-R28-DOSE（UNTESTED，唯一裁决 E2）。
- **推翻 2：** "推导深度不可调节"——同事实组 `rule_operators` 1→2/2→3/3→4 而金标逐字节相同 → **UNTESTED**，须 t5 用 solver 验证。
- **B1：** 描述性 PASS、预测性 **UNTESTED**；`can_redesign_levels_from_25_questions=false`，禁止据 25 题重设等级。

## ③ 四个可调剂量（全 UNTESTED；只改呈现层，`solver_facts`/`decision_record_flat` 不变）

| 剂量 | 参数 | 0 | 1 | 2 | t5 |
|---|---|---|---|---|---|
| **D1** 证据跳数 | `alias_hops` | 事实直接以 CASE 编号命名主体 | 1 个 locator（register→token） | locator+bridge（token→packet+时间/over） | 现有支持，改按实例取值 |
| **D2** 修订链 | `temporal_joins` | 无修订 | 2 版本（被替代值+现行值，按 revision/pre-lock 选一） | 3 版本、跨 2 字段，沿链回放两次 | **新增 revision-chain** |
| **D3** 权威裁决 | `scope_decisions` | 单一权威 | 2 源冲突+policy | ≥2 冲突（3 源）+policy+masked cell | **扩展 ≥2 冲突+masked** |
| **D4** 干扰同构度 | `isomorphic_distractors` | 无干扰 | 1 个同构 shadow | ≥2 个，其中 1 个 near-miss（除 1 事实外全同） | 现有计数支持；near-miss 需新增 |

## ④ 三集合拆分与验收阈值

| 集合 | 内容 | 硬验收 |
|---|---|---|
| **发布集** `public/`+`private/` | 160 题（32 场×5），一题一记录，每族 ≤1 题 | 互异率 **1.0**；恒定字段 **0**；BYE/LEG_BYE/PENALTY 非零 **46/38/78**；每格 ≥2 status/≥2 dismissal；prompt ≤7000 tokens；族名基线 lift-over-marginal（AMEND-002） |
| **对照集** `variants/` | 每题一份配对渲染（四剂量全 0） | `solver_facts`+`decision_record_flat` **逐字节相同 160/160**；题面 160/160 相同；两臂证书重推 **100%** |
| **实验集** `eval_runs/` | 160 对 = **320 次**推理（本地 7B，temperature=0） | 主端点 `paired_accuracy_drop`（9 信息字段 ITT，分母 160×9）；McNemar+两种 bootstrap；基线 52.89/54.22/73.33+exact 32；停止规则 S1–S13 |

两块：因子核 **64**（2⁴×4）+ 剂量阶梯 **96**（4 机制×3 剂量×8）。同 seed 确定性重建；R26.15 只读（165 文件/93,346,177 字节/聚合 `343afde4…51bd`）。

## ⑤ 分层定向枚举配额（写死，禁止随机采样）

**记录空间：** 定向枚举**下界 761**（15,840 组构造事实、0 失败、67 层）；随机 2 万只得 156（NONE 74%），**旧"160 近天花板"作废**。

| 状态 × dismissal | NONE | RUN_OUT | OBSTRUCTING | HIT_BALL_TWICE | BOWLED | LBW | CAUGHT | STUMPED | 合计 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LEGAL | 31 | 19 | 13 | 13 | 2 | 2 | 2 | 2 | **84** |
| NO_BALL | 19 | 13 | 8 | 8 | — | — | — | — | **48** |
| WIDE | 11 | 6 | 4 | 4 | — | — | — | 2 | **27** |
| DEAD_REBALL | 1 | — | — | — | — | — | — | — | **1** |
| **合计** | **62** | **38** | **25** | **25** | **2** | **2** | **2** | **4** | **160** |

**怎么避免 NONE 74%：** ① NONE 上限压到 **62/160=38.75%**；② 强制 RUN_OUT 38、OBS 25、HIT 25、合法 dismissal 10；③ 每层配额 ≤ 该层可达记录数；④ 格分配"同 status/dismissal 最少优先"（16 格×4、12 格×8 全满，每格 ≥2 status/≥2 dismissal）；⑤ 强制覆盖 5 个"从未共存"事实组合（如 `appeal_made=False+LBW`、`contact=PERSON+wide_called=True`）各 ≥1 题。账本非零：BYE **46**、LEG_BYE **38**、PENALTY **78**（旧 0/0/0）。

## ⑥ 与 AUDIT 的对应：哪些旧主张已被推翻

| 旧主张 | 状态 | 现结论 |
|---|---|---|
| "63.3/60.0/51.7 ⇒ 剂量杠杆已验证"（§3.2） | **推翻** | 10 对 5 降/4 升/1 平，p=0.50 → HYP-R28-DOSE UNTESTED |
| "推导深度不可调节/REJECTED"（§3.2） | **推翻** | 1→2/2→3/3→4 金标不变 → UNTESTED，t5 验证 |
| "记录空间数百、160 近上限"（§4） | **修正** | 定向 761；N 最多约 640；瓶颈是功效 |
| "互异≥0.9×题数 + 每题双渲染"（§3.3） | **冲突已解** | 发布 160 互异记录 + `variants/` 160 配对，两集合分开 |
| "加文档/加长上下文能加难"（§4） | **REJECTED** | 信息字段 4.033→4.200→4.552；80K−15K=+0.552 |
| "L1–L5 可据 25 题重设计"（§3.2） | **不可用** | B1 预测性 UNTESTED；每级 n=5；族分类器 100% |
| "66.33% 可证明读卷宗"（§4） | **推翻** | 题面 LR 54.22 vs GLM 55.11；anchor 73.33 → 三基线门槛 |
| "Brier vs 0.25 / edge 0.7696=给定正确节点"（§2/§5） | **作废** | 气候学 0.2016、skill −2.11；边指标五分列 |

## ⑦ 确认后

- **A/C：** t5 按 N=160 开工（生成器+D2/D3 renderer+分层枚举），t6 构建；t12/t13/t24 解锁。
- **B/B2：** 先走预注册 amendment（只改 `n_published`）+ t8 + 你签字，再按新 N 构建；其余条款不变。
- **未确认：** 停在 t4/t25，不生成数据、不调用模型；t25 保持 in_progress。全程零付费 API、不修改 R26.15 任何字节；金标/证书只由确定性 solver 生成。

**相关文件：** `02_contract/R28_CONTRACT.md`、`02_contract/r28_contract.json`、`preregistration.json`、`02_contract/evidence/{record_space_probe,quota_assignment_check,power_ladder}.json`。
