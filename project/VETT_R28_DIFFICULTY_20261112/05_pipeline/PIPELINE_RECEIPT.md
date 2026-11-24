# t13 闭环流水线验收回执

- 实现：`05_pipeline/vett_r28/pipeline/`（14 个模块）
- 配置：`05_pipeline/r28.toml`
- 测试：`05_pipeline/tests/test_pipeline.py`（22 项，离线）
- 状态：**PASS**（`--dry-run` 全绿；第二次同命令全命中缓存且产物哈希逐一相同；live 全量 360 题跑到报告）
- 边界：0 网络、0 付费 API、未读 `.secrets`；写入只在 `05_pipeline/runs/` 内；R26.15 零字节改动。

## 1. 验收命令与结果

| # | 命令（cwd = `05_pipeline`） | 退出码 | 结果 |
|---|---|---|---|
| 1 | `python -m vett_r28.pipeline --config r28.toml --stage all --dry-run`（第 1 次） | 0 | 6 阶段 + 21 门全 PASS；cache miss 12 / hit 0 |
| 2 | 同一命令（第 2 次） | 0 | cache **hit 12 / miss 0**；`ARTIFACT_HASHES.json` 与第 1 次逐字节相同；`REPLAY_CHECK.identical=true` |
| 3 | `python -m vett_r28.pipeline --stage all --fault local --run-id live_full` | 0 | 真实生成器 360 题（320 发布 + 40 held-out）→ 标注 → 报告；本地不可用如实降级（3 条 DEGRADED，coverage 0），链路继续 |
| 4 | `python -m vett_r28.pipeline --stage all --fault local --limit 2 --sample-instances 1` | 0 | live 冒烟 + 降级演练 |
| 5 | `python -m vett_r28.pipeline --stage all --fault cloud --dry-run --run-id dryrun_cloud` | 0 | `CLOUD_RULER_UNAVAILABLE` 记录，禁云路径不回退（`runs/_dryrun/dryrun_cloud/`） |
| 6 | `python -m vett_r28.pipeline --stage all --fault disk --dry-run --run-id disk_drill` | 0 | 回退临时目录，`DISK_UNAVAILABLE` 记录，链路继续（清单副本 `runs/_drills/disk_drill_run_manifest.json`） |
| 7 | `python -m vett_r28.pipeline --stage publish --dry-run --run-id publish_gate` | **7** | `HUMAN_GATE_REQUIRED`；未写 `PUBLISH_READINESS.json`（`runs/_dryrun/publish_gate/`） |
| 8 | `python -m vett_r28.pipeline --stage publish --allow-human-gate --dry-run --run-id publish_packet` | 0 | 只写 `PUBLISH_READINESS.json`（`AWAITING_HUMAN_SIGNATURE`），未发布任何数据（`runs/_dryrun/publish_packet/`） |
| 9 | `python -m vett_r28.pipeline --stage all --dry-run --resume` | 0 | 6/6 阶段 `resumed`，0 次新调用 |
| 10 | `python -m vett_r28.pipeline --stage report --dry-run` | 0 | 单阶段自动补前置，6 阶段 done |
| 11 | `python -m unittest discover -s tests -v` | 0 | **22 tests OK** |
| 12 | 主项目基线：`$env:PYTHONPATH='src'; python -m unittest discover -s tests -p 'test_*.py'` | 0 | **203 tests OK**（205.8s） |
| 13 | t1 备份校验：`python _BACKUPS\...\_tools\baseline_backup.py verify` | 0 | **22/22 checks passed**；r26_15 165 文件 / 93,346,177 B / 聚合 `343afde4…51bd` |

## 2. 能力对照（任务硬性要求）

| 要求 | 实现 | 证据 |
|---|---|---|
| 单入口 `python -m vett_r28.pipeline --config r28.toml --stage all` | `__main__.py` + `runner.py` | 命令 1–3 |
| `--stage` 单跑 | 自动补前置；`--list-stages` | 命令 10 |
| `--dry-run` 合成输入不写真实产物 | 独立 `runs/_dryrun/`，产物标记 `synthetic` | 命令 1–2；`REPORT.md` §1 |
| `--resume` 内容寻址断点续 | `state.json`（含 config digest）逐阶段跳过 | 命令 9 |
| 内容寻址缓存，键 = sha256(input+params+prompt_version+model_tag/digest) | `cache.py`，与 t12 `judge_protocol.cache_key` v2 一致 | 单测 `test_cache_key_matches_frozen_protocol`；命令 2 |
| 门注册表：纯函数返回 `{verdict, evidence}`，PASS 才放行，FAIL 落 `gate_ledger.jsonl` | `gates.py` 21 门 + `GATE_REGISTRY.json`；`gate_ledger.jsonl` | 每次 run 的 `gate_ledger.jsonl` |
| 有界修复：单门最多 2 轮，第 3 轮仍 FAIL → ESCALATED 停止 | `runner.run_gate`（MAX_REPAIRS=2）+ `repairs.py` 5 条预注册修复 | 单测 `test_gate_loop_is_bounded_and_escalates`：FAIL×3 + ESCALATED×1、修复恰好 2 次 |
| 自动降级：云端/本地/磁盘任一不可用 → 预定义路径 + DEGRADED 事件 + 链路继续 | `degrade.py` + `annotate_stage`/runner 回退 | 命令 3、5、6；`DEGRADED_EVENTS.jsonl` |
| 预算熔断：每次调用记 token，超硬顶 → BUDGET_STOP 立即落盘停止 | `budget.py`（fsync + `BUDGET_STOP.json`） | 单测 `test_budget_breaker_stops_and_writes_stop_file`、`test_budget_stop_halts_pipeline`（exit 5） |
| 本地优先断言：白名单任务走云端直接抛异常 | `routes.assert_local_first` / `CloudForbidden` / `assert_local_endpoint` | 单测 `test_local_first_assertions` |
| 人工门：端点修改/发布决定/触碰 R26.15 在 `allow_human_gate=False` 时抛异常 | `human.py`（`HumanGateRequired`，exit 7）+ `guard_write` 无条件拒绝 R26.15 写入；`run.modify_endpoint=true` 在 bootstrap 触发端点修改门 | 命令 7–8；单测 `test_human_gate_blocks_publish_and_r26_15_writes`、`test_endpoint_modification_config_needs_human_gate`（exit 7） |
| 零漂移自检每轮执行 | bootstrap 阶段 `G_R26_15_ZERO_DRIFT` + `G_PROTECTED_PATHS` | 每次 run 的 gate 账本；命令 13 |

## 3. dry-run 产物哈希（两次运行逐字节相同）

| 产物 | sha256 |
|---|---|
| `dataset_manifest.json` | `5edeee7c7d58aff359f71b0670080118f4a5bafedfbda75683d9ef82fe0611f4` |
| `annotations.json` | `ad99bf3ca499ed1d1f069fe8e8cd78ec4f16ab08ddc668a2c05bf569a2b5defe` |
| `judge.json` | `c00ede808ca24322bebdd116f5556f5997da6d6d4becf36dab4cd01d60bf0ffe` |
| `aggregate.json` | `ea094af600c0c38fc171322b1d26065d5eeaa4e2e9345f2e28ca1999d6d0dc0e` |
| `REPORT.md` | `c963661a1b032588fced48acce49338b4f2b777a17f55e4093a45da8e0dcc3e1` |
| `PIPE_RECEIPT.md` | `58834d51dad0641b00be03bc26ef122a3978f43aefa80bf9e85ccc22088864f0` |

- 第 1 次：`cache={hits:0,misses:12,writes:12}`，budget `calls=12 / tokens 1084 in / 200 out / ¥0`。
- 第 2 次：`cache={hits:12,misses:0,writes:0}`，budget `calls=12 / cache_hits=12 / ¥0`。
- `REPLAY_CHECK.json`：`previous_present=true, identical=true`。

## 4. live 全量运行（真实生成器）

- 运行目录：`05_pipeline/runs/live_full/`
- 规模：**360 题**（published 320 / held_out 40），互异记录 360/360，恒定字段 0，族 360，prompt 最大 1339 tokens
- 确定性抽样：3 题重建摘要一致（`G_DATASET_DETERMINISM=PASS`）
- 21 门：19 PASS + 2 非阻塞 DEGRADED（`G_ANNOTATION_COVERAGE`、`G_JUDGE_COMPARABILITY`，因注入本地故障）
- 降级：3 条 `LOCAL_SERVICE_UNAVAILABLE`（T1/S1/C1 各一），coverage 0.0 如实写入报告
- 主端点：`paired_accuracy_drop = NOT_RUN`（未评分模型答案，不伪造）
- 耗时：19.97s（generate 19.38s）；网络 0；付费 API 0

## 5. 程序化证据

- `GATE_REGISTRY.json`：21 门（id/stage/blocking/repair/exit_code/谓词），`validate_registry` 0 问题。
- `REPAIR_REGISTRY.json`：5 条预注册修复，`max_rounds=2`。
- 每次 run：`gate_ledger.jsonl`、`cost_ledger.jsonl`、`DEGRADED_EVENTS.jsonl`、`pipeline_log.jsonl`、`state.json`、`run_manifest.json`。
- 失败/降级路径持久证据：`runs/_dryrun/publish_gate/`（exit 7）、`runs/_dryrun/publish_packet/`（待签署）、`runs/_dryrun/dryrun_cloud/`、`runs/_drills/disk_drill_run_manifest.json`；`ESCALATED.json` 与 `BUDGET_STOP.json` 由单测实际落盘验证。
- 验收证据汇总：`ACCEPTANCE_EVIDENCE.json`（两次 dry-run 的 cache/budget/hashes/replay/门表）。

## 6. 已知限制（诚实声明）

1. `--dry-run` 的标注是**合成**的，产物显式标记 `synthetic` 且报告写明不得作为证据。
2. 主端点永远 `NOT_RUN`：本流水线不评分模型答案；端点判定仍由 E1/E2 在预注册下执行。
3. live 默认只标注 `T1/S1/C1` 的有界样本（`annotation.sample_instances=4`, `max_calls=24`）；`T2_naturalness` 需要干净的 `V+/V−` 配对，未默认启用。
4. 数据集落盘仍由 t6 `03_build/scripts/build_dataset.py` 负责；本流水线只做内存构建 + 审计 + 报告。
5. 故障演练（`--fault local|cloud|disk`）是**注入**的，用于证明降级分支，不等同真实故障。

## 7. 写入边界核查

- 主项目（`VETT_Cricket_v0.22_R16_Multisource_Dilemmas`）：19:55 之后**0 个文件被修改**（mtime 扫描）。
- `VETT_R28_DIFFICULTY_20261112` 内：只有 `05_pipeline/` 被本任务写入；`03_build/local/**/__pycache__` 最新 mtime 19:42（早于本任务开始 19:55），未被本流水线改动。
- R26.15：165 文件 / 93,346,177 B / 聚合 `343afde4c91d7785f42296074ecea685d5d466260674ab5a8c3bc37323d851bd`，与 t1 冻结备份逐文件一致。

