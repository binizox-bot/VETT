# D0 孪生卷宗原型说明（t7）

- 数据集：`03_build/dataset_r28` ｜ config `cc78be40996eaed4…` ｜ solver `4fcd8a10fe5cb7c8…`
- 抽样：5 题（FACTOR 1111 / D1-2 / D2-2 / D3-2 / D4-2，每层取 item_id 最小的发布题）
- **门 D0 结论：PASS**（机械约束 5/5；可读性 1.0 ≥ 0.8）

## 1. 三个变体

- **V+（决定性事实）**：直接采用**证书自带的 countermodel**（同一字段、同一替代值），因此“证书 countermodel 是否与 V+ 一致”由构造保证，并逐题复核新记录 sha。
- **V−（非决定性事实）**：优先把某个事实改成**使记录逐字节不变**的替代值（`non_decisive_substitution`）；若该题所有事实都决定性（本例 D0-C4，13/13 事实 pivotal），则引入一个对该题不适用的新事实（`non_decisive_fact_introduced`，如 OBSTRUCTING_FIELD 案件加 `forced_not_count`）。两种做法都要求记录不变。
- **V0（顺序置换）**：文档顺序整体反转、每篇文档内 span 顺序反转；span id / document id / 文本多重集 / 计数全部守恒。

## 2. 逐题结果

| case | item | 机制 | 剂量 | V+ 字段 | 旧 → 新 | V+ 变化字段（信息字段） | V− 方式与字段 | V− 变化 | V0 计数守恒 | V0 变化 | countermodel |
|---|---|---|---|---|---|---|---|---:|---|---:|---|
| D0-C1 | `r28q_0121` | FACTOR | FACTOR | `penalty_runs_batting` | 5 → 0 | 2（total_runs, ledger.PENALTY；信息字段 1） | 替代 `appeal_in_time` True→False | 0 | 7→7 文档 / 23→23 span，守恒 | 0 | 一致 |
| D0-C2 | `r28q_0161` | D1 | D1-2 | `completed_runs` | 1 → 0 | 2（total_runs, ledger.BYE；信息字段 1） | 替代 `appeal_in_time` True→False | 0 | 4→4 文档 / 21→21 span，守恒 | 0 | 一致 |
| D0-C3 | `r28q_0209` | D2 | D2-2 | `boundary_mode` | OVERTHROW → NONE | 2（total_runs, ledger.BYE；信息字段 1） | 替代 `appeal_in_time` True→False | 0 | 4→4 文档 / 22→22 span，守恒 | 0 | 一致 |
| D0-C4 | `r28q_0257` | D3 | D3-2 | `appeal_in_time` | True → False | 1（dismissal；信息字段 1） | 引入 `forced_not_count` None→True | 0 | 4→4 文档 / 25→25 span，守恒 | 0 | 一致 |
| D0-C5 | `r28q_0305` | D4 | D4-2 | `boundary_allowance` | 4 → 0 | 2（total_runs, ledger.BYE；信息字段 1） | 替代 `appeal_in_time` True→False | 0 | 4→4 文档 / 25→25 span，守恒 | 0 | 一致 |

> V+ 的“变化字段”列给出 12 字段中变化的字段数与名称；括号内为其中属于 9 个信息字段的个数。门要求 **1 ≤ 信息字段变化数 ≤ 3**；5 题实测均为 1 个信息字段（另可能带 1 个非信息账本字段）。

## 3. 机械约束（5/5）

逐题五项布尔：V+ 可用、V+ 信息字段变化 1–3、V− 变化 0、V0 变化 0 且文档/span 计数守恒、证书 countermodel 与 V+ 一致。

结果：**5/5 题全部通过**

- V− 构造方式分布：`{'non_decisive_substitution': 4, 'non_decisive_fact_introduced': 1}`
- countermodel 一致：5/5

## 4. 可读性盲测

- 判读者：**本会话模型**（只看改动后事实集与两条候选记录，不看任何 span）
- 盲包：`D0_READABILITY_PACKET.md`，sha256 `dfc8ff2723ad87982334c3119d1f7b25f319bef3781d96d0b85072bf0f1d2ff5`；答案键：`D0_READABILITY_KEY.json`；作答：`D0_READABILITY_ANSWERS.json`
- 流程：先写盲包（A/B 顺序由固定种子随机化）→ 判读者读包作答并落盘 → `--stage finalize` 才读取答案键计分。作答文件的时间戳早于计分。
- 说明：首次计分时发现两个**计分器 bug**（答案文件顶层包裹 `answers` 未展开；以及键把“可推导侧”标成了改动前记录一侧）。修复过程中盲包被重新生成了两次，最终落盘盲包 sha256 与判读时**逐字节相同**（`dfc8ff2723ad8798…`），且判读在修复前完成，因此没有用答案反推题面。
- 命中：**5/5 = 1.0**（阈值 0.8）

| case | 回答 | 可推导侧 | 命中 | 推导要点 |
|---|---|---|---|---|
| D0-C1 | B | B | ✓ | LEGAL / dismissal NONE. movement = completed 3 + OVERTHROW allowance 6 + crossed 1 = 10, award +1 = 11; contact BAT so all 11 go to ledger.BATTER; penalty_runs_batting is 0 (no wilful) so ledger.PENALTY = 0, total = 11,  |
| D0-C2 | B | B | ✓ | NO_BALL (no_ball_called). wilful_deception trips the dead gate so dismissal = NONE. ledger.NO_BALL_EXTRA = 1. movement = completed 0 + award 1 = 1 (award and wilful add a single +1, not two), contact NONE so BYE = 1. PEN |
| D0-C3 | A | A | ✓ | LEGAL (no no-ball, no wide). wilful_deception trips the dead gate so dismissal = NONE. movement = completed 2, boundary_mode NONE so the 6-run allowance is not applied, award +1 = 3; contact NONE so BYE = 3. PENALTY = 0  |
| D0-C4 | B | B | ✓ | NO_BALL. appeal_in_time is false, so the appeal gate blocks the Obstructing-the-field candidate and dismissal = NONE (candidate A keeps OBSTRUCTING_FIELD, which needs a timely appeal). NO_BALL_EXTRA = 1. movement = compl |
| D0-C5 | B | B | ✓ | NO_BALL. wilful_deception trips the dead gate so dismissal = NONE (the Stumped/Run-out choice is never reached). NO_BALL_EXTRA = 1. movement = completed 3 + OVERTHROW allowance 0 + not crossed 0 = 3, award +1 = 4; contac |

## 5. 发现与根因记录

- **该题所有事实都决定性**：D0-C4（`r28q_0257`，NO_BALL + OBSTRUCTING_FIELD）的 13 个事实全部 pivotal，不存在“把某个既有事实改成惰性值”的 V−；改用“引入不适用事实”构造。这不是数据缺陷，而是该实例信息密度高（任何单点改动都会改变记录）。
- **V+ blast radius 很小**：5 题都只有 1 个信息字段变化（外加 0–1 个非信息账本字段），说明单事实反事实在 R28 记录上确实是局部的、可审计的。
- **V0 纯顺序置换对记录零影响**：文档/span 计数与 id 全部守恒，记录 0 变化，符合“呈现层操纵不改答案”的合同要求（但注意：这只说明置换不变，不说明模型不受顺序影响）。

## 6. 边界与诚实说明

- 这是 **D0 原型**：5 题只证明“孪生卷宗可构建、证据敏感性可机械核验”，**不构成**任何难度、解释质量或统计主张。
- 可读性判读由本会话模型完成，**n=5**：Wilson 95% 区间约为 [0.57, 1.00]，5/5 只说明“这 5 个事实集足以推出金标”，不能当作人类可读性或模型可解释性的证据。
- V+ 只改一个事实且复用证书 countermodel；多事实、跨字段、非 countermodel 的反事实未在 D0 覆盖。
- V− 的“引入不适用事实”比“改既有事实”弱：它证明记录对不相关事实不敏感，但不证明记录对该字段的某个具体取值不敏感。
