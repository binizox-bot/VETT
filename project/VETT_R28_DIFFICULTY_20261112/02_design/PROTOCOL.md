# VETT-R28 评测协议（冻结）

| | |
|---|---|
| **协议 ID** | `VETT-R28-JUDGE-PROTOCOL-20261112-v1` |
| **版本 / 状态** | `1.0.0` / `frozen`（2026-11-12） |
| **负责人** | judge_architect（t12） |
| **机器可读镜像** | [`protocol.json`](protocol.json)（由 `scripts/build_protocol.py` 从权威文件派生） |
| **可执行实现** | [`scripts/judge_protocol.py`](scripts/judge_protocol.py) |
| **校验器** | [`scripts/protocol_verify.py`](scripts/protocol_verify.py)（`--freeze` / `--check`） |
| **离线单测** | [`tests/test_judge_protocol.py`](tests/test_judge_protocol.py) |
| **实测依据快照** | [`evidence/routing_evidence_snapshot.json`](evidence/routing_evidence_snapshot.json) |
| **上游权威** | `03_build/local/routing_card.json`（t18）、`01_measurement/BASELINES.json`（t2）、`preregistration.json`（v1.1.0）、`02_contract/r28_contract.json`（v1.1.0） |

本协议把 t18 实测出来的**能力边界**与**工作负载分解**写成代码可执行的分层规则：谁能判什么（双标尺）、
能看什么（盲包）、怎么记账（缓存 / 重放）、什么才算数（可信度底线 / 三基线 / 有效 n）、失败时怎么留痕
（DEGRADED）。**协议不新增任何测量结论**：所有实测数字都从 `routing_card.json` /
`capability_matrix.json` / `BASELINES.json` 原样搬运并在 `protocol.json.bindings` 里逐文件绑定
sha256；改了上游而没重新冻结，`protocol_verify.py --check` 直接 FAIL（`PROTOCOL_DRIFT`）。

---

## 0. 一句话立场

> **本地 7B 是劳动力，云端模型是参考标尺，确定性 solver 是唯一正确性锚点。**
> 三者不可互相替代；任何"分数"若没有机械真值锚点、三条基线并列与有效 n 声明，一律不得出报告。

本协议**不做**的四件事（避免越权）：

1. 不改端点、不改阈值、不改停止规则 —— 那是预注册 v1.1.0 的独占权限（`R-S4`）。
2. 不评数据内容正确性 —— 那是合同 HA1–HA18 与 t8 独立验证的职责。
3. 不产生任何标注 —— 判分者不标注（`R-S1`）。
4. 不引用无法复现的口径 —— 历史聚合 `2cb1ea2c…9417` 已证伪（t1 穷举 657 种算法失败），
   零漂移一律用 `_BACKUPS\VETT_R28_PRE_CHANGE_20261112\PROTECTED_PATHS.json` 的
   `vett-tree-aggregate-v1`（R26.15 组 = `343afde4…51bd`）。

---

## 1. 权威与优先级

```
机械真值（solver / 确定性代码）
  > 预注册 v1.1.0（端点、阈值、停止规则）
    > 合同 v1.1.0（HA1–HA18、配额、prompt 预算）
      > 本协议（谁可以判、怎么判、怎么记账）
        > routing_card.json（本地能力的唯一白名单来源）
```

冲突处理：上层永远压下层。若本协议与预注册冲突，以预注册为准并在 `protocol_amendments`
（append-only）登记；若 `routing_card.json` 与本协议记录的 verdict 不同，`--check` FAIL 并要求重新冻结，
**不允许**"运行时以最新卡为准"这种静默漂移（`R-L2` + `PROTOCOL_DRIFT`）。

**绑定文件（`protocol.json.bindings`，逐文件 sha256）**

| 角色 | 文件 | sha256（前 16 位） |
|---|---|---|
| 本地能力白名单 | `03_build/local/routing_card.json` | `e76d5858fdbfc766` |
| 能力矩阵（原始测量） | `03_build/local/capability_matrix.json` | `d8156f6f8a94a3c4` |
| 三条基线 | `01_measurement/BASELINES.json` | `e40b1760fb59bbf0` |
| 预注册 v1.1.0 | `preregistration.json` | `5e0056e118a2d633` |
| 合同 v1.1.0 | `02_contract/r28_contract.json` | `7f10f9833ec0edc8` |
| R26.15 冻结数据 | `r26_15_content_dependency_candidate_v3/`（165 文件 / 93,346,177 B） | 聚合 `343afde4…51bd` |

---

## 2. 双标尺总览与工作负载分解

| 标尺 | 是谁 | 干什么 | 调用量上限 | 成本 | 校验方 |
|---|---|---|---:|---:|---|
| **本地** | Qwen2.5-7B-Instruct Q4_K_M（Ollama，RTX 3070，100% GPU） | 4 类封闭式标注（广度） | **6,400** 次 | ¥0 | 机械真值 + 重测 |
| **云端** | 本会话模型（in-session） | T3 全量裁定 + T1/T2 抽样对照（深度） | **52** 次（硬顶 80） | 软顶 ¥3 | 机械真值 + 自一致 |
| **机械真值** | 确定性 solver / 确定性代码 | 唯一正确性锚点 | — | ¥0 | 可重推 |

本地 : 云端 = **123 : 1**。这不是"本地更强"，而是"本地更便宜、更封闭、更可记账"：
凡是需要多步推导、需要给概率、需要仲裁、需要统计推断的活，一概不给本地（见 §3.2）。

| 任务 | 标尺 | 单次输入上限 | 实测 p50 | 调用预算 | 依据 |
|---|---|---:|---:|---:|---|
| T1 因子/剂量可见性 | 本地 | 3,000 tok | 0.191 s | 320 | 320 题 × 1 span |
| T2 自然度（配对） | 本地 | 2,000 tok | 0.212 s | 320 | 320 题 × 1 配对 |
| S1 span 主题 | 本地 | 1,000 tok | 0.146 s | 2,560 | 每题 ≤8 条证据 span（协议自设上限） |
| C1 证书逐句一致性 | 本地 | 2,000 tok | 0.216 s | 3,200 | 每题 ≤10 条证书句（协议自设上限） |
| T3 提报裁定 | 云端 | 无上限（是活不是包） | — | 12 | t16 全量 12 条提交 |
| T1 抽样对照 | 云端 | ≤3K 盲包 | — | 24 | 分层每机制/等级 ≥2 |
| T2 抽样对照 | 云端 | ≤6K 盲包 | — | 16 | 配对抽样 |

> 吞吐实测 207.89 次/分钟（162 次全新调用 / 46.8 s），VRAM 峰值 6,388 MiB、最低剩余 1,630 MiB。
> 因此 6,400 次本地调用是**分钟级**成本，云端 52 次是**token 级**成本 —— 分解的目的是把"贵的"限制在
> 必须由深度模型判断的地方，而不是把活平均分。

---

## 3. 本地尺（ALLOW 4 / DENY 9）

判定来源：`routing_card.json`。本协议**不重新裁定**，只把结果落成断言。

### 3.1 ALLOW（仅四项，不得扩大）

| 任务 | 一致率 | n | 门槛 | 校验方 | 模板版本 | 失败回退 |
|---|---:|---:|---:|---|---|---|
| `T1_factor_visibility` | **0.9333** | 30 | 0.85 | mechanical_truth | `T1.factor_visibility.v1` | `mechanical_lexicon_rule` |
| `T2_naturalness` | **1.0000** | 30 配对 | 0.85 | retest + mechanical_truth | `T2.naturalness_pair.v1` | `mechanical_corruption_proxy` |
| `S1_span_topic` | **1.0000** | 32 | 0.85 | mechanical_truth | `S1.span_topic.v4` | `mechanical_lexicon_rule` |
| `C1_cert_sentence_consistency` | **1.0000** | 30 | 0.85 | mechanical_truth | `C1.cert_sentence_consistency.v1` | `deterministic_solver_certificate` |

分类别细节（来自 `capability_matrix.json`）：

- T1：`NEG_PLAIN` 1.0（10）、`NEG_PROVENANCE_ADJACENT` 1.0（10）、**`POS_OVERRIDE` 0.8（10）**
  —— 即"推翻/取代"类跨度上 10 题错 2 题，是四项里唯一非满分项，t17 必须重点复核这一类。
- T2：四种机械损坏各 7–8 题全对；重测 10 对 `exact_repeat_rate = 1.0`。
- S1：四类各 8 题全对。
- C1：15 条 CONSISTENT + 15 条 INCONSISTENT 全对。

### 3.2 DENY（九项；分"实测禁止"与"角色隔离"两类）

**关键诚实点：9 条 DENY 里有 2 条（D5、D8）没有实测数字，因为它们是角色隔离而非能力测量。
协议不得给它们编造数字，`evidence_status` 写死 `POLICY_NO_MEASUREMENT`。**

| 任务 | reason_code | 依据类别 | 实测依据（原文搬运） | 回退 |
|---|---|---|---|---|
| `D1_12_field_record_derivation` | `MEASURED_BELOW_PRIOR` | 实测 | 40K 卷宗信息字段 **4.20/9 < 常数先验 4.77/9**；80K 仅升到 4.55/9 且 **17.7 s/题** | 确定性 solver / private gold |
| `D2_confidence_output` | `UNUSABLE_OUTPUT` | 实测 | 置信度均值 **60.53**（应在 0–1）；任何 confidence 一律丢弃 | 丢弃置信度 |
| `D3_kappa_arbitration` | `ROLE_ISOLATION` | 实测＋隔离 | kappa 属统计推断，归 judge/统计代码；且受 D2 排除 | judge + 确定性代码 |
| `D4_statistical_inference` | `NOT_A_MODEL_TASK` | 实测 | 先验/Brier/斜率/CI/p 值由确定性代码算（40K 4.20/9 说明其不具备推断证据） | 确定性统计代码 |
| `D5_contract_or_code_design` | `ROLE_ISOLATION` | **政策** | 无实测（设计产物归 data_designer / data_engineer / pipeline_engineer） | 设计角色 |
| `D6_input_over_8k_tokens` | `HARD_INPUT_CAP` | 实测 | 80K = **17.7 s** 且无增益（4.55 vs 4.20）；硬顶 **8192** | 拒绝（不截断） |
| `D7_draft_without_solver_check` | `UNVERIFIED_GENERATION` | 实测 | 本地 4.20/9 → 草稿必须过 solver 才能发布/计分 | solver 校验 |
| `D8_T3_adjudication` | `ROLE_ISOLATION` | **政策** | 无实测（T3 裁定归云端；本地无该能力测量） | 云端 annotator_alpha |
| `R1_readability` | `CAPABILITY_BELOW_THRESHOLD` | 实测 | **0.6667（20/30）< 0.85**；**ρ = −0.1672**；`discrimination_ok=False`；精确一致 0.2333；只输出 3 个不同分数；单调性 False（各档 0.333/0.6/1.0/0.5） | **机械 FRE 分档** |

### 3.3 可执行断言

```python
from judge_protocol import assert_local_allowed, InputCapExceeded, TaskDenied

assert_local_allowed("T1_factor_visibility", prompt=text)   # 返回 route；超限/越权抛异常
assert_local_allowed("R1_readability", prompt=text)         # → TaskDenied
assert_local_allowed("T1_factor_visibility", tokens=8193)   # → InputCapExceeded（硬顶，不截断）
```

规则：

- `R-L1` ALLOW 集合恰为四项；第五项 ALLOW 即违规。
- `R-L2` **判分时**（t17 J 门）重新读 `capability_matrix.json` 复核 `agreement ≥ 0.85` 且 `n ≥ 30`；
  文件缺失 / 任务缺失 / 低于门槛 → DENY + `DEGRADED`。
- `R-L3` DENY 九条任何情况不得执行，不得"试一下"。
- `R-L4` 任务上限 + 8192 硬顶双约束；`estimate_tokens = ceil(utf8_bytes / 3)`（保守高估），
  实际 `prompt_eval_count` 事后记账；**超限拒绝，绝不截断**。
- `R-L5` 本地不得输出置信度/概率/仲裁（`D2`/`D3`）。
- `R-L6` 本地标签是候选，不是金标；必须由 t17 + 机械真值复核。

### 3.4 ALLOW 的置信区间警告（必须随报告出现）

四项 ALLOW 都是 30–32 个样本上的**点估计**。以 T1 为例，`n=30`、`agreement=0.9333` 的 Wilson 95% CI
约为 **[0.79, 0.98]**，下界低于 0.85 门槛。因此 ALLOW 的正确读法是
**"本次测量未劣于门槛"**，而不是"已证明稳定优于门槛"。任何把 ALLOW 当"合格证"的表述记为过度解读。

---

## 4. 云端尺（参考标尺，不是真值）

| 任务 | 抽样方式 | 次数上限 | 依据 |
|---|---|---:|---|
| `T3_adjudication` | **全量**（集合内不抽样） | 12 | t16：12 条提报 |
| `T1_cross_check` | 分层（每机制/等级 ≥2） | 24 | 与本地 T1 形成跨模型对照 |
| `T2_cross_check` | 分层 | 16 | 与本地 T2 形成跨模型对照 |
| **合计** | — | **52**（硬顶 80，余量 28） | 团队计划"云端只做 80 次抽样" |

- `R-C1` T3 全量由云端裁定；本地 `D8` 永久 DENY。
- `R-C2` 抽样上限写死在代码里；超限抛 `CloudBudgetExceeded`。
- `R-C3` 云端**同样**受盲包约束（禁 gold / level / family / dose）。
- `R-C4` **T3 只有 12 条（< 30）→ 任何云端 T3 一致率只能是 `DESCRIPTIVE_ONLY`**，
  不得当门、不得写进 PASS 证据；要成为门必须 ≥30 个已判题（`R-Q1`）。
- `R-C5` 云端与机械真值冲突时以机械真值为准；云端不得"修正" solver 输出。
- `R-C6` 只允许本会话模型；任何外部 provider / SDK / 联网调用直接抛 `PaidProviderForbidden`。

云端门槛（比本地更严，因为它是参考）：一致率 **0.90**；自一致 10% 重复 **≥0.90**；对抗探针 **≥0.90**
（t17 J4/J5/J6）。云端 `kappa` 由确定性代码计算（`R-S2`），只报数并解释方向，不设通过线。

---

## 5. 机械真值：唯一正确性锚点

`R-M1` **12 字段记录、被改字段、删除测试最小性，一律以 solver 为真值；模型判定只能作为对照。**

锚点清单（全部由确定性代码产出，禁止语言模型撰写）：

1. `decision_record_flat`：12 字段，solver 在两臂上各自重推 100% 成功（合同 HA7/HA8）；
2. `solver_facts`：canonical JSON 字节，发布版与对照版逐字节相同（HA8）；
3. 证书：`minimum_evidence_spans` / `rule_path` / `authority_decision` / `revision_chain` /
   `why_not_distractor` / `derivation_check`；
4. 枚举合法性：`delivery_status` / `dismissal` / `run_ledger`。

`R-M2` 禁止用模型输出定义、补全或修改 `private_gold`；证书不得由模型撰写。
`R-M3` 所有统计量（准确率、Brier、斜率、CI、p 值、kappa）由确定性代码计算。

**禁止的替代品**：本地输出、云端输出、人工口述（未落盘未双标）、事后拟合的阈值。

---

## 6. 盲包（blind packet）

### 6.1 原则

只给该任务需要的最小字段；**不进入包 = 不进入**（不是打码，不是脱敏）。

| 任务 | payload 白名单 | 说明 |
|---|---|---|
| `T1_factor_visibility` | `passage` | 单条证据 span |
| `T2_naturalness` | `natural_text`, `degraded_text`, `clean_position` | 配对；位置由调用方随机化 |
| `S1_span_topic` | `span_text` | 单 span |
| `C1_cert_sentence_consistency` | `sentence`, `record` | **`record` 即答案 → `contains_answer=true`** |

信封键固定为：`schema_version` / `packet_id` / `item_handle` / `task` / `ruler` /
`prompt_template_version` / `token_estimate` / `contains_answer` / `payload`。

### 6.2 禁用内容

**递归禁用键**（大小写不敏感，出现在任何层级都拒绝）：
`private_gold` `private_evidence` `gold` `decision_answers` `answer(s)` `expected` `reference`
`truth` `truth_band` `label(s)` `difficulty` `difficulty_vector` `difficulty_graph` `level`
`level_label` `scenario_family` `family` `family_id` `dose` `dose_manifest` `mechanism`
`mechanism_id` `certificate(s)` `rule_path` `minimum_evidence_spans` `why_not_distractor`
`revision_chain` `authority_decision` `derivation_check` `match_id` `instance_id` `path`
`file_path` `source_path` `private_path`。

`record` 的子键必须是**且仅是** 12 个冻结字段（`batter_runs` … `total_runs`），多一个即拒绝。

**禁用内容模式**（对序列化文本扫描）：

| ID | 模式 | 拦什么 |
|---|---|---|
| `BP-MATCH-ID` | `\bmatch[_-]?\d{3,}\b` | match 编号 |
| `BP-FAMILY` | `\bL[1-5]_[A-Z0-9_]+\b` | 族名形态（如 `L3_NB_KEEPER_EXCEPTION`） |
| `BP-LEVEL` | 独立 `L1`–`L5` | 等级词 |
| `BP-DIFFICULTY-WORD` | difficulty / harder / dose / mechanism / scenario_family | 难度/剂量/机制词 |
| `BP-WINPATH` | `C:\…`、`\\host\…` | 绝对路径 |
| `BP-INNERFILE` | `private_gold.json` 等 | 内部文件名 |
| `BP-DATASETPATH` | `VETT_Cricket_v*` / `VETT_R28*` / `r26_15_*` | 目录名 |
| `BP-R28-ID` | `(?i)\br28[a-z0-9]+[-_][0-9a-z_-]{2,}\b` | **R28 id 形状规则**：`r28q_` / `r28h_` / `r28fact_` / `r28rule_` / `r28bind_` / `r28conflict_` / `r28revpolicy_` / `r28masked_` / `r28authpolicy_` / `r28shadow_` / `r28scope_` 等任意 `r28` 前缀 token |
| `BP-R28-HELDOUT-ITEM` | `\br28h_[0-9a-f]{4,}\b` | R28 held-out 题号（`r28h_0005`）—— 单独保留以便区分严重度 |
| `BP-R28-FAMILY` | `\brfam_[0-9a-f]{12}\b` | R28 族标识（`rfam_83faedd9516b`） |

> **PAMEND-003**（冻结后补入）：R28 的 id 形态出现在首冻之后，原模式表只覆盖 `match_` 与
> `L#_FAMILY` —— 盲包扫描不认识自己的 id 形态，等于泄漏检测有洞。补入后复扫 64 个既有盲包仍 0 违规。
>
> **PAMEND-004**（PAMEND-003 的不完整修正）：PAMEND-003 用的是**前缀白名单**，只列了
> `fact / rev / authpolicy / shadow / scope` 五个；t8 预检发现实测命名空间还有
> `r28rule_`（1,378）、`r28bind_`（112）、`r28conflict_`（112）、`r28revpolicy_`（96）、
> `r28masked_`（32）—— 这 **1,730 条 span 一条都拦不住**（0 命中不代表安全，是洞没被踩到）。
> 因此改为**形状规则**（`r28` 前缀 + 分隔符，不再枚举前缀），新增前缀无需再改协议。
> 误报风险实测为 0：320 份公开卷宗共 **1,046,911** 字符的文本（题面 + 文档标题 + 全部 span 文本）里
> `r28` 出现 **0** 次。配套 `reaudit_packets.py --inject-selftest` 会从数据集**自动派生**全部实测前缀
> 逐个注入，当前 **13/13 全部阻断**，64 个既有盲包仍 0 违规。

### 6.3 标识与顺序

`R-B4` 不透明 handle：`sha256('vett-blind-id/v1|salt|instance_id')[:16]`；
salt 每轮 32 字节随机、**绝不进包**；同轮固定以便复算，跨轮必须更换。
记录 canonical 化（键排序、数字串收窄为 int、无空白），消除字段顺序线索；文本**逐字不改**
（改写就是换刺激，会让 T2/T1 的判定失去可比性）。

### 6.4 审计与阻断

```python
packet = build_blind_packet(item, "T1_factor_visibility", salt)   # 越权即抛 BlindPacketViolation
violations = audit_packet(packet)                                  # 空列表 = 可投喂
```

`R-B6` 审计失败即阻断：该题不投喂 + 写 `DEGRADED(BLIND_PACKET_VIOLATION)`；
不得"先投喂再修包"。

### 6.5 残余风险（必须写进报告的诚实边界）

1. **C1 包必然含答案记录**（任务定义要求）→ 受控披露，用 `contains_answer` 隔离用途；
2. 正则扫描拦不住改写的难度词、也拦不住跨包组合推断 → 第二道门是 t17 J7 与 t8 泄漏扫描；
3. 若卷宗文本本身泄露答案，那是数据侧问题（HA11），本协议拦不住。

---

## 7. 缓存与重放

### 7.1 缓存键

```
cache_key = sha256(canonical_json{
    schema: "vett-judge-cache/v1",
    task, input_sha256,
    params: {temperature, seed, num_ctx, num_predict},   # 四项缺一即抛错
    prompt_template_version,
    model_digest                                         # 不是 model_tag
})
```

`R-R1` **v2 键必须绑 `model_digest`**（`845dbda0…b697e6`）。t18 的 v1 键用 `model_tag`，
同一个 tag 可能被重新拉取或重新量化 —— 判分调用一律用 v2；v1 键只保留用于重放 t18 的能力矩阵
（`legacy_cache_key_v1()` 复刻其口径，供迁移比对）。

`R-R6` 命中仍记账（`cache_hit=true`、成本 0）；缓存条目损坏 → 重算，不静默使用。

### 7.2 逐字落盘

`R-R2` `raw_output` 必须 **byte-exact** 落盘，不得 strip / 规范化 / 重排。账本缺
`input_sha256` / `prompt_template_version` / `temperature` / `seed` / `model_tag` /
`raw_output` / `parsed_output` / `wall_clock` 任一项，该条输出**不得进入统计**
（t18 实测：457 条全部完整、`excluded_from_stats = 0`）。

### 7.3 重放 = 重算评分，不是重生成输出

```
replay_score(entry, parse) -> {replayed_parsed, replay_digest, parsed_matches_ledger,
                               regenerated_model_output: False}
```

`R-R3` replay 路径**禁止调用模型**：只读 `raw_output` 重新解析（可选再打分）。
缺 `raw_output` → `ReplayUnavailable`，**不允许**"重新生成一次把它补上"。

`R-R7` **重放必须绑定解析器版本**。这不是理论洁癖，是实测出来的坑：`cost_ledger.jsonl` 共 **457** 条，
其中 **40 条**来自已废弃的 S1 模板 `v1`（5 条）/`v2`（35 条），那两版的 topic 枚举含 `PROVENANCE`，
`v3` 起移除该分类 —— 这 40 条里有 **25 条**（v1: 3、v2: 22）用当前解析器重算**必然失配**。
当前在用的解析器（T1v1 / T2v1 / S1v4 / C1v1 / R1v1）加仍兼容的 S1v3 覆盖 **417 条，
重放 417/417 逐值一致**（V10）。结论：旧条目只能作历史证据，不得进入判分统计；
重放报告里必须写清用的是哪一版解析器。

### 7.4 非确定性：可复现的边界

`R-R5` **禁止声称 `temperature=0` + 固定 seed 可逐位复现模型输出。** 实测证据
（`runs/repro/nondeterminism_evidence.json`）：152 个样本中 **1 个** 5 分制可读性分数跨运行
**移动 1 分**（`R1-53fd65f10741`，两次都判对），所有任务一致率与判定不变。

`R-R4` 同一 `(input, params)` 的再次生成是**新 replicate**（`repeat_of` / `repeat_index`），
不得覆盖原记录，且必须报告跨 replicate 差异。

**结论口径**：可复现的是 ①评分重算 ②缓存键 ③数据构建（MANIFEST tree aggregate）；
不可复现的是 ④模型原始输出。报告里必须区分这四者。

### 7.5 缓存命中率的最大误区

用"缓存命中率 100%"证明"结果可复现"是错误推理：命中只说明**没有重跑**，
不说明重跑会得到同样的字。真正的可复现证据是 V10（重算评分一致）与 t20 的字节级重放。

---

## 8. 可信度底线

| 项 | 值 | 说明 |
|---|---|---|
| 每任务最小样本数 | **n ≥ 30** | 本地与云端同标准；`n < 30` 只能写 `DESCRIPTIVE_ONLY` |
| 本地门槛 | **0.85** | `routing_card.gate.threshold`，一致率口径 |
| 云端门槛 | **0.90** | 参考标尺更严（t17 J4） |
| 未测量 | **DENY** | fail-safe：矩阵/卡缺失、任务未知、指标缺失 |
| 硬输入上限 | **8,192 tok** | 超限硬拒绝，**不截断**（`D6`） |
| 契约 prompt 预算 | **7,000 tok** | 超限判不合格（合同 HA15） |
| 自一致 | 云端 10% ≥0.90；本地 10% ≥0.85 | 未做自一致 → 只能报"未验证" |

`R-Q3` 是这套底线的核心：**没有测量就没有放行**。任何"应该没问题"的判断都等价于 DENY。

---

## 9. 三条基线门槛（G1 / G1r）

`R-BL1` 任何准确率报告**必须**与下列四条并列，缺一条即拒绝出报告：

| 基线 | 冻结参考值 | 出处 | R28 同集重测口径 |
|---|---:|---|---|
| 常数先验（逐字段众数） | **52.89%**（119/225） | `BASELINES.json#/baselines/constant_75_to_25` | 按族 LOFO 逐字段众数 |
| 只看题面 TF-IDF + 逻辑回归 | **54.22%**（122/225） | `…#/baselines/tfidf_logreg_question_text_75_to_25` | 按族分组 5 折 OOF |
| anchor 众数 | **73.33%**（165/225） | `…#/baselines/anchor_classifier_75_to_25` | 同 anchor 规则 LOFO |
| anchor 记录 exact | **32%**（8/25、32/100） | `…#/baselines/anchor_classifier_75_to_25/record_exact` | anchor LOFO exact |

`R-BL2` 判定：`acc(发布版, 9 信息字段) < min(冻结参考, R28 同集重测)` **对三条同时成立**才算更难；
`record exact` 同样对 `min(0.32, 同集 anchor exact)` 取小。方向必须写清：**更难 = 准确率更低**。

`R-BL3` **单基线禁令**：只越过常数先验不算成立；只报 anchor 不报题面基线同样不算。

`R-BL4` 报告禁令：Brier 禁止 "vs 0.25"（必须四项并列：含气候学 0.2016 / 0.2956 / 0.3927）；
边指标禁止只报 as-coded **0.7696**（那是 precision 以 gold 节点、recall 以恢复节点为条件的**混用**），
必须五分列 **0.299264 / 0.4886 / 0.3857 / 0.325284 / 0.092308**，0.7696 只能作 legacy 脚注。

**为什么这么狠**：t2 实测"只看题面"的 LR 已达 54.22%，而 GLM 是 55.11 —— 只差 0.89pp；
anchor 众数的 exact 32% 甚至高于 GLM 的 28%。在这种基线下，"我们更难了"若只对着常数先验说，
等于什么都没说。

**fail-safe**：任一同集基线不可测（数据不足/口径无法复现）→ **UNTESTED**，
不得声称更难，并写 `DEGRADED(BASELINE_TRIO_MISSING)`。

---

## 10. 有效 n

`R-N1` 每族至多 1 题、一题一记录（`distinct_record_ratio = 1.0`）；统计单位是**题**，不是字段。
`R-N2` 任何分析必须同时打印 `n_items` / `n_families` / `n_distinct_records`。
`R-N3` 与 R26.15 比较必须按族聚类：**n_eff ≤ 25 族（仅 16 个互异记录）** + 按族 bootstrap/置换。
`R-N4` 双渲染/配对不增加有效 n：320 对 = **320 个统计单位、640 次推理**，禁止当 640 个独立样本。
`R-N5` 禁止同族跨 split；基线拟合用按族 5 折或 leave-one-family-out。

R26.15 的教训（必须随比较出现）：100 题 = 25 族 × 4 副本，族内金标记录完全相同，**只有 16 个互异记录**；
给定族名的分类器 field/record = **100%**。所以"100 题上 66%"的真实样本量至多是 25/16，
记录级 exact 的 Wilson 95% CI 是 **[0.143, 0.476]** —— 那个 28% 完全不足以支撑任何强结论。

---

## 11. DEGRADED 事件合同（供 t13 消费）

`R-D1` 必填字段：**`task`、`reason_code`、`fallback_used`、`affected_items`**
（另加 `schema_version` / `timestamp_utc` / `status` / `scope` / `source` / `evidence` / `coverage_impact`）；
`affected_items` 必须非空。

```json
{
  "schema_version": "vett-judge-degraded-event/v1",
  "timestamp_utc": "2026-11-12T00:00:00Z",
  "task": "R1_readability",
  "status": "DEGRADED",
  "scope": "local",
  "reason_code": "CAPABILITY_BELOW_THRESHOLD",
  "reason": "agreement 0.6667 on n=30 (threshold 0.85); discrimination_ok=False rho=-0.1672",
  "fallback_used": "flesch_reading_ease_band",
  "affected_items": ["R1-53fd65f10741"],
  "source": "t17",
  "evidence": {"measured": {"agreement": 0.6667, "n": 30, "threshold": 0.85}},
  "coverage_impact": {"attempted": 320, "affected": 320, "rate": 1.0}
}
```

`R-D2` 原因码是**封闭集**（23 个）：t18 的 14 个
（`TASK_DENIED` / `CAPABILITY_BELOW_THRESHOLD` / `CAPABILITY_UNMEASURED` / `INPUT_CAP_EXCEEDED` /
`SERVICE_UNAVAILABLE` / `MODEL_MISMATCH` / `PARSE_FAILURE` / `NO_INPUT` / `MEASURED_BELOW_PRIOR` /
`UNUSABLE_OUTPUT` / `ROLE_ISOLATION` / `NOT_A_MODEL_TASK` / `HARD_INPUT_CAP` / `UNVERIFIED_GENERATION`）
＋ 本协议新增 9 个：`REPLAY_UNAVAILABLE` / `BLIND_PACKET_VIOLATION` / `BASELINE_TRIO_MISSING` /
`EFFECTIVE_N_VIOLATION` / `CLOUD_BUDGET_EXCEEDED` / `CLOUD_BLIND_VIOLATION` /
`HUMAN_GATE_REQUIRED` / `SCORE_RECOMPUTE_MISMATCH` / `PROTOCOL_DRIFT`。
未知码直接 `ValueError`，不得自创。

`R-D3` **兼容**：t18 的 `vett-degraded-event/v1` 由 `normalize_degraded()` 无损升级
（`fallback → fallback_used`；`affected_items` 取 `evidence.input_sha256`，缺则 `["*"]`）；
校验器在 t18 的**真实事件**（`runs/selftest/DEGRADED_EVENTS.jsonl`）上执行（V19）。

`R-D4` 每个 DEGRADED 必须在报告里体现为覆盖率缺口；不得静默丢弃样本，也不得伪造标注。

---

## 12. 隔离与角色禁令

| 规则 | 内容 |
|---|---|
| `R-S1` | **判分者不标注**：judge_architect 不产出任何被自己判分的标注。 |
| `R-S2` | 本地不得仲裁（`D3`）；跨模型 kappa 由确定性代码算，judge 只解释方向（≥30 配对、按族 CI、不设通过线）。 |
| `R-S3` | 实现 / 验证隔离：生成器代码不得被自己的验证脚本复用（t8 独立复跑）。 |
| `R-S4` | 端点修改、发布决定、触碰 R26.15 字节，必须在人工门内执行；无人值守路径一律抛异常。 |

角色矩阵见 `protocol.json.separation.roles`。要点：本地做广度、云端做深度、solver 定真值、
judge 定规则与仲裁但不下场标注。

---

## 13. 被取代的陈旧表述与已知局限

**被本协议取代（不得再引用）**

| 文书 | 陈旧表述 | 现口径 |
|---|---|---|
| `TEAM_ROLES_AND_AUTOMATION_PLAN.md` §4.2 | 可读性评分 ✅ ALLOW | **DENY**（0.667 < 0.85，ρ = −0.167）→ 回退机械 FRE |
| 同上 | 题量 160 题 / 32 场 | **320 题 / 64 场**（AMEND-001） |
| `AUDIT_GOAL_AND_DESIGN_20261112.md` | 63.3/60.0/51.7 证明剂量杠杆生效 | 那是整级宏准确率；真正的 10 对配对 = 5 降/4 升/1 平，p = 0.50 → **UNTESTED** |

**已知局限（写进任何引用本协议的文档）**

1. 云端 T3 只有 12 条（<30）→ 一致率只能 `DESCRIPTIVE_ONLY`。
2. 本地 ALLOW 是单次 30–32 样本的点估计，Wilson CI 下界低于门槛（§3.4）。
3. `temperature=0` 非逐位确定（1/152）→ 只能重算评分，不能重生成"复现"。
4. 本轮无人工金标（t24 只准备就绪包）→ 机械真值是唯一锚点，不等于数据侧金标已被人工确认。
5. 盲包是白名单 + 正则，不是形式化信息流证明；改写难度词与跨包推断不在覆盖内。
6. 本协议只管评测，不管数据内容正确性（HA1–HA18），也不替代预注册的统计计划。

---

## 14. 验证

```powershell
cd VETT_R28_DIFFICULTY_20261112\02_design
D:\Conda\python.exe scripts\build_protocol.py          # 从权威文件派生 protocol.json + evidence/
D:\Conda\python.exe scripts\protocol_verify.py --freeze # 冻结指纹（PROTOCOL.sha256 / protocol_freeze.json）
D:\Conda\python.exe scripts\protocol_verify.py --check  # V1–V22 逐项校验（exit 0 = 全 PASS）
D:\Conda\python.exe -m unittest discover -s tests -v    # 离线单测
```

| 检查 | 内容 | 类型 |
|---|---|---|
| V1 | protocol 任务集合 == routing_card 任务集合（13） | 权威 |
| V2 | ALLOW 恰四项且与矩阵 verdict 一致 | 权威 |
| V3 | 每个 ALLOW 的 agreement/n/threshold 与 card+matrix 逐值相等且过门 | 测量 |
| V4 | 每个 DENY 的 reason_code/deny_reason/evidence 与 card 逐值相等 | 测量 |
| V5 | DENY 依据分级：7 条 MEASURED 有数，2 条 POLICY 不造数 | 测量 |
| V6 | R1 证据完整（0.6667 / 30 / −0.1672 / discrimination_ok=false / FRE） | 测量 |
| V7 | 硬上限 8192 与 card 一致且"never truncate" | 权威 |
| V8 | 缓存键确定性与四维敏感性 | 缓存 |
| V9 | v2 键含 model_digest 且 ≠ v1 键 | 缓存 |
| V10 | 真实账本：417/417 可重算条目重放 100% 一致；40 条旧模板按 R-R7 登记 legacy（其中 25 条必然失配）；replay 不重生成 | 缓存 |
| V11 | 盲包白名单执行：干净通过、注入阻断 | 盲包 |
| V12 | C1 `contains_answer=true`；记录 canonical 化 | 盲包 |
| V13 | n<30 / 未测 / 低于阈值 → DENY | 底线 |
| V14 | 超任务上限与超 8192 硬顶均抛出、不截断 | 底线 |
| V15 | 三基线缺失（含单基线）拒绝；完整报告给出 PASS/FAIL/UNTESTED | 基线 |
| V16 | 三基线参考值与 BASELINES.json 逐值相等 | 基线 |
| V17 | 有效 n：320/320/320 通过；字段级/640 独立/跨族/R26.15 非按族 违规 | 有效 n |
| V18 | DEGRADED 必填四字段 + 封闭原因码 | 降级 |
| V19 | t18 真实事件可无损归一化 | 降级 |
| V20 | 云端 24/16/12 与总 80 上限；外部 provider 拒绝 | 云端 |
| V21 | `PROTOCOL.md` 与 `protocol.json` 的 rule id 集合完全一致 | 一致性 |
| V22 | 绑定摘要未变 + R26.15 聚合 == `343afde4…51bd` | 漂移 |

结果落在 `protocol_verify_result.json`（逐项 status/evidence），冻结指纹落在
`protocol_freeze.json` + `PROTOCOL.sha256`。**本文件不复制结果数字**，避免正文与结果漂移。

---

## 附录 A：规则索引


| 规则 | 级别 | 内容 | 强制点 |
|---|---|---|---|
| `R-L1` | MUST | 本地尺 ALLOW 集合只有 routing_card 判为 ALLOW 的四项：T1 因子可见性、T2 自然度、S1 span 主题、C1 证书逐句一致性。协议不得自行扩大/缩小；任何第 5 项 ALLOW 即为违规。 | `assert_local_allowed / local_route_at_judge_time` |
| `R-L2` | MUST | 本地任务在**判分时**（t17 J 门）必须重新读取 capability_matrix.json 复核 agreement≥0.85 且 n≥30；文件缺失、任务缺失或低于门槛一律 DENY（fail-safe），并写 DEGRADED(CAPABILITY_UNMEASURED/CAPABILITY_BELOW_THRESHOLD)。 | `local_route_at_judge_time / assert_local_allowed` |
| `R-L3` | MUST_NOT | routing_card 判为 DENY 的九条路由（D1–D8 + R1）任何情况下不得由本地模型执行，调用必须抛 TaskDenied 并写 DEGRADED；不得以'试一下'为名绕过。 | `assert_local_allowed` |
| `R-L4` | MUST | 输入严格按任务上限（T1 3000 / T2 2000 / S1 1000 / C1 2000 token，UTF-8 字节/3 保守估计）且受 8192 硬顶约束；超限拒绝（InputCapExceeded + DEGRADED），**不得截断**。 | `assert_local_allowed` |
| `R-L5` | MUST_NOT | 本地模型不得输出置信度/概率/仲裁结论。R1 实测置信度均值 60.53（应在 0–1）证明其标度不可用：本地任何 confidence 字段必须丢弃、不得进入校准、风险-覆盖或统计。 | `local_route_at_judge_time（D2_confidence_output DENY）` |
| `R-L6` | MUST_NOT | 本地标注不得当作金标。ALLOW 只表示'与该任务机械真值的逐样本一致率≥0.85'，仍需 t17 J 门与云端抽样复核；本地标签只能是候选。 | `PROTOCOL.md §3.4 / t17` |
| `R-C1` | MUST | T3 提报裁定由云端全量执行（T3 集合内不抽样），本地 D8 永久 DENY。 | `assert_cloud_allowed` |
| `R-C2` | MUST | T1/T2 云端只做分层抽样对照（T1 ≤24、T2 ≤16），云端总调用 ≤80 次；超限抛 CloudBudgetExceeded，不得'顺手多跑几条'。 | `assert_cloud_allowed` |
| `R-C3` | MUST_NOT | 云端标注员同样不得看到 private_gold / difficulty_vector / level / scenario_family / dose；适用与本地相同的字段白名单与内容扫描。 | `build_blind_packet / audit_packet` |
| `R-C4` | MUST | 云端 T3 当前只有 12 条提报（<30）。因此任何云端的 T3 一致率都只能标 DESCRIPTIVE_ONLY，不得作为通过门、不得写进门的 PASS 证据；要成为门必须 ≥30 个已判题。 | `gate_capability（n<30 → DENY）` |
| `R-C5` | MUST_NOT | 云端是参考标尺，不是真值。任何云端判定与机械真值冲突时以机械真值为准；云端不得覆盖、修改或'修正' solver 输出。 | `PROTOCOL.md §5 / t17` |
| `R-C6` | MUST_NOT | 零付费推理 API：云端调用只允许本会话模型（in-session），任何外部 provider/SDK/联网调用即违规，assert_no_paid_provider 直接抛 PaidProviderForbidden。 | `assert_no_paid_provider` |
| `R-M1` | MUST | 机械真值是唯一正确性锚点：12 字段记录、被改字段、删除测试最小性一律以 solver 为真值；模型判定只能作为对照，不得替代。 | `PROTOCOL.md §5 / t17 J1` |
| `R-M2` | MUST_NOT | 禁止用模型输出定义金标、补全金标或修改 private_gold；证书必须由确定性 solver 生成。 | `PROTOCOL.md §5.2` |
| `R-M3` | MUST | 所有统计量（准确率、Brier、斜率、CI、p 值、kappa）由确定性代码计算；模型不得参与任何统计推断（D4 DENY）。 | `local_route_at_judge_time / PROTOCOL.md §12.2` |
| `R-B1` | MUST | 投喂给任何标注员的包必须按任务字段白名单构造：只允许该任务声明的最小字段集，其余一律丢弃（不是遮蔽、不是脱敏，是不进入包）。 | `build_blind_packet` |
| `R-B2` | MUST_NOT | 包内不得出现 private_gold / gold / decision_answers / difficulty_vector / level / scenario_family / dose / mechanism / match_id / 文件路径 等键（递归检查，大小写不敏感）。 | `audit_packet` |
| `R-B3` | MUST_NOT | 包内序列化文本不得命中禁内容模式：match_ 编号、族名（L#_FAMILY 与 R28 的 rfam_<12hex>）、任何 R28 id 形态（r28 前缀 + 分隔符：r28q_/r28h_/r28fact_/r28rule_/r28bind_/r28conflict_/r28revpolicy_/r28masked_/r28authpolicy_/r28shadow_/r28scope_ 等；见 PAMEND-003/004 的形状规则）、独立等级词、难度/剂量/机制词、文件路径、数据集内部文件名。 | `audit_packet` |
| `R-B4` | MUST | 题目标识必须是不透明 handle = sha256('vett-blind-id/v1|salt|instance_id')[:16]，记录必须 canonical 化（键排序、类型归一）以消除字段顺序线索；salt 每轮随机且不进包。 | `build_blind_packet / canonical_record` |
| `R-B5` | MUST | C1 的包内含 12 字段 record（即答案），必须显式声明 contains_answer=true；此类包只能用于逐句一致性判定，禁止复用于任何'整理出记录'的统计。 | `build_blind_packet` |
| `R-B6` | MUST | 盲包审计失败即阻断：不得'先投喂再修'。审计结果必须逐条落盘（violations 非空 → 该题不投喂）。 | `build_blind_packet / audit_packet` |
| `R-R1` | MUST | 缓存键 = sha256(canonical_json{input_sha256, params(temperature/seed/num_ctx/num_predict), prompt_template_version, model_digest})；缺任一参数视为不可缓存（抛错）。t18 的 v1 键用 model_tag 而非 model_digest，判分级缓存一律用 v2（含 digest）。 | `cache_key` |
| `R-R2` | MUST | raw_output 必须逐字（byte-exact）落盘，不得 strip/规范化/重排；账本缺 raw_output/prompt_template_version/temperature/seed/model_tag/parsed_output/wall_clock 任一项的输出不得进入统计。 | `assert_replayable` |
| `R-R3` | MUST | **重放 = 重算评分，不是重生成输出**：replay 只允许读 raw_output 重新解析与打分，禁止在 replay 路径上调用模型。 | `replay_score` |
| `R-R4` | MUST | 同一 (input, params) 的再次生成属于**新 replicate**，不得覆盖原记录；必须报告跨 replicate 差异（实测 152 样本中 1 个 5 分制分数移动 1 分）。 | `PROTOCOL.md §7.4` |
| `R-R5` | MUST_NOT | 禁止声称 temperature=0 + 固定 seed 可逐位复现模型输出。可复现的只有：评分重算、缓存键、数据构建（MANIFEST tree aggregate）。 | `PROTOCOL.md §7.5` |
| `R-R6` | MUST | 缓存命中仍须记账（cache_hit=true，成本 0）；缓存校验失败 → 重算，不得静默使用损坏条目。 | `PROTOCOL.md §7.6` |
| `R-R7` | MUST | 重放必须绑定**解析器版本**：按条目自身的 prompt_template_version 用对应解析器重算。模板升级会改解析口径（实测：S1 v1/v2 的 PROVENANCE 分类在 v3/v4 被移除，25/457 条旧条目用当前解析器重算必然失配）。旧版本条目只能作历史证据，不得进入判分统计。 | `replay_score / V10` |
| `R-Q1` | MUST | 任何'该标尺能胜任该任务'的结论都要求 n≥30 个已评分样本（本地与云端同标准）；n<30 只能标 DESCRIPTIVE_ONLY。 | `gate_capability` |
| `R-Q2` | MUST | 门槛：本地 0.85（routing_card.gate.threshold）；云端作为参考标尺用更严的 0.90。 | `gate_capability` |
| `R-Q3` | MUST | 未测量即 DENY（fail-safe）：矩阵/路由卡缺失、任务未知、样本不足、指标缺失，一律 DENY 并写 DEGRADED，不得默认放行。 | `local_route_at_judge_time / gate_capability` |
| `R-Q4` | MUST | 超 8192 token 输入硬拒绝，不截断、不摘要、不分块绕过；契约 prompt 预算 7000 token 同为硬指标（超限判不合格）。 | `assert_local_allowed` |
| `R-Q5` | MUST | 自一致：云端 10% 重复 ≥0.90，本地 10% 重跑 ≥0.85；未做自一致的任务只能报'未验证'。 | `gate_capability` |
| `R-BL1` | MUST | 任何准确率报告必须与三条基线并列：常数先验 52.89%、只看题面 TF-IDF+LR 54.22%、anchor 众数 73.33%，另加 anchor 记录 exact 32%。缺任一条即拒绝出报告。 | `require_baseline_trio` |
| `R-BL2` | MUST | 判定用双阈值：acc(发布版) 必须严格小于 min(冻结参考值, R28 同集重测值)；任一侧无法测 → UNTESTED，不得声称更难。 | `require_baseline_trio` |
| `R-BL3` | MUST_NOT | 禁止单基线结论：'只赢过常数先验'不算通过；只报 anchor 不报题面基线同样不算。 | `require_baseline_trio` |
| `R-BL4` | MUST | AS-Coded 边指标 0.7696 只能作为 legacy 混合条件脚注；Brier 必须四项并列并禁止 'vs 0.25'。 | `PROTOCOL.md §9.4` |
| `R-N1` | MUST | 每族至多 1 题、一题一记录（distinct_record_ratio=1.0）；统计单位是题，不是字段。 | `check_effective_n` |
| `R-N2` | MUST | 任何分析必须同时打印 n_items、n_families、n_distinct_records 三个数。 | `check_effective_n` |
| `R-N3` | MUST | 与 R26.15 比较必须按族聚类：n_eff 上限 25 族（仅 16 个互异记录），用按族 bootstrap 或按族置换检验；禁止把 100 题当 100 个独立样本。 | `check_effective_n` |
| `R-N4` | MUST_NOT | 双渲染/配对不增加有效 n：320 对配对实验是 320 个统计单位、640 次推理，禁止把 640 当 640 个独立样本。 | `check_effective_n` |
| `R-N5` | MUST | 禁止同族跨 split；基线拟合一律按族分组 5 折或 leave-one-family-out。 | `check_effective_n` |
| `R-D1` | MUST | 降级事件必须含 task、reason_code、fallback_used、affected_items 四个字段（另加 schema_version/timestamp_utc/status/source/scope）；affected_items 非空。 | `make_degraded / validate_degraded` |
| `R-D2` | MUST | reason_code 取封闭集合；未知码直接 ValueError，不得自创。 | `make_degraded` |
| `R-D3` | MUST | t18 的 vett-degraded-event/v1 必须能被无损归一化（fallback→fallback_used，affected_items 由 input_sha256 或 '*' 补齐），供 t13 单一消费者处理。 | `normalize_degraded` |
| `R-D4` | MUST | 每个 DEGRADED 必须在报告里体现为覆盖率缺口；不得静默丢弃样本，也不得伪造标注。 | `PROTOCOL.md §11.4 / t13` |
| `R-S1` | MUST_NOT | 判分者不得标注：judge_architect 不产出任何被自己判分的标注。 | `PROTOCOL.md §12.1` |
| `R-S2` | MUST_NOT | 本地模型不得仲裁（D3 DENY）；跨模型 kappa 由确定性代码计算，judge 只解释方向。 | `local_route_at_judge_time / PROTOCOL.md §12.2` |
| `R-S3` | MUST | 实现与验证隔离：生成器代码不得被自己的验证脚本复用（t8 独立复跑）。 | `PROTOCOL.md §12.3` |
| `R-S4` | MUST | 端点修改、发布决定、触碰 R26.15 字节必须在人工门内执行；无人值守路径一律抛异常。 | `PROTOCOL.md §12.4` |
---

## 附录 B：给下游的接入清单

| 下游 | 必须调用 | 不得做 |
|---|---|---|
| t13 流水线 | `assert_local_allowed` / `assert_cloud_allowed` / `cache_key` / `normalize_degraded` | 绕过 `api.annotate` 直接调 `service.generate` |
| t14 本地标注 | `build_blind_packet` + `assert_local_allowed` | 传含 gold/level/family 的 dict 进包 |
| t16 云端标注 | `assert_cloud_allowed` + `audit_packet` + `assert_no_paid_provider` | 看 private gold；超 24/16/12 |
| t17 J 门 | `local_route_at_judge_time` / `gate_capability` / `require_baseline_trio` / `check_effective_n` / `replay_score` | 复用本地解析器判本地对错；给云端 T3 设通过线 |
| t19 主实验 | `require_baseline_trio` + `check_effective_n` + `make_degraded` | 只报常数先验；把 640 当独立样本 |
| t20 闭环 | `replay_score` + `validate_degraded` | 用"缓存命中"当"可复现"证据 |
| t8 / t9 | `protocol_verify.py --check` | 用历史聚合 `2cb1ea2c…9417` 做零漂移 |
