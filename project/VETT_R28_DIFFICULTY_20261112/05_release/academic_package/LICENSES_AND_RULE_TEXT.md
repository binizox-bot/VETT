# 许可与板球规则文本引用核对

## 1. 定稿候选

| 对象 | 许可 | 文件 |
|---|---|---|
| R28 生成数据（public/variants/held_out/记录/证书/audit） | **CC BY 4.0** | `LICENSE_DATA_CC_BY_4.0.md` |
| R28 构建/验证代码、本包脚本 | **MIT** | `LICENSE_CODE_MIT.txt` |

两项均已按“数据/代码分别定稿”的要求分文件声明；SPDX 标识分别为 `CC-BY-4.0` 与 `MIT`。

## 2. 板球规则文本：核对结果（必须如实披露）

`src/vett_r25/scenarios.py` 的 `RULE_TEXT` 是**简短的规则摘要/改写**，引用 MCC Laws 的条号（如 “Law 21.17”, “Law 22.9”）与概念，例如：

- `NB_PRECEDENCE`: “Law 21.12: a No-ball call overrides a Wide call at any time.”
- `NB_DISMISSAL_GATE`: “Law 21.17: after No ball, dismissal is unavailable except …”
- `DEAD_SEQUENCE`: “Laws 20.1 and 20.6: …”

核对所见：

1. **没有发现**仓库内附带 MCC 规则全文、MCC 的再分发许可，或任何显式 `LICENSE` 文件。
2. `RULE_TEXT` 是**摘要/改写**，不是逐字全文；但“改写”不自动等于“无版权风险”，条号与表达仍需法律复核。
3. 因此本包不能声称已获得 MCC 的授权，也不能把 `RULE_TEXT` 纳入 CC BY 4.0 的再许可范围；它只作为研究代码中的引用/改写保留。
4. **发表前动作**：由数据所有者做一次法律复核；若不能确认可再分发，替换为**完全自建的规则摘要**（保留条号引用、去掉受版权保护的具体表达），或在论文附录中只引用条号、不复制文本。
5. 这是 **B7 发布边界**；不能因为“只是短句”而省略。

## 3. 源素材（220 场）与 Cricsheet

- 220 场为半合成虚构素材（`AUDIT_GOAL_AND_DESIGN_20261112.md` §189–191），本包不替其授权；数据所有者需确认源侧许可。
- 若未来接入 Cricsheet：遵守其许可、保留来源/衍生声明；Cricsheet 只作为**附录级可选外部效度检查**，不作为主结论依赖（`EXTERNAL_VALIDITY.md`）。
- 不使用任何付费 provider / 云端 API；本包脚本零网络。

## 4. 结论

- 数据/代码许可**可定稿**为 CC BY 4.0 / MIT；
- **规则文本引用许可未闭环**，是发表前的法律复核项（不是数据许可失败）；
- 未发现可声称的 MCC 授权；不写“已获授权”。
