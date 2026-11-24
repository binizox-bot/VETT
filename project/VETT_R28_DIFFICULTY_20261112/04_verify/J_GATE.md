# J 门 — 哪些标注能进主分析，哪些不能

| | |
|---|---|
| **门号** | `VETT-R28-GATE-J-20261112` |
| **执行** | judge_architect（t17） |
| **机器可读** | [`J_GATE.json`](J_GATE.json)（含逐条证据与命令） |
| **复算脚本** | [`scripts/j_gate.py`](scripts/j_gate.py)（纯标准库、只读、零网络、零模型） |
| **前置** | `02_design/protocol_verify.py --check` → **22/22 PASS**（协议唯一来源 `02_design/protocol.json`） |

> **一句话结论**：本地 T1、T2 可以进主分析（但 T1 只是"词表匹配"、T2 需先关掉一个卫生项）；
> 本地 S1、C1 在 R28 上**不能当门**；云端 T1/T2 可作参考标尺；云端 T3（n=12）只能作描述性，
> 而且它的 overall 判定是平凡策略、模型自写的"正确记录"与金标只有 0.4541 量级的字段一致。

---

## 0. 门判定总表

| 项 | 内容 | 判定 | 能否进主分析 |
|---|---|---|---|
| J0 | 协议前置 22/22、绑定 prereg/contract v1.2.0 | **PASS** | 前置满足 |
| J1-T1 | 本地 T1 vs 分层机械真值（n=320） | **PASS** | **可**（逐类 + 逐 role 披露） |
| J1-T2 | 本地 T2 序判定（n=317 有效） | **PASS** | **可**（J8 已于修复后关闭） |
| J1-S1 | 本地 S1 span 主题（n=320） | **INSUFFICIENT** | **否**（只可描述） |
| J1-C1 | 本地 C1 证书逐句（R28 未运行） | **INSUFFICIENT** | **否** |
| J1b | 分层真值与卷宗文本的落地核验 | **PASS** | 佐证 |
| J1c | T1 短路审计（词表 vs 语义） | **SHORTCUT_FLAG** | 限定 T1 的解释力 |
| J2 | 云端 vs 机械真值（T1 24/24、T2 16/16、T3 描述性） | T1/T2 参考、T3 **DESCRIPTIVE_ONLY** | T1/T2 参考；T3 否 |
| J3 | 跨模型 kappa | **NOT_ESTIMATED**（全部臂 n<30） | 不估计 |
| J4 | 自一致（本地 10% 重测） | **PASS** | 佐证 |
| J5 | 对抗探针 | **NOT_RUN** | 未测量（写进局限） |
| J6 | 盲包泄漏审计（64 包） | **PASS** | 佐证 |
| J7 | 账本与重放绑定（R-R7） | **PASS** | 佐证 |
| J8 | 模板卫生（`T2.naturalness_pair.choice.v1`） | **PASS**（已关闭） | **可**（五条判据全部满足） |
| J9 | 分歧率 vs 30% 阈值 | **PASS** | 协议无需改 |
| J10 | 退化真值护栏（`t1_override_truth` 全 false） | **GUARDED** | 说明为何用分层真值 |
| J11 | T3 数据欠定 5 条 | **TRANSFER_TO_T11** | 不得填补 |
| J12 | t16 `C_t14` 状态翻转 | **FLAG_NOT_ADMISSIBLE** | 空洞翻转，不可引用 |
| J13 | 无区分度维度 | **NO_DISCRIMINATION** | abstain/conformance/overall 不可当门 |

**阻塞项：无。** J8 已由 local_operator 修复；本门**独立复算**后关闭（见 §9 的 C1–C5），未采信其自报。

---

## 1. 前置：协议 22/22，且绑定到最新的上游文书

- `protocol.json` sha256 = `1a87c3165353f5ec…c50c1293`（PAMEND-004 后；PAMEND-003 时为 `a07463aa…02ff7a`），
  `PROTOCOL.md` = `9758d0e1fc8e1390…7eb4300e`，`protocol_freeze.json` = `ab18ee1bffe17322…0f0761697e`；
  `--check` **22/22 PASS**（V1–V22）。
- 绑定版本：`preregistration v1.2.0`（AMEND-002）、`r28_contract v1.2.0`（AMEND-002）。
- 说明：AMEND-002（captain 裁决：per-cell accuracy 混淆边际偏斜与泄漏，泄漏统计量应为
  lift-over-marginal）只改 HA10 口径，不触及协议管辖的任何规则；协议以 **PAMEND-002**
  做"绑定刷新、规则零改动"并重新冻结（见 `02_design/protocol_amendments.jsonl`）。
  在这之前 `--check` 确实报 FAIL（V22 `PROTOCOL_DRIFT`）——冻结机制按设计工作。
  另有 **PAMEND-003**（captain 指令，发布阻塞项）：把 R28 自身 id 形态 `r28q_` / `r28h_` /
  `rfam_` / `r28*_span` 补进盲包禁用模式表（首冻时这些形态还不存在）。补入后新表复扫 64 个既有盲包
  **仍 0 违规**，且四类注入均被 V11 阻断。

---

## 2. J1：本地 vs 机械真值

### 2.1 T1 因子可见性 —— **PASS**，但必须逐类读

| 指标 | 值 |
|---|---|
| 总体 | **0.9750**（312/320），Wilson95 [0.9515, 0.9873] |
| `NEG_PLAIN` | **1.0000**（192/192） |
| `NEG_PROVENANCE_ADJACENT` | **1.0000**（80/80） |
| `POS_OVERRIDE` | **0.8333**（40/48），Wilson95 [0.7042, 0.9130] |
| 门槛 / 最小 n | 0.85 / 30（三类各 48–192，均达标） |

**为什么不能只看总体**：这份分层真值下 `constant-false` 就能拿到 **0.8500**（272/320），
正好等于门槛；也就是说总体 0.9750 的"余量"只有 +0.1250（lift over majority）。
若用 t14 recon 自报的 `t1_override_truth {"false": 320}`（全 false），一律答 false 即 0.8500 ≥ 0.85
→ 闸门被平凡策略满足（J10）。**因此 T1 只能以分层真值 + 逐类报告的形式当门。**

### 2.2 T2 自然度 —— **PASS**（只报序判定）

| 指标 | 值 |
|---|---|
| 有效 n | **317**（3 条 `function_word_swap` 腐蚀无效被剔除：r28q_0067/0099/0159） |
| 序判定一致率 | **0.9905**（314/317），Wilson95 [0.9725, 0.9968] |
| 分腐蚀器 | duplicate 80/80、shuffle 80/80、half_splice 77/80、function_word 77/77 |
| 模板 / 指标 | `T2.naturalness_pair.v1` 320/320；`ordinal_preference_from_frozen_T2v1_scores` 320/320 |
| 绝对分 | clean {2:4, 3:31, 4:163, 5:122}、degraded {1:15, 2:277, 3:23, 4:5} —— **仅描述**，进阈值即 FAIL |

已逐一验证 `correct == (clean_score > degraded_score)`（320/320 无例外），即评分确实是序口径。

### 2.3 S1 span 主题 —— **INSUFFICIENT**（不能当门）

R28 的 span 是叙述性事实/规则句，**不存在可独立复算的机械主题真值**：模型行 207、机械词表回退
PROVENANCE 96、DEGRADED 17。用回退标签算"准确率"等于自己判自己。t18 的 1.0（n=32）建立在
R26.15 字段词组 span 上，**ALLOW 不能平移**（R-Q3 fail-safe）。→ 只能 DESCRIPTIVE_ONLY。

### 2.4 C1 证书逐句一致性 —— **INSUFFICIENT**

R28 上没有 C1 产物（t21 未交付）。t18 的 1.0/30 是 R26.15 证书句，不能当作 R28 的测量。

### 2.5 J1b：分层真值站得住（独立佐证）

| 类别 | n | span 覆盖率 | override 词表命中率 | provenance 词表命中率 |
|---|---:|---:|---:|---:|
| `POS_OVERRIDE` | 48 | 1.0 | **0.8333** | 0.6250 |
| `NEG_PLAIN` | 192 | 1.0 | **0.0000** | 0.1354 |
| `NEG_PROVENANCE_ADJACENT` | 80 | 1.0 | 0.0625 | 0.6000 |

320/320 的 `passage_span_id` 都能在 R28 公开卷宗（6,539 个 span）里定位；POS 类压倒性含覆盖语汇、
`NEG_PLAIN` 完全不含（Δ = 0.8333）。**这是佐证，不是真值来源**——真值来自刺激构造。
注意 5/80 的 `NEG_PROVENANCE_ADJACENT` 含覆盖词：这正是"来源相邻但无覆盖"的硬负例，
说明词表本身不够，不能拿来当真值。

### 2.6 J1c：T1 的失败**集中在一个构造**上（稳健结论），但"词表匹配"不是机制断言

POS 类 2×2（**仅在声明的 `OVERRIDE_LEXICON` 下**）：

| | 词表命中 | 词表不命中 |
|---|---:|---:|
| 本地答对 | 40 | 0 |
| 本地答错 | 0 | 8 |

**稳健的部分**：8 个错**全部**落在 `authority_policy` 这一种构造上（`pos_error_roles = {"authority_policy": 8}`），
即同一句 `For this delivery the signed observation is the controlling source; unsigned copies may be quoted but never used…`。
按 span role 分组：

| role | n | 一致率 |
|---|---:|---:|
| fact | 192 | 1.0000 |
| locator | 32 | 1.0000 |
| revision_version | 32 | 1.0000 |
| distractor | 32 | 1.0000 |
| **authority_policy** | **32** | **0.7500** |

**不稳健的部分（t8 F1 复核后已从本门撤下）**：上一版写过"错集 == 词表不命中集，集合完全相同"。
该等式**依赖词表把 `controlling` 排除在外**：把 `controlling` 加进词表后，不命中集变 **0** 而错误仍是 8，
等式即破（`broad_semantic` 变体同样为 0/8）。因此**该等式不得作为机制断言引用**。

| 词表变体 | POS 不命中数 | 等于错集 | NEG_PLAIN 误命中 |
|---|---:|---|---:|
| declared（本门原用） | 8 | 是 | 0/192 |
| +`controlling` | 0 | 否 | 0/192 |
| broad semantic | 0 | 否 | 0/192 |

**后果（t11/t23 请按此表述）**：T1 仍可作标注劳动（0.9750 过门），但
① **不得**当作"本地能判断证据支持"的能力证据；② 必须按 span role 分组披露，`authority_policy` 子组 0.7500；
③ 统一表述为"**8/8 错误集中在 authority_policy 构造；POS 0.8333；恒答 false 基线 0.8500**"。

## 3. J2：云端 vs 机械真值

### 3.1 T1（两臂）

| 臂 | n | 云端 vs 真值 | 可逐条比较的题 | 本地 vs 云端分歧 |
|---|---:|---:|---:|---|
| R28 分层臂 | 24 | **1.0000**（24/24） | 17（其余 7 题云端用 authority/revision span，t14 标的是别的 span） | 0/17 = **0.0000** |
| 同刺激对照臂（t18 冻结 prompt） | 24 | 1.0000（24/24） | 24 | 2/24 = **0.0833** |

7 题不可比的明细（`J_GATE.json#/items/J2_cloud_vs_mechanical/T1_r28_arm/unmatched_items`）：
r28q_0090（authority_conflict vs fact）、r28q_0250/0272/0249（authority_conflict vs authority_policy）、
r28q_0010（distractor vs fact）、r28q_0289（fact vs distractor）、r28q_0257（fact vs authority_policy）。

### 3.2 T2：16/16 序判定正确（n=16 < 30，仅参考）；云端 clean 侧 16/16 给 5 分 → 绝对分不可比
（这正是"绝对分只作描述"的实证）。

### 3.3 T3 提报裁定 —— **DESCRIPTIVE_ONLY**（n=12，不足以做推断性主张）

| 维度 | 分布 |
|---|---|
| fields | DEFECT 9 / PASS 1 / UNSURE 2 |
| span | DEFECT 12 |
| edge | DEFECT 9 / PASS 1 / UNSURE 2 |
| abstain | PASS 12（**无区分度**） |
| conformance | PASS 12（**无区分度**） |
| overall | DEFECT 12 |

用 solver 金标独立重算（12 条提报 × 12 字段）：

- **12 条提报全部真的与金标不同** → `overall=DEFECT` 的平凡策略也是 12/12，**overall 不能当质量门**；
- 逐字段 verdict：**precision 0.9333**（28/30 标记正确）、**recall 0.6087**（46 个真错字段漏 18）；
- 云端自己写的 `correct_record` 与 solver 金标只有 **0.4514**（65/144 字段）一致
  → **模型输出绝不能当金标**（R-M1/R-M2 的实证）。

---

## 4. J3 跨模型 kappa —— **NOT_ESTIMATED**

| 臂 | 可配对 n | 判定 |
|---|---:|---|
| T1 R28 臂（同 span 子集） | 17 | 不估计（n<30） |
| T1 同刺激臂 | 24 | 不估计（n<30） |
| T2 | 16 | 不估计（n<30；且两臂非同刺激） |
| （探索性）T1 两臂合并 | 41 | kappa 0.8951，CI [0.7192, 1.0]，**只作量级、不得进主表** |

---

## 5. J4 自一致 —— 本地 **PASS**，云端 **NOT_RUN**

| 任务 | 重复数 | 完全相同 | 比例 |
|---|---:|---:|---:|
| T1 | 32 | 32 | 1.0000 |
| S1 | 18 | 18 | 1.0000 |
| T2 | 32 | 32 | 1.0000 |

云端未做 10% 重复 → 云端自一致**未测量**，不得声称 ≥0.90（R-Q5）。
本地 1.0 是本次实测，不等于"确定性"（t18 记录过 152 样本里 1 次 1 分移动）。

---

## 6. J5 对抗探针 —— **NOT_RUN**

本轮没有交换记录/篡改字段/不可答题的探针产物。后果：云端对抗鲁棒性未验证；
由于 T3 输出本就是描述性，不阻断主分析，但必须写进 t11 的局限。

---

## 7. J6 盲包泄漏审计 —— **PASS**

- 审计 **64** 个包（T1 48 + T2 16），用冻结协议 `judge_protocol.audit_packet`：**0 违规**。
- 额外用更严的 R28 id 形态扫描（`r28q_\d{4}`、`r28(fact|rev|auth|policy)_…`、`FC_/DL_` 族码）：**0 命中**。
- 最大 token 估计 130（T1 上限 3000、T2 上限 2000）。
- **协议模式覆盖（已关闭，两轮）**：首冻时禁用模式表不含 R28 id 形态（协议早于该 id 方案）→
  **PAMEND-003** 补 4 条；t8 预检发现 PAMEND-003 的 span 前缀白名单只覆盖 5/10 个实测前缀
  （漏 `r28rule_`1,378 / `r28bind_`112 / `r28conflict_`112 / `r28revpolicy_`96 / `r28masked_`32 = 1,730 条）
  → **PAMEND-004** 改为**形状规则** `(?i)\br28[a-z0-9]+[-_][0-9a-z_-]{2,}\b`（新增前缀无需再改协议）。
  现行模式表 **10 条**；`reaudit_packets --inject-selftest` 从数据集**自动派生**前缀逐个注入 →
  **13/13 blocked**、64 个既有盲包 0 违规；误报实测 0（320 份公开卷宗 1,046,911 字符文本里 `r28` 出现 0 次）。

---

## 8. J7 账本与重放 —— **PASS**

| 项 | 值 |
|---|---|
| 标注账本 | `03_build/local/t14/runs/t14_main/local_cost_ledger.jsonl`，**905** 行 |
| 必填字段缺失 | **0** |
| 模板版本 | T1v1 323 / S1v4 242 / T2v1 340（全部当前版本） |
| R-R7 旧解析器条目 | **0**（无需排除） |
| 参数 | temperature 0.0 / seed 20261112 / num_ctx 8192 / num_predict 128 与 96 |
| model_digest | `845dbda0ea48ed74…` 905/905 |
| 缓存键 v2 复算 | **806/806** 与对象文件名逐位相同（用缓存对象自带的 prompt 复算） |

计费账本 `cost_ledger.jsonl`（976 行）缺 `prompt_template_version/temperature/seed` 是**设计如此**，
它是计费账本、不是标注账本，按 R-R2 不得用来重建标注。

**字段语义告警（非阻塞）**：annotations/ledger 的 `input_sha256` ≠ 缓存对象里 prompt 的 sha256
（r28q_0001：标注 `218441b2…`，对象 `9c6316f0…`），因此它不能定位缓存对象；可靠指针是
`annotation.cache_key`。建议改名为 `packet_sha256` 或另存 `prompt_sha256`。

---

## 9. J8 模板卫生 —— **PASS**（已关闭）

历史：本门在 t17 判 FAIL（变体进了 `t14_smoke` 的 cache/ledger，且 `t14_main/config.json` 仍声明该字段）。
local_operator 修复后，本门按**五条判据**独立复算（不采信自报），全部满足：

| # | 判据 | 实测 |
|---|---|---|
| **C1** | 主路径零污染：生产账本 + 生产标注全为冻结模板 | 905 条账本 `{T1v1:323, S1v4:242, T2v1:340}`；320 条标注 `{T2v1:320}`；变体条目 **0 / 0** |
| **C2** | `t14/runs/**` 无变体痕迹：raw-bytes 扫 `choice.v1` **+** JSON 结构扫描（`.json` 整文件解析、`.jsonl` 逐行；解析失败记为 `unauditable`，生产目录内不可解析即 FAIL） | raw 命中 **0**、结构命中 **0**、`unauditable` **0**、生产不可解析 **0**；**结论口径：未发现符合形态的变体，不证明不存在** |
| **C3** | config 字段消失或显式废弃 | `t2_choice_template_version` **已不存在**（`absent=true`） |
| **C4** | 每条 `cache_hit=true` 的标注必须解析到**冻结模板**的缓存对象 | **71/71** 全部解析成功（T1 29 + T2 42），模板不符 **0**、对象缺失 **0** |
| **C5** | 退役运行必须**带审计痕迹隔离**，而非删除 | `t14/quarantine/`：35 文件逐个 sha256 校验 **35/35 OK**，`MANIFEST.json` 写明 *"retired … kept for audit only, never evidence"*；**生产统计产物**（`t14_main/**` 的账本/标注/acceptance/analysis）**文本层面未见引用**（文本 grep，**非结构证明**） |

**为什么加 C4/C5**：C1–C3 只证明"现在干净"，不证明"当时的命中来自哪个模板"，也不证明"退役数据还在"。
C4 直接回答 captain 关心的"71 次缓存命中是否全部来自冻结模板"；C5 保证删掉的是可见性而不是审计能力。

### 9.1 工具缺陷与修复记录（不抹除）

| 编号 | 发现者 | 问题 | 处置 |
|---|---|---|---|
| **F4** | verifier（t8 预检） | **C2 的"结构扫描"第一版逐行 `json.loads` 并在首个失败处 `break`** —— 于是 **pretty-printed `.json`**（最常见形态）被**静默跳过**。复现：pretty 的 `{"t2_choice_template_version":"T2.naturalness_pair.choice.v9"}`（后缀 v9，raw 里没有 `choice.v1`）→ J8 仍判 **PASS**；同内容 compact 单行则 FAIL。**因此修复前的"双通道"声明不成立。** | 改为 `.json` **整文件** `json.loads` 后递归；`.jsonl` 才逐行；解析失败记 `unauditable` 且**生产目录内不可解析即 FAIL**（宁可误报不漏报）。回归测试：`tests/test_j_gate.py::test_pretty_printed_variant_is_detected`（就是 verifier 的样本）。修复后 `unauditable` 从 5 条降为 **0**（说明此前被标"不可解析"的其实是 pretty JSON，正是该 bug 的症状）。 |
| **F5** | verifier（t8 预检） | C5 的"生产零引用"只扫 `t14_main/**`，若说成"全仓零引用"则表述过宽（`t14/evidence/`、`t14/test_*.py` 合法提到 quarantine） | 范围写死为**生产统计产物**（`t14_main/**` 的账本/标注/acceptance/analysis）；被排除的审计/测试路径在证据里显式标注（`quarantine.scan_scope`）；**captain 追加裁决：再降级为“文本层面未见引用”，并写明它不是结构证明**。 |
| **F6** | verifier（t8 预检，按 captain 要求构造新绕过） | 拆分字段可以绕过 C2 的字符串形态匹配。**精确复现**：`{"a":"T2.naturalness_pair.cho","b":"ice.v9"}`（pretty JSON）→ **PASS**；`{"a":"T2.naturalness_pair.","b":"choice.v9"}` 只记 prose mention，不影响判定。注意：captain 最初点名的 `{"prefix":"…choice","suffix":".v9"}` **是能拦住的**（prefix 的字符串本身就命中形态），真正的绕过必须**把 token 从中间拆开**。 | 按 captain 裁决（同类=对抗构造、不修）**记为 C2 辅助通道的已知上限**，并把 C2 结论口径改为“未发现符合形态的变体，不证明不存在”。若将来要让 C2 成为结构证据，**不能靠字符串拼接近似**，应改为 config schema 白名单 / 解析 runner 实际读取的配置键。已加特征测试 `test_known_limit_fully_split_field_is_not_detected`，一旦有人加固 C2，该测试会失败并提醒同步更新本条。 |
| **F7** | verifier（t8 预检观察指纹时序） | `--check-md` 会**重写** `J_GATE.json`（每次新 `generated_at_utc`），于是同一份内容在连续运行中产生 3 个 sha256（`4a3ddb46` → `97ff83b3` → `cf452a2f`）。**这不是内容漂移，是工具在污染下游用来核对的指纹**——比内容错误更难查，因为它让"稳定"看起来像"一直在变"。 | 自 **S1** 起 `--check-md` 与 `--no-write` **只读**（只有不带这两个开关的运行才写文件）；并新增 [`GATE_J_SNAPSHOT.json`](GATE_J_SNAPSHOT.json)：记录 6 个产物的 bytes+sha256、钉住的 `generated_at_utc`、以及**不含时间戳的内容摘要** `5d7efca5…`，供 t8 在任意时刻逐字节核对；改任何产物都必须发新的 snapshot_id（S2…）。 |
| **F8** | verifier（t8 逐字节核对）+ captain 定性 | **快照 S1 在 t20 正常复核期间被打破**：`J_GATE.json` `acb06196…` → `6f534158…`（`generated_at_utc 15:26:22Z`）。写入者是 t20 的 **plain `j_gate.py` 运行**（它在做 J8 闭合复核，完全合法）。**根因不是谁违规，而是工具设计：一个验证门每次被运行都重写自己的产物** —— 只要两个 agent 互相复核，锚点必然反复失效。 | F7 只把 `--check-md` 改成只读，不够；**`j_gate.py` 现在默认只读，写 `J_GATE.json` 必须显式 `--write`**，把“跑验证”与“产物变更”解耦。S1 状态改为 `SUPERSEDED_NO_ANCHOR`，**t20 关闭前不设新锚点**（见 `GATE_J_SNAPSHOT_POLICY.md`）。 |
| **F8b** | judge_architect（修 F8 时连带发现） | 内容摘要此前**不可复现**，两层原因：① `J_GATE.json` 里 J0 证据出现了**两份**（`protocol_precondition` 与 `items.J0_protocol_precondition`），只剔一份仍会带进上游 `verify_checked_at_utc`；② 先前记的 `5d7efca5…` 是**旧口径**（只剔顶层 `generated_at_utc`）且没写 canonical 化细节，别人算不出来。 | 口径升级为 `vett-gate-content-digest/v2`（剔 3 条路径 + 紧凑分隔符 + 键升序），并提供**两份独立实现**：`scripts/recompute_content_hash.py` 与 `scripts/verify_snapshot.py --content-digest`——两实现逐位一致（`9b0f4d40…`），`--compare` 可判“仅元数据变动”。 |

> 结论口径：**J8 的 PASS 依据是 C1 + C3 + C4 + C5（结构证据），C2 作为辅助**。F4 修复后 C2 已是真双通道，
> 但按 captain 裁决，t8 判漂移/失败时仍以结构证据为主、C2 为辅。

**残留约束**：`t14/quarantine/` 只作审计留存，t19/t21/t11/t8 任何统计**不得读取**（MANIFEST 已写死）。
J8 的关闭**不等于** T2 可发布：仍受预注册三基线、有效 n、t19 主端点与"只报序判定"约束（见 §10、§16）。

## 10. J9 分歧率 vs 30% 阈值 —— **PASS**

| 臂 | n | 分歧 | 分歧率 | < 0.30 |
|---|---:|---:|---:|---|
| 同刺激对照臂 | 24 | 2 | **0.0833** | 是 |
| R28 可比较子集 | 17 | 0 | 0.0000 | 是 |
| 合并（可比较） | 41 | 2 | 0.0488 | 是 |

两条分歧都是**本地漏正类**（云端对）：
`T1-dadba405fc74`（"…displaces… That change applies only to this location"，把作用域限定读成否证）、
`T1-1a528bdcf2ac`（"the replacement is \"Result\""，替换对象是非计分字段时不认）。
协议的排除规则（抄录 / 首次值 / 无独立校验 / 仅提编号）都不涵盖 displace/replacement 句式
→ **本地能力不足，不是协议缺陷**，无需改协议。

---

## 11. J10 退化真值护栏 —— **GUARDED**

`t1_override_truth = {"false": 320}`（t14 recon 自报）下：一律答 false ⇒ 0.8500 ≥ 0.85，
闸门被平凡策略满足。所以本门用**按刺激类别分层**的真值（48/80/192，每类 ≥30）并逐类报告。
分层真值来自刺激构造（span 角色与覆盖语义），不来自模型输出，故不循环。

---

## 12. J11 T3 数据欠定（转交 t11，不得填补）

5 条 `unsure`：(sub_05 / r28q_0176)、(sub_08 / r28q_0222)、(sub_09 / r28q_0182) 等，
三类根因：① 4.1.5 罚分与记录 0 不一致；② catch/LBW/obstructing 后的越界 allowance；
③ boundary 条目跨越 supersede completed-runs。**模型不得自行填补**（R-M1/R-M2），交 t11 作数据质量项。

---

## 13. J12 t16 `C_t14` 翻转 —— **FLAG_NOT_ADMISSIBLE**

按队长指令 (I) 执行了 `annotations/tools/compare_with_local.py`，`C_t14` 由 `BLOCKED_ON_T14`
翻为 `DETECTED`。但该脚本的检测器是 `any("t14" in str(p))` 的**路径子串判定**，
`candidate_files` 全是 t14 之前就存在的账本/矩阵文件 —— **没有做任何逐条匹配**，
所以 `DETECTED` 是空洞翻转，**不得作为证据**。真正的匹配由本门完成：R28 臂 17 题可逐条比较，
一致 17/17（0.0000 分歧）。修复（owner: annotator_alpha）：把检测器改成基于 span_id/item_id 的真实匹配。

---

## 14. J13 无区分度维度 —— **NO_DISCRIMINATION**

`abstain` 12/12 PASS、`conformance` 12/12 PASS → 两维在 R28 上无区分度，只能作满足率描述；
`overall=DEFECT` 12/12 同样是平凡策略（12 条提报全部真错）。
→ T3 的可用信号是**逐字段 verdict**（precision 0.9333 / recall 0.6087），不是 overall。

---

## 15. 队长指令 (A)–(I) 对照

| 指令 | 要求 | 结果 | 判定 |
|---|---|---|---|
| (A) | 协议单一来源，不写副本 | 未创建副本；J 门直接 import `02_design/scripts/judge_protocol.py` | PASS |
| (B) | T1 不得用退化真值；逐类报告 | 分层真值 48/80/192，逐类 0.8333 / 1.0000 / 1.0000 | PASS |
| (C) | 复核 8.33% < 30% 并写明两条分歧句式 | 0.0833 < 0.30；displace / replacement 两例已写明 | PASS |
| (D) | T2 只报序判定；模板必须是冻结版 | 序判定 0.9905；主路径 320/320 冻结版；变体已隔离、config 字段已移除 → J8 PASS | **PASS** |
| (E) | 云端 T3 n=12 仅描述性；5 条 unsure 转 t11 | DESCRIPTIVE_ONLY；5 条已列并转交 | 合规 |
| (F) | abstain/conformance 不得当质量门 | 12/12 全 PASS，已排除出质量判定 | PASS |
| (G) | kappa 只在 n≥30 算 | 全部臂 n<30 → 不估计（探索性合并仅量级） | PASS |
| (H) | 旧账本条目不计入一致率（R-R7） | 0 条旧模板条目；缓存键 806/806 复算 | PASS |
| (I) | 复用 t16 工具把 C_t14 翻为 DETECTED | 已翻，但**空洞检测**，不可采信；真实匹配由本门补 | DONE_BUT_NOT_ADMISSIBLE |

---

## 16. 复现

```powershell
cd VETT_R28_DIFFICULTY_20261112\02_design
D:\Conda\python.exe scripts\protocol_verify.py --check      # 前置：22/22 PASS, exit 0

cd ..\04_verify
D:\Conda\python.exe scripts\j_gate.py                        # 重算全部 J 项 → J_GATE.json
D:\Conda\python.exe scripts\j_gate.py --check-md             # 断言本文件的数字与 JSON 一致
```

`j_gate.py` 只读：t14 标注/账本/缓存对象、t16 盲包与 cloud_alpha、dataset_r28 金标、
t18 矩阵臂、`02_design/protocol.json`。零网络、零模型、零 GPU。

---

## 17. 诚实局限

1. **T1 的失败集中在一个构造**（J1c）：8/8 个错都在 `authority_policy`（同一句式），该子组只有 0.7500。
   "错集 = 词表不命中集"的等式**依赖词表、不稳健**（加 `controlling` 即破），已撤下，不得引用。
   T1 不能当作"本地能读懂证据支持"的证据。
2. **T1 总体 0.9750 的对照基线是 0.8500**（constant-false），余量只有 +0.1250。
3. **S1 无机械真值、C1 未运行**：两项在 R28 上都没有资格当门。
4. **kappa 全部不估计**：只有 41 条合并的探索性值（0.8951），不得进主表。
5. **云端自一致与对抗未测量**（J4/J5）：不得声称云端 ≥0.90。
6. **T3 n=12**，overall 与 abstain/conformance 均为平凡策略；云端自写记录仅 0.4514 与金标一致。
7. **J8 已关闭**（C1–C5 全满足）：但 `t14/quarantine/` 必须保持"只存不读"；任何统计若读了它，J8 的结论即失效。
8. **C2 曾有一个静默漏报缺陷（F4）**：第一版逐行解析、遇 pretty JSON 即跳过，由 verifier 复现后修复并加回归测试
   （`tests/test_j_gate.py`，14 项）。C2 至今只算**辅助证据**，PASS 以 C1/C3/C4/C5 的结构证据为准。
9. **C5 只是"文本层面未见引用"**（`t14_main/**` 文本 grep），**不是结构证明**——文本 grep 可被拆分/编码绕过。
   它只覆盖生产统计产物；`t14/evidence/**` 与 `t14/test_*.py` 属审计/测试引用，不计入。
   使用规则：**C5 不得单独作为"隔离有效性"的强证据**，必须与 C1/C3/C4 同看。
10. **已知未堵的 C2 绕过（F6，captain 裁决：记为局限、不修）**：把变体 token **从中间拆开**放在两个字段里
   （`{"a":"T2.naturalness_pair.cho","b":"ice.v9"}`）不会被命中；`{"a":"T2.naturalness_pair.","b":"choice.v9"}`
   只记 prose mention、不影响判定。**注意精确性**：captain 最初点名的 `{"prefix":"…choice","suffix":".v9"}`
   **是能拦住的**（prefix 本身命中形态），绕过必须把 token 拆在中间。
   C2 的结论口径因而是：**"未发现符合形态的变体，不证明不存在"**。C2 只是辅助通道，PASS 依据是 C3 + C1/C4/C5。
   **若未来把 C2 升为主判据，必须先把它改成结构判定**（config schema 白名单 / 解析 runner 实际读取的键），
   而不是继续做字符串形态匹配；否则主判据会带一个已知可绕过的洞。
11. **t16 `C_t14` 不可引用**：那是路径子串判定的空洞翻转。
