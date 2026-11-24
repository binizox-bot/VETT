# VETT-R28 闭环流水线报告（t13）

## 1. 概览

- pipeline：`vett_r28.pipeline` v1.0.0；run_id `_verify/replay_live`；模式 **LIVE**
- config digest：`4b96fe32f6b67a17976fc15b904b258b169020091788b131069b209b0f3764ff`
- dataset_version：`VETT-Cricket-v0.37-R28-diagnostic-pair-20261112`；模式 `live_generator_limited`；synthetic=`False`
- 运行目录：`D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_R28_DIFFICULTY_20261112\05_pipeline\runs\_verify\replay_live`
- 写入边界：所有写入均位于本次运行目录内；网络调用 0；付费 API 0
- 缓存对象：6 个（内容寻址，命中即复用）

## 2. 冻结输入与零漂移

- config digest：`4b96fe32f6b67a17976fc15b904b258b169020091788b131069b209b0f3764ff`；bootstrap 产物 sha256：`6a16f215501f3784157274ac3567bbecc07a9d878220b80df62062b60993461c`
- R26.15：**165 文件 / 93,346,177 字节**，逐文件 sha256 与 t1 冻结备份一致（G_R26_15_ZERO_DRIFT / G_PROTECTED_PATHS 均 PASS）
- prereg / contract / protocol / build_config / protected manifest 均按冻结指纹复核

## 3. 数据集

- 题数：**2**（published 2 / held_out 0）
- 互异记录：2（ratio 1.0）；恒定字段：3；族数：2
- prompt 预算最大值：917 tokens（上限 7000）
- 记录树聚合：`243b976ae62099b55f45a9001d84819d7e38dffcee564af4fd78ff360cf1d902`
- 确定性重放：`True` （live_generator_limited）

## 4. 标注

- 模式：**local**；任务：T1_factor_visibility, S1_span_topic, C1_cert_sentence_consistency
- 计划 6 条，尝试 6 条：OK 6 / DEGRADED 0，覆盖率 **1.0**（下限 0.95）
- DEGRADED 一律计入覆盖缺口，不静默丢弃；缓存策略：内容寻址（input+params+template+model digest），命中即复用，不重复推理/扣费
- 本地标注只作描述性审计，**不是金标**，也不参与端点判定

## 5. 判分

- `C1_cert_sentence_consistency`：n=2，OK=2，DEGRADED=0，机械参考一致 2/2（rate 1.0）
- `S1_span_topic`：n=2，OK=2，DEGRADED=0，机械参考一致 0/0（rate None）
- `T1_factor_visibility`：n=2，OK=2，DEGRADED=0，机械参考一致 0/2（rate 0.0）

## 6. 端点状态

- `paired_accuracy_drop`：**NOT_RUN**，未做任何端点声称；无模型答案即无准确率。
- 预注册 ZR1–ZR6 与停止规则未被本流水线触发或改写；端点判定仍由 E1/E2 负责。

## 7. 门与修复

| gate | verdict | stage |
|---|---|---|
| G_PREREG_FROZEN | PASS | bootstrap |
| G_CONTRACT_FROZEN | PASS | bootstrap |
| G_PROTOCOL_FROZEN | PASS | bootstrap |
| G_SOLVER_PIN | PASS | bootstrap |
| G_R26_15_ZERO_DRIFT | PASS | bootstrap |
| G_PROTECTED_PATHS | PASS | bootstrap |
| G_BUDGET_CONFIG | PASS | bootstrap |
| G_FAMILY_UNIT | PASS | generate |
| G_CONFIG_VALID | PASS | generate |
| G_DATASET_COUNTS | PASS | generate |
| G_DATASET_INTEGRITY | PASS | generate |
| G_DATASET_DETERMINISM | PASS | generate |
| G_ROUTING_CARD | PASS | annotate |
| G_LOCAL_ROUTE | PASS | annotate |
| G_ANNOTATION_CACHE_KEY | PASS | annotate |
| G_ANNOTATION_COVERAGE | PASS | annotate |
| G_LOCAL_FIRST | PASS | annotate |
| G_JUDGE_SCHEMA | PASS | judge |
| G_JUDGE_COMPARABILITY | FAIL | judge |
| G_ENDPOINT_UNSCORED | PASS | judge |
| G_BUDGET_WITHIN_CAP | PASS | aggregate |

- 修复轮次记录：0；单门最多 2 轮，第 3 轮仍 FAIL 即 ESCALATED 停止。

## 8. 预算

- 调用 6 次（本地），tokens in/out = 532/61，成本 ¥0.000000；硬顶 ¥100.00；云端调用 0（上限 80）
- 熔断：每次调用后检查累计成本与云端调用数，越线立即落盘 BUDGET_STOP 并停止。

## 9. 降级

- DEGRADED 事件 0 条：`{}`
- 本地不可用 → 机械证书路径继续（coverage 缺口如实报告）；云端不可用 → 描述性标记，绝不静默回退；磁盘不可用 → 回退目录 + 事件记录。

## 10. 复现

```powershell
cd VETT_R28_DIFFICULTY_20261112\05_pipeline
python -m vett_r28.pipeline --config r28.toml --stage all --dry-run
python -m vett_r28.pipeline --config r28.toml --stage all
```

- 第二次相同命令：标注全部命中内容寻址缓存，产物哈希必须逐一相同（见 REPLAY_CHECK.json / ARTIFACT_HASHES.json）。

## 11. 产物哈希

| artefact | sha256 |
|---|---|
| `aggregate.json` | `9d02648ede3b7baced3845394ac27377fed36c3b74bef7e9c6844a7f15da1018` |
| `annotations.json` | `6810178420ced68995a0f7ad7f751e7ba5d7771393a60b4bc4e5ffab3430cb1b` |
| `dataset_manifest.json` | `c6938ab997efbb21a210b72a46f6b24cc73961a3d28800fae5f3243818f3684d` |
| `judge.json` | `e33580fc66eaf52ae679b09ae991d758f5d320990b40b722e32d11b6a978d623` |

> 本报告由确定性流水线生成；除 `run_manifest.json` / ledger 外，所有产物在相同输入下逐字节可复现。R26.15 未被修改。
