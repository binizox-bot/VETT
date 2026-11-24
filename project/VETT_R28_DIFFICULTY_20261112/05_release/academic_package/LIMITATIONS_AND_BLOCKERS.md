# 局限与发表阻断项（Limitations & Publication Blockers）

## A. 发表阻断项（必须解决或明确写入 Limitations 才能投稿）

### A1 — 人工双标尚未执行（最高优先级）

- R28 金标来自确定性 solver，**不是人类标注**；E 阶段的人工双标没有执行。
- t24 kit（`04_verify/human_verification_kit/`）已可移交，但 `STATUS.json` 明确：
  - `ready_for_handoff = true`
  - `ready_to_annotate = false`
  - `human_gold_produced = false`
- 在真实双标 adjudicate PASS 之前：
  - 不得声称 H1（每维≥98%）、H2（关键缺陷=0）、H3（资格门）已满足；
  - 数据卡/Limitations 必须写“gold 未经人工一致性验证”；
  - 任何“金标可靠性”推断只能作为待验证假设。

### A2 — 板球规则文本引用许可未闭环

- `src/vett_r25/scenarios.py` 的 `RULE_TEXT` 是 MCC Laws 的简短摘要/改写；仓库没有 MCC 全文再分发许可，也没有显式 LICENSE。
- 数据 CC BY 4.0 / 代码 MIT **不覆盖** MCC 原文；发表前必须法律复核，必要时替换为自建摘要。
- 不得声称“已获 MCC 授权”。

## B. 主张限制（不是“数据坏了”，而是不能这么说）

### B1 — 半合成 / 无逐球事实

- 220 场源素材为虚构场景，仅局级聚合；事实由模板/枚举注入。
- 不能外推到真实比赛分布、真实裁判行为、真实球员能力。

### B2 — 记录空间/结构天花板

- 可达互异记录下界 761；N=320 设计需求 392；合法送达型 dismissal 仅 11 条可达（HA18）。
- 这是冻结单球 solver 的表达力限制；扩大需 R29+ 扩展 solver，不是加 N 能解决。

### B3 — 规则引用装饰性

- 360 实例 / 1546 唯一渲染 span；488（31.57%）从未承载；360/360 至少一个装饰性算子。
- `BAT_CREDIT` 118 / `NB_COUNT` 100 / `WIDE_COUNT` 53 从未必要；`COUNTS_IN_OVER` 317/360 非承载。
- 证书 `rule_path` 只含承载算子（1199 条，0 交集）。
- 三条方法局限：单算子消融、必要性相对 solver、推导深度非已验证机制。

### B4 — 难度主张不成立

- E1 drop 0.557pp（CI [−0.801,+1.846]），`harder_claim_permitted=false`；
- E2 HYP REJECTED（非单调 59.38/62.67/60.94）；
- E3 H3=False；
- record-exact 5/638 = 0.78%。
- **不得**写“R28 比 R26.15 难”。

### B5 — T1 词表匹配 / E5 UNTESTED

- T1 overall 0.975，但 `authority_policy` role 0.75、constant-false 0.85、余量 +0.125；不得写成“模型能判断证据支持”。
- E5 = UNTESTED（仅 1 个本地模型，零付费禁云端）；区分度主张已撤回；不得把 UNTESTED 写成“未跑”或“不适用”，也不得当作 PASS。

## C. 已处置/非阻断（保留披露）

### C1 — t20 Windows GBK 编码（已闭合）

- 修复前：文档单命令在 vanilla Windows GBK 控制台 9/10（D0 UnicodeDecodeError）；需 `PYTHONUTF8=1`。
- 修复后：子进程强制 UTF-8，父进程 `encoding='utf-8'`，harness reconfigure；在 chcp 936、未设 UTF-8 环境变量的控制台 **10/10 PASS, exit 0**；t8 append-only 增量复核已记录。
- 当前无环境前置；pre 归档与 post 哈希保留（`04_verify/t20_closed_loop/archive_prefix_utf8/`）。

### C2 — 审计产物时间戳回填（已披露，不再改回）

- 早前误跑 `protocol_verify --check` 后回填 `checked_at`；已在 `04_verify/PROTOCOL_VERIFY_RERUN_NOTE.json` 完整披露。
- `protocol_verify_result.json` 是派生结果、不在 7 件冻结集；**不得回填时间戳**；当前 22/22。t8 记为 `PASS_WITH_DISCLOSURE`。

### C3 — build_index 旧字节不可 diff（透明 caveat）

- t6 `2502aed5…` → 当前 `dd6de16a…`；t6 replay 目录已删，无法逐字节 diff。
- 已用 360 项 record→private_gold、640 条 e1 gold 绑定与当前 item header 双钉证明数据未变；属**有证据的元数据追加**，不是“已还原旧文件”。见 `04_verify/BUILD_INDEX_FREEZE.json`。

### C4 — 模型输出不是逐位可复现

- temperature=0 也不保证同一输出；152 个样本中 1 个 5 分制分数移动 1 分。
- 可复现的是评分重算、缓存键、数据构建；必须绑定解析器版本 R-R7。

## D. 论文写作检查表

- [ ] 数据卡 B1–B7 全部出现在正文/附录，不只放补充材料
- [ ] “no harder claim” 与 E1/E2/E3/record-exact 同页
- [ ] T1 写作 “word/passage-cue matching”，不写 “semantic support judgment”
- [ ] E5 写 “UNTESTED”，不写成 “not run / 未跑”，也不当作 PASS
- [ ] gold 写 “solver-generated, not human double-annotated”
- [ ] 规则文本引用许可复核记录在案（或已替换为自建摘要）
- [ ] 单命令复现（无环境前置）与 `reproduce.py --check` 输出入附录
