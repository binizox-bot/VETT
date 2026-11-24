# VETT-R28 闭环流水线报告（t13）

## 1. 概览

- pipeline：`vett_r28.pipeline` v1.0.0；run_id `live_smoke`；模式 **LIVE**
- config digest：`685fd56b5f0bb6c794ee14be5a87789a954cdcd112d0c9ec0f117b95b33e1183`
- dataset_version：`VETT-Cricket-v0.37-R28-diagnostic-pair-20261112`；模式 `live_generator_limited`；synthetic=`False`
- 运行目录：`D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_R28_DIFFICULTY_20261112\05_pipeline\runs\live_smoke`
- 写入次数：12，全部位于本次运行目录内；网络调用 0；付费 API 0

## 2. 冻结输入与零漂移

- config digest：`685fd56b5f0bb6c794ee14be5a87789a954cdcd112d0c9ec0f117b95b33e1183`；bootstrap 产物 sha256：`03bf9e096bb00ef99122979efd075179e736383a211420d8eea73da006a25077`
- R26.15：**165 文件 / 93,346,177 字节**，逐文件 sha256 与 t1 冻结备份一致（G_R26_15_ZERO_DRIFT / G_PROTECTED_PATHS 均 PASS）
- prereg / contract / protocol / build_config / protected manifest 均按冻结指纹复核

## 3. 数据集

- 题数：**2**（published 2 / held_out 0）
- 互异记录：2（ratio 1.0）；恒定字段：3；族数：1
- prompt 预算最大值：917 tokens（上限 7000）
- 记录树聚合：`243b976ae62099b55f45a9001d84819d7e38dffcee564af4fd78ff360cf1d902`
- 确定性重放：`True` （live_generator_limited）

## 4. 标注

- 模式：**mechanical_only**；任务：T1_factor_visibility, S1_span_topic, C1_cert_sentence_consistency
- 计划 3 条，尝试 0 条：OK 0 / DEGRADED 0，覆盖率 **0.0**（下限 0.95）
- DEGRADED 一律计入覆盖缺口，不静默丢弃；缓存策略：内容寻址（input+params+template+model digest），命中即复用，不重复推理/扣费
- 本地标注只作描述性审计，**不是金标**，也不参与端点判定

## 5. 判分

- 无可用标注：判分保持空，覆盖缺口已记录（不伪造分母）

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
| G_CONFIG_VALID | PASS | generate |
| G_DATASET_COUNTS | PASS | generate |
| G_DATASET_INTEGRITY | PASS | generate |
| G_DATASET_DETERMINISM | PASS | generate |
| G_LOCAL_ROUTE | PASS | annotate |
| G_ANNOTATION_CACHE_KEY | PASS | annotate |
| G_ANNOTATION_COVERAGE | DEGRADED | annotate |
| G_LOCAL_FIRST | PASS | annotate |
| G_JUDGE_SCHEMA | PASS | judge |
| G_JUDGE_COMPARABILITY | DEGRADED | judge |
| G_ENDPOINT_UNSCORED | PASS | judge |
| G_BUDGET_WITHIN_CAP | PASS | aggregate |

- 修复轮次记录：0；单门最多 2 轮，第 3 轮仍 FAIL 即 ESCALATED 停止。

## 8. 预算

- 调用 0 次（本地），tokens in/out = 0/0，成本 ¥0.000000；硬顶 ¥100.00；云端调用 0（上限 80）
- 熔断：每次调用后检查累计成本与云端调用数，越线立即落盘 BUDGET_STOP 并停止。

## 9. 降级

- DEGRADED 事件 3 条：`{'LOCAL_SERVICE_UNAVAILABLE': 3}`
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
| `aggregate.json` | `31402a3e85af022612b56323431303ed33ee2060fc26e9fa4d864ee42c61c6b7` |
| `annotations.json` | `e17a86db2d7d07964b39030d21364ffa9882c2648a3cdb18963a9b4bbc43af59` |
| `dataset_manifest.json` | `55acac76af1123cfe138c28e2abb2ff3583911ca417856e9843334be19c4b7ac` |
| `judge.json` | `08b63508b20614a6d61968eb4e5ca90ebeef184168578abe03ff82bc511da746` |

> 本报告由确定性流水线生成；除 `run_manifest.json` / ledger 外，所有产物在相同输入下逐字节可复现。R26.15 未被修改。
