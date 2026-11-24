# VETT-R28 闭环流水线报告（t13）

## 1. 概览

- pipeline：`vett_r28.pipeline` v1.0.0；run_id `_verify/kill_mid`；模式 **DRY-RUN（合成数据，不作证据）**
- config digest：`6029df77730bd9428a97664329d646ba11f5b81c30aa0671bef0b8f42a042555`
- dataset_version：`DRYRUN-SYNTHETIC-DO-NOT-USE-AS-EVIDENCE`；模式 `dry_run_synthetic`；synthetic=`True`
- 运行目录：`D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_R28_DIFFICULTY_20261112\05_pipeline\runs\_dryrun\_verify\kill_mid`
- 写入边界：所有写入均位于本次运行目录内；网络调用 0；付费 API 0
- 缓存对象：12 个（内容寻址，命中即复用）

## 2. 冻结输入与零漂移

- config digest：`6029df77730bd9428a97664329d646ba11f5b81c30aa0671bef0b8f42a042555`；bootstrap 产物 sha256：`1935a3c731eea486739bc1c42619855816d24d831c51b3c02db30074803cd622`
- R26.15：**165 文件 / 93,346,177 字节**，逐文件 sha256 与 t1 冻结备份一致（G_R26_15_ZERO_DRIFT / G_PROTECTED_PATHS 均 PASS）
- prereg / contract / protocol / build_config / protected manifest 均按冻结指纹复核

## 3. 数据集

- 题数：**8**（published 8 / held_out 0）
- 互异记录：8（ratio 1.0）；恒定字段：0；族数：8
- prompt 预算最大值：48 tokens（上限 7000）
- 记录树聚合：`2d6669a22c0e0a06c89e5ff0b22d097c7572f185938484cb61c5abf7e2985024`
- 确定性重放：`True` （synthetic）

## 4. 标注

- 模式：**synthetic**；任务：T1_factor_visibility, S1_span_topic, C1_cert_sentence_consistency
- 计划 12 条，尝试 12 条：OK 12 / DEGRADED 0，覆盖率 **1.0**（下限 0.95）
- DEGRADED 一律计入覆盖缺口，不静默丢弃；缓存策略：内容寻址（input+params+template+model digest），命中即复用，不重复推理/扣费
- 本地标注只作描述性审计，**不是金标**，也不参与端点判定

## 5. 判分

- `C1_cert_sentence_consistency`：n=4，OK=4，DEGRADED=0，机械参考一致 3/4（rate 0.75）
- `S1_span_topic`：n=4，OK=4，DEGRADED=0，机械参考一致 0/0（rate None）
- `T1_factor_visibility`：n=4，OK=4，DEGRADED=0，机械参考一致 2/4（rate 0.5）

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
| G_JUDGE_COMPARABILITY | PASS | judge |
| G_ENDPOINT_UNSCORED | PASS | judge |
| G_BUDGET_WITHIN_CAP | PASS | aggregate |

- 修复轮次记录：0；单门最多 2 轮，第 3 轮仍 FAIL 即 ESCALATED 停止。

## 8. 预算

- 调用 12 次（本地），tokens in/out = 1084/200，成本 ¥0.000000；硬顶 ¥100.00；云端调用 0（上限 80）
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
| `aggregate.json` | `8b08d5d65b7e54bd9c106ae835dae773000c28f137dfd518f0ecbf3656f363fb` |
| `annotations.json` | `fdaade315f33414a0d229796fca38735326178afc0a07531f36fcb16bbd0c85e` |
| `dataset_manifest.json` | `2e73c43c39c3fdfb5139e92fb75340c7885e383196908b6568981d3ee80a6e5b` |
| `judge.json` | `c00ede808ca24322bebdd116f5556f5997da6d6d4becf36dab4cd01d60bf0ffe` |

> 本报告由确定性流水线生成；除 `run_manifest.json` / ledger 外，所有产物在相同输入下逐字节可复现。R26.15 未被修改。
