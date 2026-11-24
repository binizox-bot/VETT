# R28 数据集卡（CANDIDATE，t6 构建）

- **数据集**：`VETT-Cricket-v0.37-R28-diagnostic-pair-20261112`（design `R28-DOSE-DIAGNOSTIC-PAIR`）
- **规模**：发布集 **320** + held-out **40**（一题一记录、一题一族、每题独立卷宗）
- **配置**：`config/r28_build_config.json` sha256 `cc78be40996eaed4f8d5ac49ceec1cf55dd7739d2b81c3f49c47246024e525d6`（合同 v1.1.0 sha256 `7f10f9833ec0edc88a713fc77e34833a1503b2573a77e7ed0d7407782075a94b`）
- **金标**：确定性 solver `vett_r25.solver`（sha256 见 `MANIFEST.json`）；**无任何语言模型参与事实、金标或证书**

## 1. 两臂与“事实相同”

- 发布版（dose 按格赋值）与对照版（四剂量全 0）共享**逐字节相同**的 `solver_facts` 与 12 字段 `decision_record_flat`；差异只在卷宗呈现层。
- “事实相同”= 解析后的 solver 事实与记录相同，**不是**公开文本相同——公开文本正是被操纵的变量。

## 2. 四剂量：全部 UNTESTED

D1 alias_hops 0/1/2 ｜ D2 temporal_joins 0/1/2（真修订链：版本+生效时间+join 回放）｜ D3 scope_decisions 0/1/≥2（多源冲突+masked cell，裁决回同一组 facts）｜ D4 isomorphic_distractors 0/1/≥2（含 near-miss）。

> **剂量已分配，效果未验证。**“更难”只能由 E2（HYP-R28-DOSE）判定；不得用 span 数、token 数或样例量作为难度证据。

## 3. 分布（发布集）

- delivery_status：`{'DEAD_REBALL': 1, 'LEGAL': 166, 'NO_BALL': 100, 'WIDE': 53}`
- dismissal：`{'BOWLED': 2, 'CAUGHT': 2, 'HIT_BALL_TWICE': 50, 'LBW': 2, 'NONE': 124, 'OBSTRUCTING_FIELD': 50, 'RUN_OUT': 86, 'STUMPED': 4}`
- 账本非零：`{'ledger.BYE': 96, 'ledger.LEG_BYE': 78, 'ledger.PENALTY': 153}`
- 合法 dismissal 合计（HA18 封顶 11）：11
- 互异记录：320 / 320（比率 1.0）

## 4. 结构天花板（合同 §6，须在论文复述）

- `DEAD_REBALL` 强制全账本清零且 dismissal=NONE → 只有 1 个可达记录。
- `BOWLED`/`LBW`/`CAUGHT` 各 2 个可达记录、`STUMPED` 4 个 → 合法 dismissal ≤11，不随 N 放大（HA18）。
- `WIDE` 状态 contact 必须 NONE → BYE/LEG_BYE 恒 0；BYE 与 LEG_BYE 互斥。

## 5. 记录空间与余量

- 规范网格可达互异记录 **4001**（与合同逐层 `reachable_cap` 不一致 65 层）
- 扩展网格 **4001**；需求 360（含 10% 余量 392）→ 满足

## 6. 已知限制

- solver 是单球规则查表器，不是多跳推理机；金标未经人工双标。
- 族名基线：族名是中性哈希（`rfam_`+12 hex），一题一族。值平衡准确率见 `BUILD_ACCEPTANCE.json`；逐单元准确率的**结构性下限**是边际众数（约 55%），因为三个字段按构造大量为零——它不是族名泄漏。
- 确定性只针对数据构建（同 seed 同配置逐字节可重建），不针对任何模型输出。

## 7. 验证

- 12 项 t6 验收：见 `BUILD_ACCEPTANCE.json`（由 `scripts/verify_build.py` 只读磁盘独立重算）。
- `STABILITY_AUDIT.json`：分布稳定性 + 二次构建确定性 + R26.15 零漂移。
