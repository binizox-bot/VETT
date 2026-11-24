# APPENDIX（可选外部效度 / 复现 / 未运行项）

## A. Cricsheet 接地方案（可选附录，不作为主结论）

**现状**：本交付**没有**联网、没有下载、没有使用 Cricsheet；R28 主结论只基于 E1–E5 的 eval_runs 与 gate_ledger。Cricsheet 只作为未来外部效度工作的附录级方案。

**目的**：把 R28 的生成器锚在真实逐球分布上，但不把 R28 变成真实比赛基准。

**步骤**：

1. **许可**：确认 Cricsheet 许可与署名要求；不把原始数据再分发，只发布派生统计/生成器；在数据卡声明来源与衍生关系。
2. **解析**：逐球 delivery → `solver_facts` 子集；字段缺失/歧义显式标 `UNMAPPED`，不静默填充。
3. **接地检查**：
   - 边际分布对齐（status / dismissal / ledger 非零）；
   - 真实 delivery 的可达性 sanity check；
   - 作为外部测试集，不与 R28 调参/选择混用。
4. **重验**：用冻结 solver 重推记录；无法映射的 delivery 不进分母，单独报 `UNMAPPED` 比例。
5. **报告**：只放附录，标 `exploratory, not preregistered`；主结论仍用 R28 预注册分析。
6. **禁止**：不因接入 Cricsheet 就声称“真实世界难度”“人类金标”“通用模型能力”。

**残余风险**：许可、清洗成本、比赛格式差异、单球事实不可从局级聚合恢复；这些都不确定性，不能预填数字。

## B. E6（本地白名单能力）为什么没有数字

- 预注册把 E6 指向本地 5 类白名单任务 vs 机械真值；t18 是 reference-only，R28 没有运行 E6 的 eval_runs endpoint。
- 本论文遵守“数字只来自 eval_runs/gate_ledger”，因此 E6 在 `EXPERIMENTS.md` 中写 `NOT_IN_R28_EVAL_RUNS`，**不从 t18 平移数字**。
- 若未来运行：每类 n≥30、报告点估计+95%CI+效应量；否则保持空白。

## C. 复现与发布工程（与数据卡分开装订）

- 数据卡/许可/held-out 协议/单命令复现：`05_release/academic_package/`（`DATASET_CARD.md`、`REPRODUCIBILITY.md`、`HELD_OUT_PROTOCOL.md`、`reproduce.py`）。
- 独立验证：`04_verify/INDEPENDENT_VERIFICATION.md`；J 门：`04_verify/J_GATE.json`。
- t20 闭环：`cd 05_pipeline && python verify/run_closed_loop_verification.py --config r28.toml`；修复后 vanilla Windows GBK 控制台通过（D0 无解码异常），更早代码需 `PYTHONUTF8=1`。具体读数见 t20 报告，不进入本文结果表。
- 重放语义：可复现的是评分重算/缓存键/数据构建，**不是模型输出逐位复现**；必须绑定解析器版本 R-R7。

## D. 未运行/未使用项清单（防止误读）

| 项 | 状态 | 说明 |
|---|---|---|
| 人工双标 | **NOT_EXECUTED** | 发表阻断项；t24 kit ready_for_handoff=true / ready_to_annotate=false |
| E5 跨模型区分度 | **UNTESTED** | 只有 1 个本地模型；零付费禁云端；区分度主张撤回 |
| E6 本地白名单能力 | **NOT_IN_R28_EVAL_RUNS** | t18 reference-only；R28 无 endpoint；不填数字 |
| 证据预算消融 | **NOT_RUN** | 无 eval_runs 估计；不填“预期” |
| 证书模型侧消融 | **NOT_RUN** | 只有 gate G4 的证书覆盖/重推 PASS，非模型效应 |
| Cricsheet | **NOT_USED** | 可选附录，不作主结论 |
| 真实比赛外部效度 | **NOT_ESTABLISHED** | 半合成；不得外推 |

## E. 附录写作规则

- 附录数字仍受“只来自 eval_runs/gate_ledger”约束；不得在附录“补一个估计”。
- Cricsheet 接入不得改变主结论；若改变，必须新预注册/新版本，而不是补写附录。
- 人工双标完成后，H1/H2/H3 才可写入；此前只能写“未验证/阻断项”。
