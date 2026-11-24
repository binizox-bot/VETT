# DISAGREEMENTS.md — 云端标注员 ALPHA vs 本地 Qwen2.5-7B（t16）

**结论先说**：本轮可做逐条对照的是 **T1（24 条同刺激）**，一致 **22/24 = 91.7%**，分歧 **2 条，分歧率 8.3% < 30% 阈值**。
两条分歧**都是本地模型错、云端对**（机械真值为准），且都落在 t18 已记录的 `POS_OVERRIDE 0.8` 那 2 条上——
因此**不是协议不清，是本地能力不足**（判读见 §3.2）。
**T2 无法逐条对照**（两臂判的是不同 span，只有任务与损坏工厂相同），只做分布对照：两臂排序判定均满分，但分数刻度用法不同（§4）。
**T3 是活不是包**：云端全量裁定 12/12，本地按 `D8` 永远 DENY，不存在可比性（§5）。
**t14 逐条本地标注在本文写作时仍未落盘**（t14 仍 running），与 t14 的逐条对照标 **BLOCKED_ON_T14**，对照脚本已就绪（§6）。

---

## 1. 覆盖与合规（自查，可复算）

| 项目 | 值 | 证据 |
|---|---|---|
| 输出 | `cloud_alpha.jsonl`，**76 行**（append-only） | `tools/assemble_cloud_alpha.py` |
| 覆盖率 | T1 **48/48**（R28 分层 24 + 同刺激对照臂 24）、T2 **16/16**、T3 **12/12** | `VERIFICATION.json` |
| schema | **PASS**（必填 13 字段、judge_id=alpha、packet_sha 逐条重算一致、rationale ≥5 词） | `tools/verify_annotation.py` → exit 0 |
| 盲包审计 | 64/64 包 `audit_packet` 零违规；包内无 `r28q_` 编号、无路径、无 gold 键 | 同上 |
| token 预算 | T1 最大 **75**（上限 3000）、T2 最大 **130**（上限 6000） | 同上 |
| 云端调用预算 | **76 / 硬顶 80**（T1 48 + T2 16 + T3 12），0 付费 API、0 联网 | `judge_config.json#budget` |
| unsure | **5 条，全在 T3**（`sub_05/08/09/10/11`），T1/T2 无 unsure | `cloud_alpha.jsonl` |
| 禁读 | 未读 `private/`（gold/certificate）、未读 t14 之外的本地中间产物、未改 packet、未从路径/编号推断 | 见 §7 边界 |

产物：`cloud_alpha.jsonl`、`packets/`（盲包 + 私密索引 + salt）、`alpha_labels/`、`crosscheck_alpha_vs_local.json`、`VERIFICATION.json`、`tools/`。

---

## 2. T1 抽取臂（R28 分层，24 条）——云端自身表现

样本按**机械可定义的真类**分层（与 t18 能力矩阵同一套词法），每类 8 条：

| 真类 | n | 云端判 supported | 与机械真值一致 |
|---|---:|---:|---:|
| `POS_SUPERSESSION`（revision 条目含 "It supersedes the entry recorded under …"） | 8 | 8 | 8/8 |
| `NEG_PROVENANCE_ADJACENT`（unsigned feed / authority conflict / parallel incident） | 8 | 0 | 8/8 |
| `NEG_PLAIN`（普通 fact 陈述） | 8 | 0 | 8/8 |
| 合计 | 24 | 8 | **24/24**（1.0） |

覆盖：机制 FACTOR 3 / D1 2 / D2 10 / D3 5 / D4 4（每机制 ≥2）；剂量等级 0:5 / 1:3 / 2:13 / 无剂量 3（每等级 ≥2）。

**诚实边界**（三条，必须写进 t17/t11）：

1. **R28 的 T1 正类只存在于 D2 机制**（16 条 revision_version span 全在 `r28q_0209–0224`）。所以"每机制 ≥2"只能靠负类满足；
   若把 T1 当机制层门，**机制覆盖天然不完整**——这是数据结构事实，不是抽样失误。
2. **负类同质**：`NEG_PLAIN` 8 条全是"appeal came before the next run-up and before Time"同一句式的不同实例
   （每份卷宗的第一个 fact span 都是它）。负类多样性低，会让 T1 一致率被高估。
3. 云端 24/24 是**构造性偏高**：正类 span 里写着 "supersedes"，负类是普通陈述。它证明的是"任务可判"，
   不是"云端比本地强 24 条"；真正的对照看 §3。

---

## 3. T1 逐条对照（同刺激，24 条）——**唯一可做逐条对照的项**

刺激来源：t18 冻结能力矩阵 `runs/matrix_20261112T103502Z_full/T1_factor_visibility.jsonl` 的 30 条 prompt
中**只抽 passage 文本**（不抽本地标签、不抽 group、不抽 match id），重新按同样的盲包规则封包 8+8+8=24 条，云端盲判。
本地标签来自**已完成的 t18 矩阵**（18:35 落盘），云端 76 条判定在 **20:45–20:52** 落盘 —— 时序上云端先判后比，无事后污染。

| 指标 | 本地 Qwen2.5-7B | 云端 ALPHA |
|---|---:|---:|
| 同刺激 24 条与机械真值一致 | **22/24 = 91.67%**（`POS 6/8`，两负类 16/16） | **24/24 = 100%** |
| 全 30 条臂（本地自报） | **28/30 = 93.33%**（= t18 的 0.9333，复现一致） | —（云端只判 24 条） |

**一致 22 / 分歧 2 / 分歧率 8.33%。**

### 3.1 分歧清单（逐条）

| # | matrix sample | 真类 | 机械真值 | 本地 | 云端 | 谁对 | 判读 |
|---|---|---|---|---|---|---|---|
| 1 | `T1-dadba405fc74` | POS_OVERRIDE | supported | **false** | **true** | **云端** | 原文：*"For the method of dismissal on the first line … N75D2C3F5D3 **displaces** NB35A06CA3D and records 'c Amelia Stone b Sarah Reed'. That change applies only to this location."* 后半句 `That change applies only to this location` 是**作用域限定**，不是"没有取代"。本地很可能把限定语读成了弱化/否定。 |
| 2 | `T1-1a528bdcf2ac` | POS_OVERRIDE | supported | **false** | **true** | **云端** | 原文：*"Reconciliation moved the third listed row's **field heading** … from N62E4E241BF to N69085278D6; **the replacement is "Result"**."* 与 #1 同一机制（reconciliation + replacement），但替换对象是**非计分字段**（field heading）。本地疑似只在"计分数值"语境下承认取代。 |

本地 30 条全臂的 2 个错**恰好都被云端 24 条覆盖**（`local_arm_full_errors` 与被覆盖集合交集 = 2），
所以"8.3% 分歧率"不是抽样漏掉了失败项，而是真实覆盖。

### 3.2 是"协议不清"还是"本地能力不足"？——判据与结论

判据（协议侧）：`judge_config.json#T1_rubric` 与 t18 `T1_CLAIM` 明确三类**不支持**——(a) 只抄录/首次临时值、
(b) 只是"另一样本无独立价值/无独立校验"、(c) 只提 docket/revision 编号。两条分歧句都**不属于**这三类：
它们都出现 displace / replacement（显式取代），属于**支持**。因此协议不需要改。

判据（本地侧）：两条错误都是**遗漏正类**（false negative），错误集中且方向一致（POS_OVERRIDE 6/8 = 0.75，
与 t18 记录的 0.8 同向），且错因可定位到"限定语"与"非计分字段"两个语义边界 → **本地能力不足，不是协议歧义**。

⚠️ 但有一个**协议侧真实缺口**（不是这两条分歧造成的，是这一轮暴露的）：t18 的 T1 机械真值在 R28 上退化为**全 False**
（t14 的 `recon.json` 自报 `t1_override_truth: {"false": 320}`，因为它取"首个 necessary-evidence span"，从不落在 revision 条目上）。
**全 False 真值下，任何一律答 false 的模型都能拿 1.0**。所以 t17 若在 R28 上做 T1 门，必须换成"按真类分层"的真值
（本轮 §2 的做法），否则该门无效。这条写进建议，不改协议文本。

---

## 4. T2 自然度（16 条云端 / 30 对本地）：只能分布对照

| 指标 | 本地（30 对） | 云端（16 对，R28 span） |
|---|---:|---:|
| 排序判定正确（clean > degraded） | **30/30** | **16/16** |
| clean 侧分数分布 | 3×6、4×17、5×7 | **5×16** |
| degraded 侧分数分布 | 1×1、2×24、3×5 | 1×3、2×12、3×1 |
| 四种损坏覆盖 | 8/8/7/7 | 4/4/4/4（duplicate / shuffle / function-word / half-splice） |

**为什么不能逐条对照**：两臂判的是不同 span（本地用其 30 条 R26.15 样本文本，云端用 R28 fact span），
只有"任务定义 + 损坏工厂（`corpus.corrupt_text`）+ 机械真值（clean 胜）"是共享的。
所以 **T2 一致/分歧数不可计算**，只能报"两臂都没有排序错误"。

**刻度差异是可报告的发现**：本地 clean 侧 20/30 给 4 分（保守，几乎不给 5），云端 16/16 给 5 分。
即两模型对"同一自然度"的**绝对刻度不同**，但**序关系一致**。含义：T2 只可当**序判定**用，
任何用 T2 绝对分数做阈值的用法（例如"平均分 ≥4"）都会把模型刻度当数据性质，属误用。

---

## 5. T3 提报裁定（云端全量 12/12）——本地不可比

`D8_T3_adjudication` 对本地是**永久 DENY（角色隔离）**，因此 T3 不存在"本地 vs 云端"分歧，只有云端裁定本身。
按 `R-C4`：**n=12 < 30 → 一致率只能 `DESCRIPTIVE_ONLY`，不得当门、不得写进 PASS 证据**。

| 维度 | PASS | DEFECT | UNSURE |
|---|---:|---:|---:|
| fields（逐字段值） | 1 | 9 | 2 |
| span（证据最小充分性） | **0** | **12** | 0 |
| edge（边界规则） | 1 | 9 | 2 |
| abstain（弃权/置信度） | 12 | 0 | 0 |
| conformance（12 字段/枚举/类型） | 12 | 0 | 0 |
| **overall** | 0 | **12** | 0 |

裁定要点（逐条理由与"正确值"见 `cloud_alpha.jsonl` 的 `labels.correct_record` / `required_fixes`）：

- **span 12/12 全不合格**：弱提交者一律只引"前 3 条 fact span"（都是上诉程序事实），**从不引**状态信号、
  接触方式、越界allowance、penalty、revision 条目。→ 若把"证据最小充分性"当评分项，这条流水线目前**必然 0 分**。
- **fields 9 DEFECT**：错误集中在五类可命名的机制——(i) 越界 19.8 未累积（sub_01/09/11）、
  (ii) 按接触分类（neither bat nor person → byes/leg-byes，不是 batter runs）未做（sub_01/06/09/11）、
  (iii) No ball / Wide 后的 dismissal 限制（21.17 / 22.9）未做（sub_07）、
  (iv) revision 策略（较大 signed revision / 18:25 锁）未做（sub_03/08/10）、
  (v) 41.5 wilful deception 的 dead-ball 优先权未做（sub_05/10）。
- **abstain / conformance 12/12 PASS**：弱提交者不弃权、confidence 0.72 合法、12 字段与枚举齐全 ——
  说明这两维**没有区分度**，不能拿来当质量门（任何合规的空壳答案都会过）。
- **5 条 unsure 的诚实原因**（不是含糊其辞，是**数据本身欠定**，应报 t8/t11）：
  1. `sub_05`：41.5 自动"five Penalty runs"与卷宗"received 0 separate penalty runs"事实冲突；dead ball 之后 4 分越界 allowance 是否仍属本次投球，卷宗未定。
  2. `sub_08`：fair catch（球死）之后又记录"boundary resulted from a fielder's throw at the wicket" + 4 分 allowance，两个事件顺序不可判。
  3. `sub_09`：LBW 出局后 6 分越界 allowance 是否计入，卷宗无规则覆盖。
  4. `sub_10`：boundary allowance 条目声明"supersedes the entry recorded under VER-76A4748D"，而该版本号属于 **completed runs** 条目 —— 跨条目取代，语义不自洽。
  5. `sub_11`：obstructing 出局后越界 allowance 是否计入，同 sub_09。

---

## 6. 与 t14 的逐条对照：**BLOCKED_ON_T14**（诚实状态，不是完成）

写作本文时（2026-11-12 20:53 左右）t14 仍 **in_progress**：`03_build/local/t14/` 只有 `recon.json / pilot.py /
t14_runner.py / t14_report.py`，**没有任何逐条标签落盘**。因此：

- 本文**不编造**与 t14 的一致/分歧数；
- `tools/compare_with_local.py` 已就绪：t14 标签一落盘（任意 `03_build/local/**/*.jsonl`，只要含逐条 task+label），
  重跑该脚本即可产出 `crosscheck_alpha_vs_local.json`，`C_t14.status` 会从 `BLOCKED_ON_T14` 变 `DETECTED`；
- **已知 t14 抽样与云端不同刺激**：t14 `recon.json` 自报 320 条 T1 取"首个 necessary-evidence span"、
  且 `t1_override_truth` 全为 false；云端 T1 用的是"按真类分层 + revision 条目"的 24 条。
  因此与 t14 的对照**只能是 item 级标签对照**（同题不同 span），**不是同刺激对照**，
  报告时必须分开写，不能把两者混成一个"一致率"。

### 6.2 t14 smoke 跑的三条观察（**是冒烟，不是主跑结论**）

`03_build/local/t14/runs/t14_smoke/` 已有 2 条 T1、1 条 T2 的冒烟标签（n 太小，不做统计），但暴露三件事，建议 t17 明确：

1. **无可对照重叠**：冒烟只判了 `r28q_0001`，而云端 R28 24 条分层样本按哈希顺序从未落在该题上 → 本轮逐条对照=0 项。
2. **T2 模板与冻结协议不一致（重要）**：t14 冒烟记录 `prompt_template_version = T2.naturalness_pair.choice.v1`、
   `annotation = {"clean": "b"}`（二选一），而冻结模板是 `T2.naturalness_pair.v1`（`score_a/score_b` 各 1–5，靠分数序判定）。
   两者**输出的统计量都不同**（选择准确率 vs 序判定准确率 + 刻度），且 `prompt_template_version` 是**缓存键与账本审计的一部分**（协议 §7.1）。
   若主跑沿用 choice 模板，则 t14 的 T2 与 t18 能力矩阵（1–5 打分）**不可比**，也不能和云端 T2 合并报一个"一致率"。
3. **T1 真值退化已现**：冒烟 T1 的 `selection_source = min_evidence_fallback`、判 `supported=false`，
   与 §3.2 的诊断一致（R28 上按"首个 necessary span"取 passage 永远取不到 revision 条目 → 真值全 False）。

---

## 7. 分歧率是否 > 30%？——结论

| 项 | 可对照性 | 分歧率 | 判读 |
|---|---|---:|---|
| T1（24 条同刺激） | ✅ 逐条 | **8.3%**（2/24） | < 30%，且两条均是本地漏正类 → **本地能力不足**，非协议不清 |
| T2 | ❌ 不同刺激 | 不可计算 | 两臂排序均满分；刻度用法不同（本地保守 4、云端 5） |
| T3 | ❌ 本地 DENY | 不适用 | 云端 `DESCRIPTIVE_ONLY`（n=12<30） |

**没有证据支持"协议不清"**；相反，本轮暴露的两个真问题都是**测量口径**问题：
① R28 上 T1 机械真值退化为全 False（t14 recon 自报）→ 该门无效；
② T2 绝对分数不可比 → 只能当序判定。
这两条比"分歧率"本身更值得 captain 处理。

---

## 8. 硬边界（重申）

1. **未读** `private/`（gold / certificate）、**未读** t14 之外的本地中间产物、**未改**任何 packet；
2. 盲判期间只读 `packets/*.jsonl`；`item_id ↔ handle` 映射在 `packets/SELECTION_INDEX.json`，判定期未使用；
3. 未从文件名 / 路径 / match_id / 字段顺序推断答案；T1/T2 的抽样用了**公开的角色/机制元数据**做分层（已在 §2 声明），
   判定本身只用包内文本；
4. 0 网络、0 付费 API、0 外部 provider；R26.15 未触碰（本任务全程只读 `dataset_r28/public` 与 t18 冻结矩阵）。
