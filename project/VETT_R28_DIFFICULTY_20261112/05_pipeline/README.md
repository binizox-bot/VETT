# R28 闭环流水线（t13）

`vett_r28.pipeline` 把 R28 从**冻结基线**一路跑到**报告**：单入口、阶段化、机器可判门、预注册修复、内容寻址缓存、预算熔断、可降级、可 resume、可重放。纯标准库、零网络、零付费 API，写入只发生在本次 run 目录内。

```powershell
cd VETT_R28_DIFFICULTY_20261112\05_pipeline

# 1) 合成长跑：全链路 + 不写真实产物
python -m vett_r28.pipeline --config r28.toml --stage all --dry-run

# 2) 同一命令第二遍：标注全部命中缓存、产物哈希逐一相同
python -m vett_r28.pipeline --config r28.toml --stage all --dry-run

# 3) 真实生成器全量（360 题 / 320 发布 + 40 held-out），本地服务不可用则如实降级
python -m vett_r28.pipeline --config r28.toml --stage all

# 4) 单阶段 / 断点续 / 故障演练 / 人工门
python -m vett_r28.pipeline --stage report --resume
python -m vett_r28.pipeline --stage all --fault local|cloud|disk
python -m vett_r28.pipeline --stage publish            # 默认 exit 7，需 --allow-human-gate
python -m vett_r28.pipeline --list-stages
python -m vett_r28.pipeline --print-registry
```

## 1. 阶段图

| 阶段 | 做什么 | 产物（run 目录内） | 门 |
|---|---|---|---|
| `bootstrap` | 冻结输入指纹 + R26.15 零漂移 | `bootstrap.json` | 7 |
| `generate` | 冻结生成器内存构建 + 确定性抽样重放 | `dataset_manifest.json` | 4 |
| `annotate` | 本地标注（缓存 + 预算 + 降级） | `annotations.json` | 4 |
| `judge` | 机械参考对照、覆盖率、端点状态 | `judge.json` | 3 |
| `aggregate` | 数据集/标注/预算/降级汇总 | `aggregate.json` | 1 |
| `report` | 确定性报告 + 产物哈希 + 重放对比 | `REPORT.md`、`PIPE_RECEIPT.md`、`ARTIFACT_HASHES.json`、`REPLAY_CHECK.json` | 2 |
| `publish` | 仅人工门；只组装决策包，不发布 | `PUBLISH_READINESS.json`、`PUBLISH_DECISION_PACKET.md` | 0 |

`--stage all` = 前六个阶段（**不含** `publish`）。`--stage <name>` 会自动先跑其前置阶段。`--resume` 按 `state.json`（含 config digest）跳过已完成阶段。

## 2. 内容寻址缓存

键 = `sha256(canonical_json{input_sha256, params(temperature/seed/num_ctx/num_predict), prompt_template_version, model_digest})`，与 t12 `judge_protocol.cache_key`（v2）逐位一致（单测校验）。
- 命中：直接复用存储的 envelope，0 次模型调用、0 token 扣费；缓存对象自带 basis，键不符即隔离（`.quarantine`）而不是误用。
- 位置：`runs/<run_id>/cache/objects/<aa>/<key>.json`；dry-run 使用独立 run 目录，不污染真实缓存。
- 结果：第二遍同命令 12/12 命中，`cache.misses=0`，`ARTIFACT_HASHES.json` 逐字节相同，`REPLAY_CHECK.identical=true`。

## 3. 门注册表（23 个纯函数）

每个门返回 `{verdict, evidence}`；`PASS` 才放行，`FAIL` 记入 `gate_ledger.jsonl`。规则：

- `blocking=true`：`FAIL` → 预注册修复 → 最多 2 轮 → 仍 `FAIL` 则 **ESCALATED**（exit 6）。
- `blocking=false`：只允许 `DEGRADED`（覆盖率/判分可比性），记录后在报告中体现为缺口，不伪装成 PASS。
- 冻结类门 `exit_code=4`：`FAIL` 立即 `FROZEN_VIOLATION`，没有修复路径。
- 机器可读注册表：`GATE_REGISTRY.json`（根目录快照）与每次 run 的 `GATE_REGISTRY.json`。

关键门：`G_PREREG_FROZEN` / `G_CONTRACT_FROZEN` / `G_PROTOCOL_FROZEN`（冻结指纹）、`G_SOLVER_PIN`（vett_r25 solver 钉死）、`G_R26_15_ZERO_DRIFT` + `G_PROTECTED_PATHS`（165 文件 / 93,346,177 B / 338 受保护文件）、`G_DATASET_*`（互异/恒定字段/孪生/prompt 预算/确定性）、`G_LOCAL_ROUTE` + `G_LOCAL_FIRST`（本地优先）、`G_ENDPOINT_UNSCORED`（未产生答案就绝不声称端点）、`G_BUDGET_WITHIN_CAP`、`G_ARTIFACTS_DETERMINISTIC`、`G_REPORT_COMPLETE`。

## 4. 有界修复（预注册，最多 2 轮）

| repair_id | 绑定门 | 动作 |
|---|---|---|
| `rebuild_dataset` | G_DATASET_DETERMINISM | 用冻结生成器重建确定性抽样并复算摘要 |
| `retry_annotation` | G_ANNOTATION_COVERAGE | 重探本地服务；可用才重试，不可用保持降级 |
| `rescore_judge` | G_JUDGE_COMPARABILITY | 从已存标注与机械参考重算判分 |
| `rebuild_report` | G_REPORT_COMPLETE | 从当前产物重建报告 |
| `rewrite_artifact_hashes` | G_ARTIFACTS_DETERMINISTIC | 从磁盘产物重算哈希 |

修复**不得**改阈值、不得改门谓词、不得绕过缓存或伪造标注。第 3 轮仍失败：写 `ESCALATED.json` 并停止等人工。

## 5. 自动降级（全部落 `DEGRADED_EVENTS.jsonl`）

| 故障 | 降级路径 | 结果 |
|---|---|---|
| 本地服务不可用 | 机械证书路径继续（无模型标注） | `coverage=0` 如实报告，链路继续，exit 0 |
| 云端/付费 ruler | 禁用；只标描述性，绝不回退调用 | `CLOUD_RULER_UNAVAILABLE` |
| 磁盘不可写 | 回退临时目录并记录 | `DISK_UNAVAILABLE`，run 继续 |

`--fault local|cloud|disk` 用于无人值守的降级演练（不加载 7B 模型）。

## 6. 预算熔断

每次调用（含命中与降级）写一行 `cost_ledger.jsonl`（tokens、成本、累计、缓存命中）。累计成本 > 硬顶（默认 ¥100）或云端调用 > 80 → 立即 fsync 账本、写 `BUDGET_STOP.json`、抛 `BudgetStop`（exit 5），不再发起任何调用。

## 7. 本地优先与人工门

- 白名单 `T1/T2/S1/C1`：`assert_local_first` + 只允许 loopback endpoint，路由到云端直接抛异常（`LocalFirstViolation`/`CloudForbidden`，exit 4）。
- `publish_decision`、`modify_endpoint`：`allow_human_gate=False`（默认）时抛 `HumanGateRequired`（exit 7）。
- 写入 R26.15：无条件拒绝（`HumanGate.guard_write`），即使 `--allow-human-gate` 也不放行。
- `publish` 阶段只写「待人工签署」决策包，从不发布数据集。

## 8. 退出码

| 码 | 含义 |
|---|---|
| 0 | OK（非阻塞降级已记录） |
| 2 | 配置/用法错误 |
| 3 | 阻塞门失败或阶段错误（无修复路径） |
| 4 | 冻结输入漂移（R26.15 / 受保护文件 / prereg / contract / protocol）或本地优先违规 |
| 5 | BUDGET_STOP |
| 6 | ESCALATED（2 轮修复后仍 FAIL） |
| 7 | 需要人工门 |

## 9. t20 闭环验证（故障注入 / 降级 / 字节级重放 / resume / dry-run）

```powershell
python verify/run_closed_loop_verification.py --config r28.toml   # 10/10 PASS
```

- 覆盖：kill -9 → `--resume`（无重复调用、产物一致）、本地停服 → 机械回退、缓存篡改 → 隔离重算、两遍全命中、`--dry-run` 零真实写入、`raw_output` 字节级重放（replay≠regeneration）、路由卡唯一来源、族抽样单位 + 族 bootstrap、J8 模板卫生（独立复算）。
- 结果与日志：`04_verify/t20_closed_loop/`、`verify/out/`。
- **Windows 控制台**：建议设 `PYTHONUTF8=1`（belt-and-braces），但**不是前置条件**——harness 对所有子进程强制 UTF-8 并以 `encoding='utf-8', errors='replace'` 解码，自身输出也 reconfigure 为 UTF-8；已在 `chcp 936`、未设 `PYTHONUTF8` 的环境实测 **10/10 PASS**（t8 F10 修复）。
- 新增门：`G_ROUTING_CARD`（ALLOW/DENY 只从 routing_card.json 读取 + 静态绕过扫描）、`G_FAMILY_UNIT`（每族 ≤1 题 / 一题一记录 / 族 bootstrap 可用）。
- 缓存对象带 `result_sha256`：篡改结果会被隔离（`.quarantine`）并重算，绝不静默使用。
- 协议门只认 `protocol_freeze.json` 的 7 个冻结 artifact；派生的 `protocol_verify_result.json` 被显式排除（否则每次 `--check` 假漂移）。

## 10. 测试

```powershell
python -m unittest discover -s tests -v     # 22 项，离线
```

覆盖：配置校验、缓存键与冻结协议一致、缓存隔离、预算熔断、本地优先断言、人工门、注册表完备性、有界修复/升级、非阻塞降级、冻结门 exit 4、dry-run 全链路、第二遍全命中且哈希相同、重放一致、报告完整性、写入范围、降级演练、resume、publish 人工门、磁盘故障回退、单阶段前置。

## 11. 边界与诚实声明

- `--dry-run` 使用合成数据，产物明确标记 `synthetic`，**不得作为证据**。
- 主端点 `paired_accuracy_drop` 永远 `NOT_RUN`：流水线只编排与审计，不评分模型答案、不伪造准确率；端点判定仍归 E1/E2。
- live 模式下默认只标注 `T1/S1/C1` 的有界样本；`T2` 需要干净的 `V+/V−` 配对，未在本流水线默认启用。
- live 全量 = 冻结生成器的 360 题（320 发布 + 40 held-out）内存构建，不落数据集；数据集落盘仍由 t6 `build_dataset.py` 负责。
- 全程 0 网络、0 付费 API、未读 `.secrets`；`runs/` 之外零写入。

## 12. 文件

```
05_pipeline/
  r28.toml                    配置（路径、预算、标注、生成、故障）
  vett_r28/pipeline/          实现（config/cache/budget/routes/human/gates/repairs/
                              adapters/samples/degrade/context/stages/runner/__main__）
  tests/test_pipeline.py      22 项离线测试
  GATE_REGISTRY.json          23 门快照
  REPAIR_REGISTRY.json        5 条预注册修复快照
  PIPELINE_RECEIPT.md         验收回执（命令 + 结果）
  PIPELINE_VERIFICATION.json  机器可读验收结果
  ACCEPTANCE_EVIDENCE.json    两次 dry-run 的缓存/预算/哈希/重放证据
  runs/_drills/               故障演练的清单副本
  runs/<run_id>/              每次运行的产物、账本、日志、缓存
```




