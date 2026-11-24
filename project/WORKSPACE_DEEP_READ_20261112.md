# 工作区全面阅读报告（2026-11-12）

> 阅读对象：`D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017`
> 阅读方式：只读。除本文件外未修改任何工件；未读取 `.secrets/` 内容；未发送 provider 请求。
> 本文件是新增文件，不在 `PACKAGE_MANIFEST.json`（2026-10-17）的载荷清单内。

---

## 0. 一句话结论

这个目录名义上是「VETT-Cricket R19 完整交付包」，实际上是一个**仍在活跃演进的研究工作区的快照**：里面同时住着一条完整的板球长文本→结构化表格/证据链数据集工程（R16→R26.18，仍在跑新的付费评测）、一份停留在 R15-C 的旧研究归档、220 场原始数据的生成源头、一个完全无关的第三方开源项目（DeepTutor），以及 2026-11-06/11-12 新写的交付报告与行动规划。

**最关键的一点：我进入时，工作区里有一个正在进行的付费模型评测**（R26.18 Sentinel5，PID 38436，11:23:06 启动；我开始阅读时完成 3/5 场，结束时 4/5 场，第 5 场在飞）。它不是我的进程，是同一台机器上另一个 agent 会话（Codex，PID 16312）发起的。任何人在这个目录里动手之前都必须先确认它是否还在跑。

---

## 1. 物理构成

### 1.1 顶层清单

| 条目 | 类型 | 文件数 | 体积 | 最后修改 | 身份 |
| --- | --- | ---: | ---: | --- | --- |
| `VETT_Cricket_v0.22_R16_Multisource_Dilemmas/` | 目录 | 14,444 | 6,129.8 MB | 2026-11-12 11:23 | **主项目**：R16–R26.18 全部源码、数据、实验、审计 |
| `DeepTutor/` | 目录 | 144,919 | 4,988.2 MB | 2026-11-09 | **第三方开源项目**（HKUDS/DeepTutor），与板球无关 |
| `VETT_COMPLETE_RESEARCH_ARCHIVE_20260903/` | 目录 | 2,704 | 878.4 MB | 2026-09-03 | **旧研究归档**，实际止于 R15-C |
| `Self-cricket-clean_text_scorecard_v1_220_matches_extracted/` | 目录 | 5,587 | 19.6 MB | 2026-05-11 | 220 场原始数据的**解压工作副本 + 生成/审计脚本** |
| `Self-cricket-clean_text_scorecard_v1_220_matches/` | 目录 | 880 | 3.1 MB | 2026-10-17 | 同一份 220 场数据的**裸副本**（每场 4 个文件） |
| `VETT_R26_18_交付报告与新对话记忆_20261106/` | 目录 | 21 | 0.1 MB | 2026-11-12 11:11 | **报告包**：现状、实验账本、交接记忆、990 行行动规划 |
| `PACKAGE_MANIFEST.json` | 文件 | — | 2.18 MB | 2026-10-17 | 8,623 条载荷清单（**已过期**，见 §7） |
| `PACKAGE_SHA256SUMS.txt` | 文件 | — | 1.55 MB | 2026-10-17 | 8,624 行校验和（同样不含 11 月新增内容） |
| `PACKAGE_README.md` | 文件 | — | 2,471 B | 2026-10-17 | 包级说明（口径停留在 R19，**已过期**） |
| `VERIFICATION_RESULTS.json` | 文件 | — | 1,295 B | 2026-10-17 | 打包时的 52/52 测试与 R16–R19 审计结论 |
| `LOCAL_ENV_AND_DISK_AUDIT_20261109.md` | 文件 | — | 6,392 B | 2026-11-09 | 本机磁盘/环境审计（与项目无关，但很实用） |
| `migrate-conda-envs-to-d.ps1` | 文件 | — | 4,926 B | 2026-11-09 | Conda 环境迁移脚本（同上） |
| `Self-cricket-clean_text_scorecard_v1_220_matches.zip` | 文件 | — | 1.35 MB | 2026-07-23 | 用户最初提供的压缩包 |

**合计：168,562 个文件，11.74 GB。**

### 1.2 文件类型分布（全工作区）

`.js` 38,066 / 446 MB、`.py` 30,558 / 219 MB、`.pyc` 29,200 / 279 MB、`.json` 19,952 / **6,196 MB**、`.ts` 12,962、`.map` 7,386、`.md` 6,436 / 33.5 MB。

体积几乎全部由 JSON 数据（数据集、审计、实验响应）和 DeepTutor 的前端构建产物构成；Markdown 文档只有 33 MB。

### 1.3 主项目内部体积结构

| 子目录 | 文件数 | MB | 说明 |
| --- | ---: | ---: | --- |
| `tmp/` | 1,746 | 944.1 | 历次被淘汰候选的中间构建（r26.13 各阶段快照等），**纯垃圾但保留作证据** |
| `dataset_r24_220/` | 885 | 416.0 | R24 全量 220 场发布 |
| `dataset_r24_220_pre_answer_position_balance_backup/` | 885 | 416.0 | 备份 |
| `dataset_r24_220_pre_surface_variation_backup/` | 885 | 416.0 | 备份 |
| `dataset_r22_220/` | 885 | 406.2 | R22 全量 220 场发布 |
| `dataset_r22_220_pre_retraction_backup/` | 885 | 402.4 | 备份 |
| `dataset_r20_220/` | 884 | 285.6 | R20 规范根全量发布 |
| `r26_*` 候选（**28 个目录**） | 145–165 / 个 | 80–89 / 个 | 每轮高难度候选的完整副本，合计 **2,176.6 MB** |
| `eval_runs/` | 899 | 18.7 | 所有外部模型运行（含 11-12 正在写的目录） |
| `analysis/` | 189 | 9.7 | 33 个审计/证据包目录 |
| `src/` | 420 | 5.5 | 144 个 `.py`，35,235 行 |
| `release_r19/` 等 10 个 `release*` | 28 / 个 | 0.5–1.9 / 个 | R16–R19 六个实例级试点发布 |
| `tests/` | 89 | 1.0 | 29 个 `.py`，5,713 行，202 个测试 |

**冗余判断**：28 个 `r26_*` 候选（2.18 GB）+ r22/r24 的 4 个备份（1.63 GB）+ `tmp/`（0.94 GB）≈ **4.4 GB，占主项目 71%**。按 `LOCAL_ENV_AND_DISK_AUDIT` 的口径，这是「为了可追溯而有意保留」，不是误操作；但如果只为交付，这部分可以压缩到 1 GB 以内。

---

## 2. 各内容体的身份与关系

```
用户最初素材：220 场板球「记分表 + 解说 + 证据链」半合成数据
        │（Self-cricket 生成系统，2026-05 左右）
        ▼
主项目 VETT-Cricket（R16 → R26.18，2026-09-23 → 2026-11-12，仍在动）
        ├── 220 场规范根（R20）→ 全量长文本/整表（R22/R24）
        └── 20 场高难度 pilot（R25 → R26.15）+ 评测协议（R26.16–R26.18）

旧归档 VETT_COMPLETE_RESEARCH_ARCHIVE_20260903（R1 → R15-C，冻结于 2026-09-03）
        └── 是主项目的前身，不是同一批工件，彼此不重叠

报告包 VETT_R26_18_..._20261106（2026-11-06 建立，2026-11-12 更新）
        └── 只描述主项目，不替代主项目

DeepTutor（HKUDS/DeepTutor 开源仓库，2026-11-09 落到这里）
        └── 与本项目无技术关系，是独立下载/克隆的第三方代码
```

### 2.1 主项目：`VETT_Cricket_v0.22_R16_Multisource_Dilemmas`

名字里的「v0.22_R16」是 2026-09 的版本号，内容已经到 R26.18（2026-11）。目录本身**不是 git 仓库**（`.git` 被打包排除），只有 `.gitignore` 和一些 `*_backup/` 目录承担版本回退职责。

### 2.2 旧归档：`VETT_COMPLETE_RESEARCH_ARCHIVE_20260903`

- 2,704 个文件 / 878 MB，含 `workspace_snapshot/`（2,592 文件 / 774 MB，原 Linux 工作区 `/workspace/scratch/...` 的整树拷贝）。
- 覆盖 v0.1→v0.21（对应 R1–R15），20 个实验目录，最新是 `v0.21_r15_synthetic_dualworld`（R15-C「四种权威拓扑」）。
- 有完整清单体系：`FULL_MANIFEST.json`（2,703 条）、`PAYLOAD_MANIFEST.json`、57 个历史 ZIP 的 CRC 审计、重复内容分组（464 组 / 841 个冗余副本）、35/35 离线 smoke 检查（PASS）。
- **重要**：它比主项目落后约 11 轮、3 个数据集世代；包名里的「R19」属于外层交付包，不属于这份归档。

### 2.3 原始数据：`Self-cricket-...`

220 个 `match_XXXX/`，每场 4 个文件：`scorecard.md`（记分表）、`commentary.txt`（约 5.5 KB 解说）、`evidence_chain.md`（证据链）、`meta.json`。

`_extracted/` 版本额外带一整套**生成与审计脚本**：`analyze_dataset.py`、`smart_expand*.py`、`style_rewriter.py`、`generate_patch_plan.py`、`final_audit.py` 等，以及 `FINAL_REPORT.md`、`FULL_AUDIT_REPORT.md`、`audit_report.json`、`manifest.csv`（220 行）、`patch_plan.json`。

`FINAL_REPORT.md` 交代了来源：这是一套「证据优先」的自动生成系统（scorecard → 解析 → 证据规划 → 叙事规划 → 模板渲染 → 审计），把原始数据的可恢复率从 45% 提到 80.3%，并把难度设计成 D0–D4 五档证据嵌入方式。**这就是主项目 R16 的输入。**

### 2.4 DeepTutor

`HKUDS/DeepTutor`，自我描述 **"An agent-native intelligent learning companion with multi-agent collaboration and RAG"**，标题「DeepTutor: Lifelong Personalized Tutoring」，香港大学数据科学实验室（HKUDS）的开源项目（Apache-2.0），有 arXiv 论文（2604.26962）、Windows/macOS 安装包、8 种语言 README、Docker Compose 配置。

- Git：`origin = https://github.com/HKUDS/DeepTutor.git`，分支 `dev`，HEAD `60fb3bdfd`「release: v1.7.2」2026-11-06，标签 `v1.7.2`，3,806 个提交（首个 2025-12-28），工作树干净。
- 技术栈：Python 3.11–3.14（本地 `.venv` 是 CPython **3.14.7**，已 editable install）+ Typer CLI + FastAPI（50 个 router，注册表驱动）+ SQLite + LlamaIndex/LightRAG/GraphRAG；前端 Next.js 16 App Router / React 19 / TS 5 / Tailwind 3，11 个 locale。
- 结构化程度相当高：`deeptutor/` 约 1,127 个 Python 文件、28.5 万行；25 个模块清单（`deeptutor/modules/manifests/*.json`）各自可独立打包；`TurnApplicationService` → `turn_engine` → `orchestrator` → capability → `ToolRegistry` 的分层。
- 测试：961 个 Python 测试文件 + 443 个前端测试文件（pytest / Vitest / Playwright），本次**未运行**。
- 体积：`web/` 3.68 GB（其中 `.next` 1.37 GB + `.next-deeptutor` 1.37 GB 是**同一份前端的两套构建缓存**，`node_modules` 924 MB，真实源码仅约 19 MB）、`.venv/` 929 MB、`.git/` 259 MB、`data/` 61 MB（运行时状态：48 MB 的 `chat_history.db`、知识库索引、日志、workspace）、`deeptutor/` 25 MB。
- **和 VETT 没有任何代码或数据关联**：`git grep -I -i -E 'VETT|cricket|scorecard'` 在 4,530 个受版本控制的文件里 **0 命中**；唯一的命中是 gitignore 掉的运行时 JSON 里、因为绝对路径包含父目录名而出现的 `D:\Download\VETT_Cricket_...\DeepTutor\...`。`data/` 下是一个中文「计算机岗专项知识」知识库（2026-11-09 建的），与板球无关。
- **但它在这台机器上被真实使用过**：`data/user/` 有 48 MB 聊天历史、用量库、workspace 和设置；`model_catalog.json` 里还留着一个非空的 SiliconFlow API key（见 §7.3）。

---

## 3. 主项目深度解析

### 3.1 研究目标

把 220 场板球比赛的记分数据转成受控的半合成长文本语料，让模型在**长上下文**中完成：

1. **整表恢复**（Track A）：从散落的 9,260 篇文档里还原 91,555 个表格单元格；
2. **证据链构造**（Track B）：为题目的答案给出最小、类型化、可核验的**有向无环证据图**；
3. **规则与状态推理**：活球/死球、No-ball/Wide 优先级、dismissal 有效性、账本归账；
4. **反事实重算**：只改一个原子事实，要求完整重算决策记录与状态；
5. **开放推理**：MCC 2026 法则闭卷题 + 自由解释题。

目标难度（**预注册，未达成**）：强模型事实字段宏准确率 ≈45%–65%，L1–L5 相邻等级平均至少下降 8 个百分点。

### 3.2 版本演进（R16 → R26.18）

| 版本 | 数据版本号 | 规模 | 核心变化 | 状态 |
| --- | --- | --- | --- | --- |
| R16 | v0.22 | 6 实例 / 48 文档 / 550 声明 | 多来源困境、证据/监管链、反事实删除 | PASS；`source_only` 基线 64.29% → 促成本文移除公开权威排序 |
| R17 | v0.23 | 6 实例 / 66 文档 | 去公开数字权威，改由修订/撤回/转载/范围求解 | PASS |
| R18 | v0.24 | 6 实例 / 90 文档 | 答案分散到 ≥5 篇文档，单文档最大占比 21.43% | PASS；仍余 21.43% 最新修订捷径 |
| R19 | v0.25 | 6 实例 / 240 文档 / 1,578 声明 | 14 目标拆到 14 篇决定性文档，1–14 层错误修订链 | PASS；单文档占比降到 7.14%，最新修订捷径 0% |
| **R20** | v0.27 | **220 场 / 9,260 文档 / 274,250 声明 / 471.5 万词** | 规范根修复、冲突掩码、整表目标 | **220/220 PASS** |
| R21 | v0.28 | 20 场 pilot | 语义定位 + 证据链联合评测；统一模型运行框架 | 20/20 PASS |
| **R22** | v0.29 | **220 场 / 5,500 探针 / 54,516 次删除检查** | 五级难度 × 五任务族矩阵 | PASS（静态） |
| R23 / R23.1 | v0.30 / v0.31 | 20 场 | MCC 法则闭卷题 + 开放推理；规则线索嵌入长文本 | PASS |
| R24 | v0.32 | 220 场 / +1,100 规则题 / +1,100 开放题 | 60 场景、可逆文本替换 | **静态 PASS，实测 FAIL → 冻结为失败基线** |
| R25.2 | v0.35 | 20 场 / 100 决策题 / 1,308 span / 656 反事实 | 状态求解 + countermodel | 可交付，未晋升 |
| R26.3–R26.4 | v0.36.3/4 | 20 场 / 100 题 / **2,492 条类型边** | 最小有向无环证据图 | 静态 PASS；外部 2/5 场 |
| R26.5–R26.7 | v0.36.5–7 | 同上 | 正/排除证据分离；来源文体反捷径 | R26.6 追溯 FAIL |
| R26.13 | v0.36.13 | 20 场 / 326,308 个 span ID | 角色中立 ID、证明证书 | **追溯 FAIL**（题面 1NN 91%） |
| R26.14 | v0.36.14 | 20 场 / 100 题 | 答案盲化：反事实指令移入决定性事实 span | 静态 PASS，220 场流式预检 PASS |
| **R26.15** | **v0.36.15** | **20 场 / 100 题 / 25 情景族 / 324 条内容依赖边** | 反事实事实 → 受影响规则的 `conditions_rule` 边 | **当前数据候选**，静态+因果 PASS |
| R26.16 | 同 R26.15 | 评测层 | 未知证据引用降级为语义假阳性 | 本地 PASS；Edge7 外测 4/5 场 |
| R26.17 | 同 R26.15 | 评测层 | `exact_target_map_v3` 精确题目键 | 本地 PASS；单场烟测 PASS |
| **R26.18** | 同 R26.15 | 评测层 | `canonical_set_v2` 集合语义 + 服从性双轨 | **当前协议**，本地 PASS |

关键原则：**R26.16–R26.18 只改评测层，不动 R26.15 的任何一个数据字节**（165 个文件、93,346,177 字节、聚合 SHA-256 `2cb1ea2c…`）。

### 3.3 R20：220 场规范根（一切的地基）

- 220 个 match ID = **217 个独立根 + 3 个逐字节重复的一致性控制**（科学样本量必须写 217）。
- 98,447 个源单元格；**91,555 个可计分**；**6,892 个冲突相关单元格保留但不计分**（不猜、不改写，只打掩码）。
- 113 场至少有一个被掩码的单元格；单场最少保留 198 个可计分单元格。
- 启发式基线：首次提及 36.48%、末次提及 36.59%、多数值 43.74%、最短修订链 0%。
- 种子 20027；单场 10,040–33,731 词。

### 3.4 数据契约（最重要的工程约定）

每个发布目录固定三层：

```
public/<match_id>/public_instance.json      # 唯一允许给模型的输入
private/<match_id>/private_gold.json        # 答案 + 来源坐标
private/<match_id>/private_evidence.json    # 声明、span 哈希、图边、决定性支持
audit/<match_id>.audit.json                 # 实例级机器审计
MANIFEST.json / RELEASE_SUMMARY.json / RELEASE_REPORT.md / DATASET_CARD.md
```

以 R26.15 的 `match_0021` 为例（我实际解析过）：

- `public_instance.json`（534 KB）：23 篇文档、1,048 个公开 span、11 张表布局、266 个表格目标、25 个 R22 探针、5 道决策题、输出契约。
- 每道决策题要求输出 7 个字段：`decision_record` / `state` / `evidence_spans` / `counterfactual_record` / `counterfactual_state` / `explanation` / `confidence`。
- `private_gold.json`（381 KB）：`decision_answers`（5 条，每条含 factual/counterfactual 记录、12 字段扁平化、难度向量、最小证据、反事实 blast radius、countermodel）。
- `private_evidence.json`（846 KB）：759 条 table claims、165 条 probe claims、70 条 R25 声明、81 个文本补丁、5 条 R26 最小证据边组、5 条内容依赖边组。
- 12 个计分字段：`batter_runs`、`bowler_runs`、`counts_in_over`、`delivery_status`、`dismissal`、`total_runs` + 6 个 `ledger.*` 账本字段。

**难度向量**（私有）是判断「难度是否真的变难」的依据，包含 `authority_decisions`、`binding_collision_count`、`counterfactual_blast_radius`、`derivation_depth`、`operator_interaction_count`、`evidence_span_count`、`temporal_depth` 等 20 余项，不进入公开侧。

### 3.5 五级难度设计（R22 起冻结）

| 等级 | 名称 | 候选值 | 决定性 span | 决定性边 | 链深 | 强模型 FAM 目标 | 联合 exact 目标 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| L1 | 锚定修订 | 2 | 2–3 | 1–2 | 1 | 85–90% | 68–82% |
| L2 | 范围化调和 | 3 | 3–5 | 2–4 | 2 | 74–80% | 48–65% |
| L3 | 来源继承 | 3–5 | 4–7 | 3–6 | 3 | 62–68% | 30–48% |
| L4 | 跨记录推导 | 4–7 | 6–10 | 5–9 | 3–4 | 48–56% | 15–32% |
| L5 | 全局证据综合 | 5–9 | 9–14 | 8–13 | 4–6 | 30–40% | 5–18% |

五个**任务族**：`cell_value`、`entity_scope`、`event_state`、`derived_indicator`、`consistency_provenance`。每场 25 个探针 = 5 等级 × 5 任务族，构成完整 5×5 矩阵。

### 3.6 评测协议 R26.16–R26.18（当前最精细的部分）

R26.18 把一次模型输出拆成**四条互不替代的轨道**：

1. **provider 可用性**：503/402/429/timeout 记为执行失败，不是语义零分；
2. **硬协议合法性**：非法 JSON、截断、缺题/多题、字段类型错、畸形 ID、外来节点、原始数组超限 → 整批硬失败；
3. **输出服从性**：完全相同的 span / 边三元组 → 该题标记 `nonconformant`，单独报服从率；
4. **集合语义能力**：按集合去重后正常评分，重复副本不获得额外信用。

设计动机很具体：R26.17 已用对象键消除了「同一题目 ID 重复五次」，但 provider 仍然不执行 JSON Schema 的 `uniqueItems=true` —— `match_0021` 完整返回 5/5 题却重复了 7 组、31 个冗余边、最大重复 17 次。整批丢弃会损失真实能力测量，静默去重会掩盖不服从，所以采用双轨。

**指标层级**（`design/r26_9_metric_contract.json`，2026-10-19 冻结）：

- 主指标：`decision_field_level_macro_accuracy`（每题 12 字段 → 等级内平均 → L1–L5 等权平均）；
- 伴随指标：整记录 exact、信息字段、值平衡信息字段、状态、反事实、`paired factual-counterfactual exact`、正 span F1、排除 span F1、typed-edge F1、**内容依赖 edge F1**、证据链 exact、事实+完整链 exact、Brier、未知引用率；
- 统计：按比赛分块 bootstrap（10,000 次、种子 26091、95% 百分位区间）。

### 3.7 代码结构

```
src/
  vett_r16 … vett_r26     各版本生成器 / 审计器 / 评分器（14 个包）
  vett_eval/              统一模型运行框架：runner(132 KB) / analysis(40 KB) /
                          cohort / panel / metric_contract / recover / cli
tests/                    29 个测试文件，202 个测试
design/                   31 份冻结 JSON 合同（指标、请求、权限、合同版本）
docs/                     71 份规格与审计报告 + ADR
eval_configs/             79 个运行配置（Oracle / 各模型 / 授权与阻断成对）
analysis/                 33 个证据包（每个阶段一个目录 + JSON + MD）
eval_runs/                每次外部执行的原始响应、checkpoint、predictions
```

运行入口：

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -p 'test_*.py' -v
python -m vett_eval.cli run --config eval_configs/<config>.json
python -m vett_eval.cli analyze-r26 --release <release_dir> --run <run_dir>
```

`runner.py` 是整个系统的核心：schema 生成、请求哈希、防重复请求、断点续跑、token 安全校验、成本估算、响应规范化、未知证据归因。它把「协议」写成了可执行代码，而不是文档约定。

### 3.8 反捷径体系（这个项目真正的技术含量）

历史上被实际击穿过、并逐个修掉的捷径：

| 捷径 | 版本 | 表现 | 修法 |
| --- | --- | --- | --- |
| 公开数字权威排序 | R16 | `source_only` 64.29% | R17 移除 |
| 最新修订 / 固定修订序位 | R18→R19 | 21.43% → 7.14% / 0% | 14 目标拆到 14 篇文档 |
| 恒定反事实 | R24 | 100% | R25 引入 countermodel |
| 语义化选项标签 | R24 | 100% | R25 改结构化记录 |
| 证据角色词（decisive/misleading） | R24 | F1 100% | R26.5 正/排除证据分离 + 中立措辞 |
| 来源文体（签名/修订号/锁定时间） | R26.6 | 宏 F1 77.7% | R26.7 确定性平衡别名 |
| 公开 span ID 形态 | R26.12 | 留一比赛 F1 100% | R26.13 统一 `s_<24hex>` |
| 题面 1NN（不读文档） | R26.13 | 91% 字段 / 72% 整记录 | R26.14 答案盲化 → 54.08% / 6% |
| 固定角色模板重建整图 | R26.14 | 100% | R26.15 内容依赖边 → 0% |
| 总体 edge F1 掩盖内容边失败 | R26.15 | 删光内容边仍 93.896% | 新增内容依赖专项指标 |

当前仍被登记为风险、但未修复的：内容依赖机会量存在等级不平衡（L1 3.8 / L5 1.6 条/题），所以 `content exact-by-level` 不能当难度曲线读。

### 3.9 已知失败与边界（必须原样保留的结论）

- **不能**声明强模型事实宏准确率已稳定 ≤65%；
- **不能**声明 L1–L5 相邻等级都稳定差 8 个百分点；
- **不能**把四场子集、单场烟测、后验回放合并成「正式 Sentinel5」；
- **不能**说 220 场 R26.15 已最终物化、人工双标或发布；
- 只有一个模型家族（GLM-5.3-Flash）有实测；
- 机器门 PASS ≠ 人工自然度审计，也不证明通用模型不可解。

---

## 4. 外部实验账本（真实花过钱的）

| 批次 | 覆盖 | 费用 | 结果 |
| --- | --- | ---: | --- |
| R25.2 校准 | 20 场 | ¥0.494948 | question-only 0%、C2-Table 32%、C2-Isolated 60%；等级 80/40/20/20/0，L3–L4 平 |
| R26.4 哨兵 | 2/5 场 | — | 事实 50%、span F1 65.10%、edge F1 26.75%、链 exact 0% |
| R26.16 Edge7 | 5 场 / 6 请求 / 5 计费 | ¥0.635277 | 4 场可评分：整记录 20%、12 字段 71.67%、值平衡 38.83%、span 54.23%、内容边 17.39%、完整链 0%；L2→L3 倒置 10.42 pt |
| R26.17 烟测 | `match_0220` | ¥0.157785 | 5/5 题、无截断、无验证错误 |
| R26.17 五场尝试 | `match_0021` | ¥0.124990 | 5/5 题但 7 组重复边 → 协议失败早停 |
| **R26.18 Sentinel5** | **5 场 / 25 题** | **预算 ¥1.4（估算 ¥1.0074）** | **2026-11-12 11:23 启动，阅读时进行中** |

---

## 5. 实时状态：11-12 那一场正在跑的评测

我从三个独立来源交叉验证了这件事：

1. `analysis/r26_18_sentinel5_execution_20261112/AUTHORIZATION.json`：`AUTH-R26.18-S5-20261112-01`，用户 11:19:17 授权，一次性、上限 ¥1.4、零重试、首个硬失败即停；
2. `PRE_EXECUTION_GATE.json`：15 项门全 PASS（候选无漂移、202 测试、零请求预检、配置 diff 白名单、输出目录全新、凭据存在但未读取）；
3. `eval_runs/r26_18_s5_20261112/`：`checkpoints/` 下已有 `match_0021`（11:25:24）、`match_0066`（11:27:38）、`match_0067`（11:30:12）、`match_0162`（11:33:46）四个完成批次，`match_0220` 是 `batch_000.inflight.json`；进程 `python -m vett_eval.cli run --config eval_configs\r26_18_glm53_canonical_set_sentinel5_authorized_20261112.json`（PID 38436）存活。

按每场约 2.5 分钟推算，5 场应在 11:36 前后结束。我最后一次观察是 **11:35:02，4/5 完成、第 5 场在飞**；`predictions.jsonl` 此时仍是 11:27 的旧内容（每场落盘有延迟）。

**这是另一个 agent 会话（Codex，PID 16312）的工作，不是我的**；我全程没有触碰它，也没有读取任何凭据内容。这场实验的结果如何，取决于它结束时写进 `RAW` / `predictions.jsonl` 的 `batch status` 和 `conformance_status`——如果五场全部 `OK`，才是项目史上第一个**完整可评分**的 Sentinel5。

---

## 6. 报告包与行动规划（`VETT_R26_18_..._20261106`）

21 个文件、10 个分类目录，是整个项目**最值得先读**的部分：

| 目录 | 内容 | 价值 |
| --- | --- | --- |
| `00_总览/` | README、CURRENT_STATUS、DELIVERY_MANIFEST | 5 分钟建立全局 |
| `01_数据集演进/` | R20→R26.15 的来龙去脉 | 理解为什么这么设计 |
| `02_评测协议/` | R26.16–R26.18 为什么连续重构 | 理解协议不是拍脑袋 |
| `03_实验与指标/` | 实验账本、成本账本、指标解释 | 所有实测数字的唯一出处 |
| `04_代码与复现/` | 代码地图、复现命令、工件索引 | 上手 |
| `05_风险与决策/` | 局限、硬门、下一步 | 决策者必读 |
| `06_新对话交接/` | **HANDOFF_MEMORY.md（必须先读）**、启动提示、禁忘清单 | 新会话恢复状态 |
| `07_证据复盘/` | 九段可核验证据链 + 升维迁移附录 | 答辩/评审用 |
| `08_原始报告索引/` | 原项目权威工件位置 | 导航 |
| `09_后续行动规划/` | **990 行完整行动与升级计划书** | 阶段 0–8、M0–M6、异常矩阵、授权模板 |

`HANDOFF_MEMORY.md` 的核心信息：用户目标是「220 场、长上下文、事实有据但隐蔽、无简单规律」；优先级是 ①足够难且能区分强模型 ②金标与证据链可靠 ③可复现、可解释、费用受控；**在没有新授权时只允许阅读、审计、跑本地测试和零请求预检**。

行动规划的分阶段主线：

```
阶段0 冻结基线复验（已完成）
  → 阶段1 完整 R26.18 Sentinel5（需费用授权）← 正在发生
  → 阶段2 冻结分析与假设登记
  → 阶段3 第一强模型家族 Pilot20（20 场/100 题/5×5 锚点）
  → 阶段4 shadow 局部优化（仅满足权限时）
  → 阶段5 第二强模型家族复验
  → 阶段6 220 场内部物化 + 全量机器门
  → 阶段7 人工双标、专家仲裁、来源许可
  → 阶段8 发布候选与论文
```

---

## 7. 交付包一致性问题（这是本次阅读最需要报告的发现）

这个包**不是一个自洽的交付物**，它是三层不同时间的东西叠在一起：

### 7.1 清单与内容不匹配

- `PACKAGE_MANIFEST.json` 与 `PACKAGE_SHA256SUMS.txt` 都是 **2026-10-17** 生成的，只覆盖 8,623 个文件；
- `DeepTutor/`（2026-11-09）和 `VETT_R26_18_...`（2026-11-06/11-12）**完全不在清单里**（我用 `Select-String 'VETT_R26_18'` 在 8,624 行校验和中查到 0 条）；
- 11-12 新产生的 `analysis/r26_18_*`、`eval_runs/r26_18_s5_20261112`、授权配置同样不在清单里。

**后果**：谁按 `PACKAGE_SHA256SUMS.txt` 验证整个包，今天一定会失败；谁按清单统计体积，会漏掉 5 GB。

### 7.2 文字口径过期

| 文件 | 写的 | 实际 |
| --- | --- | --- |
| `PACKAGE_README.md` | 「R19（2026-10-17）」「52/52 测试通过」「R16–R19 审计 PASS」 | 项目已到 R26.18，202/202 测试，R26 系列审计 |
| `PACKAGE_README.md` | 「全量研究归档…含历史快照」 | 归档止于 R15-C，早于包名两代 |
| `docs/DATA_AND_AUDIT_GUIDE.md` | 只讲 R16–R19、6 个试点实例 | R20 起是 220 场；指南未更新 |
| `r26_15_.../DATASET_CARD.md` | 标题「R26.14 answer-blind shadow」 | 实际是 R26.15 候选 |
| `r26_15_.../RELEASE_REPORT.md` | 标题同样停留在 R26.14 | 同上 |
| `r26_15_.../RELEASE_SUMMARY.json` | `base_release` / `parent_release` 写死绝对路径 `D:\Download\...` | 包一旦移动即失效 |

规划书自己把这几条列为「P3 文档与可移植性缺陷」和「发布阻断项」，说明作者知道，只是没修。

### 7.3 安全

工作区里至少有 **两处真实凭据**：

1. `VETT_Cricket_.../.secrets/siliconflow.env`，72 字节，一个 SiliconFlow API key；
2. `DeepTutor/data/user/settings/model_catalog.json` 里 `connections[0].api_key`，51 字符、非占位符。

两者都**不在** `PACKAGE_MANIFEST.json` / `PACKAGE_SHA256SUMS.txt` 里（我查过：`.secrets` 0 条、`model_catalog` 0 条），说明作者有意把密钥排除在清单外——但**文件本身还躺在目录里**。加上 DeepTutor 的 48 MB 个人聊天记录、用量库和 workspace，这个目录不能原样对外分发。

我在整个阅读过程中**没有读取、打印、复制或哈希任何密钥内容**；本报告和任何输出都不包含它们。

**建议**：对外分享前删除 `.secrets/` 与 `DeepTutor/data/user/`，并轮换这两个 key。

### 7.4 并发写入

工作区当前**不是静态的**：`analysis/`、`eval_configs/`、`eval_runs/` 的修改时间都是 11:18–11:23，正是另一个会话在跑 R26.18。任何「校验全包 SHA-256」的动作现在都会得到不一致的结果。

---

## 8. 存储与冗余

| 类别 | 体积 | 建议 |
| --- | ---: | --- |
| `DeepTutor` 的 `.next` 缓存 ×2（各 1.37 GB）、`node_modules` 0.92 GB、`.venv` 0.93 GB | ~4.6 GB | 可重建；若只为「留一份参考」，保留源码 + lockfile 即可 |
| `tmp/`（1,746 文件 / 944 MB） | 0.94 GB | 被淘汰候选的中间构建，证据价值低 |
| 数据集多版本备份（r22/r24 各 2–3 份） | ~1.6 GB | 若确定不再回滚，可只留最新 + 审计报告 |
| 28 个 `r26_*` 候选副本 | 2.18 GB | 只有 `r26_15_content_dependency_candidate_v3` 是当前候选，其余是历史/失败快照 |
| `analysis/`（33 个证据包） | 仅 9.7 MB | 是审计证据，体积可忽略，不要删 |

按 `LOCAL_ENV_AND_DISK_AUDIT_20261109.md` 的口径，整机层面还有约 20.9 GB 可回收缓存和 85.47 GB 的旧 Docker 盘，但那些不在本工作区内。

---

## 9. 风险清单

| 级别 | 风险 | 证据 | 建议 |
| --- | --- | --- | --- |
| **P0** | 交付包含 API 密钥（两处） | `VETT_Cricket_.../.secrets/siliconflow.env`（72 B）、`DeepTutor/data/user/settings/model_catalog.json`（51 字符 key） | 对外分享前删除并轮换 |
| **P0** | 第三方项目携带个人数据 | `DeepTutor/data/user/chat_history.db` 48 MB、`usage.sqlite3`、workspaces、日志 | 分发前清空 `data/user/` |
| **P0** | 包完整性清单过期 | 8,623 vs 实际 168,562 文件 | 重新生成 manifest，或明确标注「本包为工作快照，不作完整性验证」 |
| **P1** | 并发会话在同一工作区写文件 | PID 16312 / 38436 | 操作前确认没有别的 agent 在跑；不要在校验哈希时假设静态 |
| **P1** | 当前候选与发布文档标题不一致 | R26.14 vs R26.15 | 修文档标题，不动数据字节 |
| **P1** | 只有单模型家族实测 | 全部外测都是 GLM-5.3-Flash | 论文结论必须限定 |
| **P2** | 220 场 R26.15 未物化 | 只有 20 场 + 流式预检 | 不要声称「220 场已完成」 |
| **P2** | 人工标注未开始 | 只有模板和 schema | 不要声称已双标 |
| **P2** | 无 LICENSE / CITATION | 主项目根目录没有 | 发布前必须补 |
| **P3** | 目录名 `v0.22_R16` 误导 | 实际 R26.18 | 重命名或加 README 说明 |
| **P3** | 本地 Python 3.14.7、无 `jsonschema` | `LOCAL_ENV...md` + governance 报告 | 标注工具落地前需锁环境 |

---

## 10. 阅读路线图

**如果只有 10 分钟**：
1. `VETT_R26_18_.../06_新对话交接/HANDOFF_MEMORY.md`
2. `VETT_R26_18_.../00_总览/CURRENT_STATUS.md`
3. 本文件 §1 + §5

**如果要接手工作**（按顺序）：
1. `HANDOFF_MEMORY.md` → `00_总览/README.md` → `CURRENT_STATUS.md`
2. `09_后续行动规划/VETT_CRICKET_FULL_ACTION_AND_UPGRADE_PLAN.md`（990 行，至少读 §2 治理边界、§6 阶段、§13 状态机）
3. `VETT_Cricket_.../README.md`（当前结论 60 条 + 目录表）
4. `VETT_Cricket_.../CHANGELOG.md`（R16→R26.18 的逐版本决策）
5. `docs/R26_18_CANONICAL_SET_CONFORMANCE.md`（当前协议）
6. `docs/R22_FIVE_LEVEL_EVIDENCE_DESIGN.md`（五级设计，理解难度的唯一正确入口）
7. `design/r26_9_metric_contract.json`（冻结指标）
8. `analysis/r26_18_canonical_set/ADMISSION.json`（当前准入）
9. 想复现：`src/vett_eval/cli.py` + `eval_configs/r26_18_..._blocked.json`

**如果要审数据**：
- 结构：`r26_15_content_dependency_candidate_v3/public/match_0021/public_instance.json`
- 金标：同目录 `private/.../private_gold.json`
- 证据：同目录 `private/.../private_evidence.json`
- 审计：`audit/match_0021.audit.json`
- 汇总：`RELEASE_SUMMARY.json`（20 场 / 100 题 / 2816 边 / 25 族）

**如果要审历史**：
- `VETT_COMPLETE_RESEARCH_ARCHIVE_20260903/README_START_HERE.md` + `docs/01_HISTORY_AND_RESULTS.md`
- `docs/R24_FAILURE_AUDIT.md`（一次真实的失败复盘，方法论价值最高）

---

## 11. 我实际读过的东西（可核对）

- 顶层 7 个文件全部；
- 主项目：`README.md`（190 行）、`CHANGELOG.md`（246 行）、`docs/DATA_AND_AUDIT_GUIDE.md`、`docs/R20_BENCHMARK_PROTOCOL.md`、`docs/R22_FIVE_LEVEL_EVIDENCE_DESIGN.md`（397 行）、`docs/R24_FAILURE_AUDIT.md`、`docs/R26_18_CANONICAL_SET_CONFORMANCE.md`、`r25_diagnostic_pilot/CALIBRATION_REPORT.md`、`r26_15.../RELEASE_SUMMARY.json`、`DATASET_CARD.md`、`audit/match_0021.audit.json`、`analysis/r26_18_stage1_readiness_20261112/STAGE1_READINESS_AUDIT.md`、`analysis/r26_18_local_governance_20261112/GOVERNANCE_CONTINUATION_AUDIT.md`、`analysis/r26_18_canonical_set/ADMISSION.json`、`analysis/r26_18_sentinel5_execution_20261112/*`、`eval_configs/r26_18_..._authorized_20261112.json`、`src/vett_eval/cli.py`、`repair_r20/REPAIR_REPORT.md`、`dataset_r20_220/RELEASE_SUMMARY.json`；
- 数据结构：实际用 PowerShell 解析了 `public_instance.json`、`private_gold.json`、`private_evidence.json`；
- 报告包：全部 10 个目录的 21 个文件（含 990 行规划书）；
- 原始数据：`match_0001` 全部 4 个文件、`FINAL_REPORT.md`、`manifest.csv` 表头、`summary.json`；
- 研究归档：由子代理逐目录调查（2,704 文件、62 份快照、20 个实验、57 个 ZIP CRC 审计、35/35 离线复核），结论已并入 §2.2；
- DeepTutor：由子代理做 git/架构/测试/体积全量调查，我自己复核了 git HEAD、体积分布、`pyproject`/`package.json` 元数据和 3,312 个源文件的 `VETT|cricket|scorecard` 检索（仅在运行时 JSON 的绝对路径里命中）。

**未做**：没有运行任何测试（避免与正在跑的付费评测争资源）、没有读取密钥内容、没有修改任何既有文件、没有做完整 SHA-256 复核。
