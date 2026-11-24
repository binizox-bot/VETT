# VETT-Cricket 研究项目综合报告

**日期**：2026-11-13　**作者**：项目 agent（captain）　**团队**：`vett-r27-opt`（8 人）
**硬约束**：零付费 API · 零外网 · 不改 R26.15 任何字节 · 不读 `private/` · 不改冻结 packet
**本报告覆盖**：既有基础（220 场语料与 R20–R26.15 谱系）→ R28 数据集与结论 → 本轮 DeepTable V1 设计、执行与结果 → 现状与下一步。

> 数字纪律：本报告每个数字都标注来源文件。未经复算的数字不进结论。
---

## 0. 一页摘要

| 问题 | 状态 | 一句话结论 |
|---|---|---|
| 220 场底座 | ✅ 稳固 | 220 场 × 4 文件（解说/记分卡/证据链/元数据），98,572 个表格 cell，L2/L3 证据占 68% |
| R28 数据集 | ✅ 已交付 | 320 发布 + 40 held-out，一题一记录一族，确定性 solver 金标，证书 320/320 |
| R28 结论 | ⚠️ 零结果 | **“更难”不成立**（drop 0.557pp，CI 跨 0）；呈现侧操纵在 7B 上全部失效，因为模型根本不读证据（V0=0.125） |
| DeepTable V1（本轮） | ✅ 首轮完成 | 18 场 × 4 条件 × 3 模型 = 216 次；C0 只有 0.272–0.313，整表全对 0/216，失败面是闭合推导 |
| 下一步 | 待决 | 先写 D5 memo，再决定是否重建 C2 / 强化 C3 / 做人工双标 |

**一句话总判断**：R28 证明“把呈现做得更难”没有用；DeepTable V1 证明“把评分对象换成推导”有用——但当前 7–9B 模型在闭合推导上仍未过关，这正是下一阶段的价值所在。

## 1. 全局脉络

```
220 场记分卡语料（Self-cricket-clean_text_scorecard_v1_220_matches）
   └─ R20.220 → R22.220 → R24.220（规则 L1–L5 + 开放推理）
        └─ R26.13 / R26.14 / R26.15（answer-blind 影子、内容依赖图 +324 边，静态候选）
             └─ R28（单球裁决记录 + 四机制剂量 + 证书 + 双渲染）
                  └─ DeepTable V1（220 场表格 cell × R28 机制层 → 长卷宗整场记分卡）
```
三条主线始终没变：**事实来自确定性 solver**、**金标可机械重推**、**数据与实验全程零付费**。

## 2. 现有基础

### 2.1 语料底座：220 场
| 项 | 值 | 来源 |
|---|---:|---|
| 场数 | 220 | `Self-cricket-clean_text_scorecard_v1_220_matches/`（220 个 `match_*` 目录） |
| 每场文件 | 4：`commentary.txt`、`scorecard.md`、`evidence_chain.md`、`meta.json` | 同上 |
| 表格 cell 总数 | 98,572（均值 448.1/场） | `DEEP_T2T/corpus_audit.json` |
| cell 构成 | 击球 33,908 / 伙伴 24,563 / 投球 20,992 / FOW 9,837 / 汇总 9,260 | 同上 |
| 证据层级 L1 / L2 / L3 | 32.1% / 40.9% / 27.0% | 同上 |
| 文本均值 | 解说 6.4 KB、记分卡 5.2 KB、证据 2.5 KB | 同上 |

**读法**：语料并不浅——68% 的证据目标在 L2/L3（闭合/综合）。浅的是以往任务只问 L1 直取。

### 2.2 数据集谱系
| 版本 | 规模 | 主要内容 | 状态 |
|---|---:|---|---|
| R20 / R22 / R24 | 220 场 | 表格目标 + 证据探针；R24 增加 L1–L5 规则应用题与开放推理题 | 已发布（各自 `DATASET_CARD.md`、`MANIFEST.json`） |
| R26.15 candidate v3 | 220 场 | answer-blind 影子 + 324 条 `conditions_rule` 内容依赖边 | 静态候选，未做经验校准 |
| **R28** | 320 + 40 | 单球裁决记录 + 四机制剂量 + 证书 + 双渲染 | **已交付**（本报告 §2.3） |
| DeepTable V1 | 18 场切片 | 长卷宗 → 整场记分卡（76 cell/场） | **本轮完成**（§3） |

### 2.3 R28 数据集规格

> 来源：`VETT_R28_DIFFICULTY_20261112/03_build/dataset_r28/DATASET_CARD.md`、`build_index.json`、`MANIFEST.json`。

| 项 | 值 |
|---|---|
| 数据集版本 | `VETT-Cricket-v0.37-R28-diagnostic-pair-20261112`（design `R28-DOSE-DIAGNOSTIC-PAIR`） |
| 规模 | 发布 **320** + held-out **40** = 360 题；**一题一记录、一题一族、每题独立卷宗** |
| 题块 | `DL`（dose ladder）216 + `FC`（factor core）144 |
| 机制 | D1 alias_hops / D2 temporal_joins / D3 scope_decisions / D4 isomorphic_distractors，各 54 题（剂量 0/1/2 各 18） |
| 记录 | 12 字段 `decision_record_flat`（击球/投球得分、status、dismissal、账本 4 项等） |
| 金标 | 确定性 solver `vett_r25.solver`；**无任何语言模型参与事实、金标或证书** |
| 证书 | 320/320 覆盖；`rule_path` 只含承载算子；564 条非承载算子登记为 `presentation_only` |
| 双渲染 | 发布版（剂量按格赋值）与对照版（四剂量全 0）的 `solver_facts` + 记录 **逐字节相同**，只差呈现层 |
| 记录空间 | 规范网格可达互异记录 **4001**；实际 **320/320 互异**（R26.15 为 16/100） |
| 结构天花板 | `DEAD_REBALL` 只有 1 个可达记录；BOWLED/LBW/CAUGHT 各 2、STUMPED 4 → 合法 dismissal ≤ 11 |
| 分布（发布集） | status：LEGAL 166 / NO_BALL 100 / WIDE 53 / DEAD_REBALL 1；dismissal：RUN_OUT 86、NONE 124、HIT_BALL_TWICE 50、OBSTRUCTING_FIELD 50 等 |
| 构建确定性 | 同 seed 同配置可逐字节重建（`config_sha256 cc78be40…`，合同 v1.1.0 `7f10f983…`，预注册 v1.1.0 `5e0056e1…`） |
| 验收 | 12 项 t6 验收（`BUILD_ACCEPTANCE.json`，由 `scripts/verify_build.py` 只读磁盘独立重算） |

**必须同时说出的限制**：solver 是单球规则查表器，不是多跳推理机；金标未经人工双标；族名是中性哈希（`rfam_`+12 hex），不是泄漏轴。

### 2.4 R28 实验结论（t19 / t8 / t20 / t11）

> 来源：`R28_DECISION_REPORT.md`（289 行，sha256 `08406850…`）。

| 问题 | 判决 | 决定性读数 |
|---|---|---|
| Q1 更难了吗 | **不成立** | E1 配对 n=319：发布 59.56% vs 对照 60.12%，**drop 0.557pp**，CI **[−0.801, +1.846]**；整记录 exact **5/638 = 0.78%** |
| Q2 更有解释性吗 | 机械可验证成立；解释忠实度不成立 | 证书 320/320、solver 重推 100%；但 E4 顺序置换 stability⁰=**0.125** → `EXPLANATION_CLAIM_NOT_ESTABLISHED` |
| Q3 更能发表吗 | 作“能力基准”**不可发表** | 四条限定全 FAIL；只能作测量/零结果/验证装置论文 |

三条关键证据：
1. **E2 剂量-反应 REJECTED**：dose 0/1/2 准确率 59.375% / 62.674% / 60.938%，斜率 **+0.781pp/step**（方向相反），CI [−1.815, +3.402]，单调性 False。
2. **E3 机制归因 H3=False**：Holm 校正后无主效应；D4 名义 p=0.041 → Holm 后 **0.166**；交互模型 `NOT_ESTIMABLE_WITH_16x8`。
3. **E4 三孪生全 FAIL**：stability⁰ **0.125 (5/40)**、stability⁻ **0.500 (16/32)**、flip⁺ **0.525 (21/40)**（低于随机地板 0.875）。

**最硬的一段解释**：E1 的 0.557pp 不是“数据没变难”，而是**模型压根没在解题**——只打乱文档顺序，87.5% 的答案就变了。在模型不读证据的前提下，任何呈现侧操纵都必然无效。

**另一个最硬的负向发现**：1,546 条渲染规则引用中 **488 条（31.6%）从未承载推导**，`BAT_CREDIT` 118 次、`NB_COUNT` 100 次、`WIDE_COUNT` 53 次**从未必要**；360/360 题至少含一个非承载算子。这直接推翻“多写规则文本 = 推导更深”。

### 2.5 站得住的资产 vs 发表阻断项

**站得住（有证据）**：

| 资产 | 证据 |
|---|---|
| 金标可被确定性 solver 重推 | 320/320 = 100% |
| 记录空间打开 | 互异记录 320/320 = 1.0 |
| 族名捷径拆掉 | 值平衡 10.39%、lift −3.54pp、置换 p=0.146 |
| 证书可机械验证 | 320/320；`rule_path` 0 违规；564 条非承载登记 |
| 双渲染隔离 | facts + record 320/320 逐字节相同 |
| 闭环流水线 | 21 门 = 19 PASS / 2 DEGRADED；缓存可重放、熔断、降级均有实证（t20 10/10，19.3s） |
| 数据健康 | 互异 320/320、恒定字段 0、solver 重推 0 失败 |
| R26.15 零漂移 | 165 文件 / 93,346,177 B / aggregate `343afde4…` |

**发表阻断项（必须如实披露，不是待办）**：
1. **人工双标未执行**：金标由 solver 生成，t24 标注包 `ready_to_annotate=false`；
2. **MCC 规则文本许可未闭环**：规则摘要引用无再分发许可，发表前须法律复核；
3. **审计产物时间戳曾回填**：已在 `04_verify/PROTOCOL_VERIFY_RERUN_NOTE.json` 完整披露，规则已立“审计产物不得回填时间戳”；
4. **E5 区分度 UNTESTED**：只有 1 个可执行本地模型，区分度主张已撤回；T1 是词表匹配（余量 +0.125），不得当作能力证据。

### 2.6 本地推理与验证工具（可复用）

| 工具 | 位置 | 作用 |
|---|---|---|
| `local_inference.service` | `VETT_R28_DIFFICULTY_20261112/03_build/local/` | 冻结解码配置（`temperature=0`、`seed=20261112`、`num_ctx=8192`、`keep_alive=30m`）调用本机 ollama |
| `verify_build.py` | `03_build/scripts/` | 只读磁盘独立重算 12 项构建验收 |
| 闭环验证 | `04_verify/t20_closed_loop/` | 10/10 门、可重放、熔断演练 |
| 人工核验包 | `04_verify/human_verification_kit/` | 126 文件 / 11.8 MB，`ready_to_annotate=false`（阻断项） |
| 学术包 | `05_release/academic_package/` | `PACKAGE_STATUS.json = READY_WITH_BLOCKERS` |
| 论文骨架 | `05_release/paper/` | `NUMBERS.json` 登记全部发表数字 |
| 成本 | 全部本地 | R28 阶段实际调用：t14 905 次、t19 652 行、t21 2,835 次；**付费 ¥0、云端 0 次** |

## 3. 本轮做了什么：DeepTable V1

### 3.1 动机
R28 的判决指出了唯一出路：**难度必须来自事实与推导本身，而不是呈现**。DeepTable V1 就是把 220 场语料里 68% 的 L2/L3 cell 变成“必须推导”的评分对象——一卷宗一场，输出整场记分卡，用 closure（账目闭合）机械判错。

### 3.2 数据与任务
| 项 | 值 |
|---|---|
| 切片 | 18 场（`match_0001–0020` 中 0004/0011 因解析出的 innings ≠ 2 被 builder 跳过） |
| 卷宗 | 4 / 6 / 8 篇文档（C0/C1/C3/C2），均值 19,265 B（15.9–23.0 KB），另含 2 份他场干扰 |
| 输出 | 76 cell/场：2 局 ×（10 汇总 + 15 击球 + 12 投球）+ `result` + `pom` |
| 金标 | 由 `build_deep20.py` 的确定性 `finish()`/`amend()` 生成，closure 恒等式自洽 |
| 清单 | `data/build_manifest.json`，SHA256 `9dd7b31d…` |

### 3.3 四个条件
| 条件 | 操纵 | 文档数 | 金标变化 |
|---|---|---:|---:|
| C0 | 只有解说 + 设定 | 4 | — |
| C1 | + 2 条事件级修订备忘（M1 补 byes、M2 修最高分） | 6 | 145 cells（8/场） |
| C2 | + 在效 2026 规则 + 被取代 2025 规则（byes 计入投手）+ 冲突声明 | 8 | 0（设计使然：2025 是诱饵） |
| C3 | 删掉 M2 备忘 | 6 | 72 cells（4/场） |

### 3.4 执行
| 项 | 值 |
|---|---|
| 任务 | `bash-c0513adb23da412a`（12:41 启动，14:16 完成，exit 0） |
| 调用数 | 216 次（3 模型 × 4 条件 × 18 场） |
| 解码 | `temperature=0`、固定 seed → **确定性**，预测变化只来自提示变化 |
| 墙钟 | 约 95 分钟；gemma2:9b 最慢（约 60 s/次），qwen 约 12 s/次 |
| 成本 | **¥0**（本机 GPU，零外网） |
| 中断记录 | 旧会话 12:33:18 因 teardown 被杀，本会话 12:41 从 C3 第 5 行续跑（脚本按 `match_id` 去重） |

### 3.5 结果
**主表（12 格，全部 18 场）**

| 模型 | C0 | C1 | C2 | C3 |
|---|---:|---:|---:|---:|
| qwen2.5:7b-instruct-q4_K_M | 0.2722 | 0.2340 | 0.2458 | 0.2465 |
| llama3.1:8b | 0.3125 | 0.3067 | 0.3067 | 0.2847 |
| gemma2:9b | 0.2788 | 0.2986 | 0.2905 | 0.2920 |

整表全对 **0/216**；closure 违规率 **≈1.00**（qwen 平均每题 3.1–3.7 处违规 / 满 8）。

**按 cell 族**（cell_exact）：局汇总、击球手、投球手三族全部在 **0.19–0.38**；只有 2 个 cell 的 `pom`/`result` 达 0.44–0.50（二分类，运气成分高）。

**行为指标**：

| 指标 | 读数 | 含义 |
|---|---|---|
| copy_rate | 0.69–0.76 | 预测数值能在原文找到出处，但正确率仅 0.23–0.31 → **抄了错的数** |
| 修订跟随（C1，145 cells） | 0.145–0.193 | 低于各模型整体（0.234–0.307）→ 备忘成了上下文负担 |
| C3 证据必要性（72 cells） | 0.194–0.306 | 与 C1 相当 → 没“识别到证据缺失” |
| C2 陷阱（36 cells） | 正确 0–3%，落入 2025 陷阱 **0 次** | 闭合 cell 在地板上，走不到“哪版规则”那一步 |

### 3.6 预注册门判定
| 门 | 判据 | 读数 | 判定 |
|---|---|---|---|
| G1 | C0 cell_exact > 0.80 则太浅 | 最高 0.3125 | **PASS** |
| G2 | C1 table_exact = 0 且 closure > 0.50 | 0；1.00 | **PASS** |
| G3 | 三模型全 parse_fail | json_ok 1.000 | 未触发 |
| G4 | C2 version_sensitivity < 0.10 则重做 | 金标变化 0/1368；陷阱命中 0/36 | **判据作废**（对诱饵型操纵用“金标变化”判是本末倒置） |

G4 改写建议：改为“陷阱命中率 > 0 且 `bowling_runs` 基线正确率 > 0.30”，否则该条件在本能力档位不可用。

## 4. 两段实验合起来的判断

| | R28 | DeepTable V1 |
|---|---|---|
| 操纵 | 呈现侧（文档数、桥接深度、干扰同构、权威裁决） | 推导侧（修订重算、规则版本、证据缺失、闭合） |
| 结果 | 0.557pp，CI 跨 0 → 无效 | C0 0.272–0.313 → 有效但未过门 |
| 根因 | 模型不读证据（V0=0.125） | 模型不会闭合（closure 违规 1.00） |
| 结论 | 呈现侧加难在原理上无效 | 推导侧是唯一有价值的方向 |

**合起来的一句话**：R28 拆掉了“靠排版变难”的幻想，DeepTable V1 证明了“靠推导变难”的方向成立；现在缺的不是更多文档，而是让模型能算对账的机制与数据设计。

## 5. 局限

- **单模型/小样本**：R28 单模型（7B Q4_K_M）；DeepTable 18 场 × 18 次/格，CI 宽；均不外推到前沿模型。
- **金标非人工**：R28 与 DeepTable 的金标都是 solver/规则重算，不是独立人工标注——两处都构成发表阻断，不得写成“已标注”。
- **确定性解码的边界**：`temperature=0` 保证同 prompt 同输出，但不同 prompt 的差异不能完全归因于被操纵变量（C3 同时改了备忘集）。
- **C2 本档位无信号**：只能写“在本能力档位测不到”，不能写“版本冲突无效”。
- **copy_rate 是弱证据**：数值在文中出现 ≠ 抄对，只用于诊断。

## 6. 现状清单

| 资产 | 状态 | 位置 |
|---|---|---|
| 220 场语料 | ✅ 只读底座 | `Self-cricket-clean_text_scorecard_v1_220_matches/` |
| R20/R22/R24 数据集 | ✅ 已发布 | `VETT_Cricket_v0.22_R16_Multisource_Dilemmas/` |
| R26.15 candidate v3 | ✅ 静态候选 | 同上 |
| R28 数据集（320+40） | ✅ 已交付 | `VETT_R28_DIFFICULTY_20261112/03_build/dataset_r28/` |
| R28 实验与判决 | ✅ 完成（零结果） | `R28_DECISION_REPORT.md`、`eval_runs/t19_e1e5_20261112/` |
| R28 独立验证/闭环 | ✅ PASS_WITH_CAVEAT / 10-10 | `04_verify/` |
| R28 学术包/论文骨架 | ⚠️ READY_WITH_BLOCKERS | `05_release/academic_package/`、`05_release/paper/` |
| 人工核验包 | ⚠️ `ready_to_annotate=false` | `04_verify/human_verification_kit/` |
| DeepTable V1 数据 | ✅ 18 场 / 72 卷宗 | `DEEP_T2T/data/` |
| DeepTable V1 评测 | ✅ 216/216，exit 0 | `DEEP_T2T/runs/`、`results.json` |
| DeepTable V1 报告 | ✅ 本轮完成 | `DEEP_T2T/REPORT_V1.md`、`analysis.json` |
| D4 可靠性 | ⬜ 未做 | — |
| D5 memo / go-no-go | ⬜ 未写 | — |

## 7. 下一步（按性价比排序）

| 优先级 | 事项 | 依据 | 预计 |
|---|---|---|---|
| P0 | **D5 一页 memo**：按“G1/G2 过、G4 作废、C1/C3 未达”给出 go/no-go | 现有证据已足够 | 30 分钟 |
| P1 | **人工双标**（R28 的 t24 kit + DeepTable 抽 20 场） | 两处都构成发表阻断 | 2–3 人日 |
| P2 | **C2 重建**：让闭合 cell 先脱地板（给局部已闭合示例），再测版本陷阱 | 当前 0/36 正确率 | 54 次，约 30 分钟 |
| P3 | **C3 强化**：改为“删唯一决定性文档 → 必须弃权” | 当前只影响 4 cell | 需改 builder + 重算金标 |
| P4 | **D4 可靠性**：10 题 × 2 次，验证确定性与上下文边界 | `temperature=0` 已确定性，主要查边界 | 20 分钟 |

**不建议做**：继续加文档数/上下文长度/干扰数量——R28 已经证明这些呈现侧杠杆全部无效（E2/E3/E4）。

## 8. 附录

**文件索引**

| 用途 | 路径 |
|---|---|
| 本报告 | `VETT_COMPREHENSIVE_REPORT_20261113.md` |
| R28 判决 | `VETT_R28_DIFFICULTY_20261112/R28_DECISION_REPORT.md` |
| R28 数据集卡 | `VETT_R28_DIFFICULTY_20261112/03_build/dataset_r28/DATASET_CARD.md` |
| R28 数据集索引 | 同上 `build_index.json`（360 项，320 public + 40 held-out） |
| DeepTable 设计 | `DEEP_T2T/PLAN_V1.md` |
| DeepTable 报告 | `DEEP_T2T/REPORT_V1.md` |
| DeepTable 指标 | `DEEP_T2T/analysis.json`、`results.json` |
| DeepTable 原始输出 | `DEEP_T2T/runs/*.jsonl`（216 行） |

**复现**
```bash
PY="C:/Users/PC/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/python/python.exe"
cd D:/Download/VETT_Cricket_Complete_Delivery_R19_20261017
"$PY" DEEP_T2T/build_deep20.py --limit 20   # 构建（幂等）
"$PY" DEEP_T2T/eval_deep.py                  # 全量评测（按 match_id 去重可续跑）
```

---

*本报告所有 R28 数字引自 `R28_DECISION_REPORT.md`；所有 DeepTable 数字由脚本从 216 行原始输出重算（`analysis.json`）。任何未执行项均标 UNTESTED/未做，不含估计值。*