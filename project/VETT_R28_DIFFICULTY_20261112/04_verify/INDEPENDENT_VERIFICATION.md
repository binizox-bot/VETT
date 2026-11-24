# R28 独立验证报告（t8 / verifier）

- 生成时间：2026-11-12T15:49:38Z
- 总体：**PASS_WITH_CAVEAT**

> 所有数字都由本脚本从原始 artefact 重算；没有把其他 agent 的验证结果作为输入。0 网络、0 付费 API、未读 .secrets、未写 R26.15。

## 0. 逐项结论

| # | 项目 | 状态 | 证据摘要 |
|---|---|:--:|---|
| 1_frozen_chain | 1_frozen_chain | PASS | all_files_ok=True; contract_version=1.2.0; contract_file_sha=dc657f9ccc6848e57a2f068b1d7edf28a80954dbd5673bc5678b09a29e97b275 |
| 2_J_gate_S2 | 2_J_gate_S2 | PASS | content_expected=9b0f4d40272213580bb03e2c60d9ef22eb39abba3723b4ca9383171d9def54b2; J8_verdict=PASS |
| 3_HA10_five | 3_HA10_five | PASS | all_ok=True |
| 4_blind_packets | 4_blind_packets | PASS | packets=64; n_violations=0 |
| 5_J8_dual_channel | 5_J8_dual_channel | PASS | C1_ledger_rows=905; C1_annotation_rows=320; C1_main_ledger_variant=0; C1_main_annotation_variant=0 |
| 6_data_health | 6_data_health | PASS | public_eq_private=True; public_held_disjoint=True; records=320 |
| 7_zero_drift | 7_zero_drift | PASS | r26_15_ok=True; total_aggregate=66e108d8efbe91c6e2d91b973f5cbac3929518386384d8a8bafa26a97b2a0433 |
| 8_build_index_governance | 8_build_index_governance | PASS | schema=vett.r28.t8.build_index_freeze.v1; frozen_at_utc=2026-11-12T15:49:37Z; old_index_sha256=2502aed5a3b3b151b1fc39f258c81f9441e04e7b4a4327dbc8e97edc9f341604; new_index_sha256=dd6de16a4001d414aa3503126f9447c93d571ce645 |
| 9_experiments_E1_E5 | 9_experiments_E1_E5 | PASS | n_pairs=319; expected_pairs=319; drop_pp=0.557297; reported_drop_pp=0.557297 |
| 10_audit_timestamp | 10_audit_timestamp | PASS_WITH_DISCLOSURE | note_present=True; note_status=DISCLOSED_GENERATED_ARTIFACT_ANOMALY; backfill_disclosed=True; current_result_checked_at_utc=2026-11-12T15:37:31Z |
| 11_byte_level_replay | 11_byte_level_replay | PASS_WITH_CAVEAT | exists=True; overall=PASS; passed=10; total=10 |
| 12_old_digest_scan | 12_old_digest_scan | PASS | n_hits=5; n_hardcoded=0 |

## 1. HA10 五项完整证据链

- per_cell_accuracy = **0.514931**（合同值 0.514931）
- marginal_prior = **0.550347**（0.550347）
- lift_over_marginal = **-0.035416**（−0.035416 ≤ 0）
- value_balanced_accuracy = **0.10387**（0.10387 ≤ 0.40）
- permutation_p = **0.146341**（0.146341 > 0.05）
- n_items / n_families = 320 / 320
- reason 字段逐字匹配：“per-cell accuracy conflates marginal skew with leakage”。

## 2. J8 双通道闭合

- C1：生产账本 905 行 / 标注 320 行；变体条目 0 / 0
- C2：raw hits **0**、结构 hits **0**、unauditable **0**
- C3：`t2_choice_template_version` 存在=False，ok=True
- C4：cache hits 71，解析 71，wrong=0，missing=0
- C5：quarantine 35 文件，校验 35，生产引用 0
- 已知局限复现：pretty v9 拦住=True；精确拆分拦住=True；**拆中间绕过=True**（F6 已知上限，不修）

> C2 是辅助通道；“未发现符合形态的变体，不证明不存在”。J8 的 PASS 依据是 C1 + C3 + C4 + C5；C5 只是文本级证据，不作为结构证明。

## 3. 指纹与零漂移治理

- S2：`verify_snapshot --expect S2` exit=0；内容摘要 `9b0f4d40…` 复算一致；J8=PASS，blocking=[]
- R26.15：165 文件 / 93346177 B / 聚合 `343afde4c91d7785f42296074ecea685d5d466260674ab5a8c3bc37323d851bd`；总保护集聚合 `66e108d8efbe91c6e2d91b973f5cbac3929518386384d8a8bafa26a97b2a0433`
- build_index：old `2502aed5a3b3b151b1fc39f258c81f9441e04e7b4a4327dbc8e97edc9f341604` → new `dd6de16a4001d414aa3503126f9447c93d571ce64524df9dc38c24f00c9ac0ee`；items=360；逐条 record 0 mismatch；e1 gold binding 640 条 0 mismatch；dual pin = file + header `9f752e048a8024b9493974a51f6cec87640a0c4fb9196ce9a84f25d4ade1bf55`
- **caveat**：Cannot byte-diff 2502aed5 vs dd6de16a because the t6 replay directory was removed. The claim is supported by (i) t6 determinism old hash, (ii) 640 e1 prompt/gold bindings, (iii) current item->private_gold binding; it is not a byte-level reconstruction.

> `protocol_verify_result.json` 是派生结果、不在 7 件冻结集中；t8 不以它判漂移。审计时间戳回填已在 `PROTOCOL_VERIFY_RERUN_NOTE.json` 披露。

## 4. 实验复核（E1–E5）

- E1 STRICT pairs=319；drop=0.557297pp（报告 0.557297）；item bootstrap CI [-0.801115, 1.846047]（报告 [-0.801115, 1.846047]）；方向 {'hard_more': 47, 'control_more': 69, 'tied': 203}；record-exact 5/638
- E2：{'0': 59.375, '1': 62.6736, '2': 60.9375}（非单调）；HYP_R28_DOSE=REJECTED
- E3：16 格独立重算与报告一致=True；H3_supported=False
- E4：substitution 0.5（n=32）；introduced 0.125；order stability 0.125；flip⁺ 0.525 vs random floor 0.875；S12=True
- E5：UNTESTED（只有 1 个本地模型；零付费硬约束）

## 5. 数据健康（独立重算）

- 互异记录 320/320；恒定字段 []
- ledger 非零 {'ledger.BYE': 96, 'ledger.LEG_BYE': 78, 'ledger.PENALTY': 153}；status {'NO_BALL': 100, 'LEGAL': 166, 'WIDE': 53, 'DEAD_REBALL': 1}；dismissal {'HIT_BALL_TWICE': 50, 'OBSTRUCTING_FIELD': 50, 'RUN_OUT': 86, 'NONE': 124, 'BOWLED': 2, 'LBW': 2, 'CAUGHT': 2, 'STUMPED': 4}；合法 dismissal 10 + DEAD 1
- 证书缺失 0；solver 重推失败 0；双渲染失败 0；rule_path 违规 0；presentation_only 564
- build_index 360 项、record 绑定失败 0；当前 sha `dd6de16a4001d414aa3503126f9447c93d571ce64524df9dc38c24f00c9ac0ee`

## 6. 发布阻断项清单

- **PASS_WITH_DISCLOSURE** `10_audit_timestamp`：checked_at was backfilled once and is disclosed in PROTOCOL_VERIFY_RERUN_NOTE.json; current result 22/22
- **PASS_WITH_CAVEAT** `11_byte_level_replay`：t20 summary 10/10; exact documented command is 9/10 on vanilla Windows GBK and 10/10 with PYTHONUTF8=1

### 补充：t20 单命令重放的复现性

- t20 记录：10/10 PASS。
- 我独立执行文档命令：vanilla Windows GBK 控制台 **9/10 FAIL**（D0 的 subprocess 文本解码 UnicodeDecodeError）；设置 `PYTHONUTF8=1` 后 **10/10 PASS**。
- 最小修复：在 `run_closed_loop_verification.py` 的 subprocess 调用中显式 `encoding='utf-8'`，或在 README/单命令里写死 `PYTHONUTF8=1`。

> 本报告不产生人工金标；E 阶段人工双标仍未执行，论文必须把该限制列为发表阻断项（见 t24 kit）。

---

## 补充（append-only）：caveat 1 已闭合 — t20 UTF-8 supplemental 增量复核

- **记录时间**：2026-11-12T15:55Z（本补充不修改上方原 t8 结论、原生成时间与原有证据；t8 仍为 `PASS_WITH_CAVEAT`）。
- **pre 归档**：`04_verify/t20_closed_loop/archive_prefix_utf8/CLOSED_LOOP_VERIFICATION.json` = `87031999b1e9411afa9593445cbf51e291976dbe7828fa97fad4a78ba62125fe`；`.md` = `37bde9afbcbd7025b208efe60fe95887f31e9c6ca116c8972d99c0219aaeb5bb`（原样保留）。
- **post 实测**（逐文件 sha256，已核对）：
  - `CLOSED_LOOP_VERIFICATION.json` = `7b5b5fa90952d4db6878b4be607ae9eda273213579e4da2f36b1b7c26ff7d020`
  - `CLOSED_LOOP_VERIFICATION.md` = `d5d0f0369d6f70365980abf55da96fbb48be6c11099809c0c725b379c9cd2b7c`
  - `T20_CLOSURE.md` = `8750506002eb7b4a803e9c8d75560b330850267e9f45065f0b9495c82e6b6392`
  - `PIPELINE_VERIFICATION.json` = `da6ad296e84b179a7548adb30be31decc8fdbf357b4ed8c24e171d0fc67c98be`
  - `README.md` = `6ef87e91a9d3cab49d506e3536e304d65001fabef583cc23ed1755883195a00a`
  - `postfix_gbk_console.log` = `c89b9c5c112fe9922d5530cb4e6540da34156cfd14e5cf473e087d269e6a2a98`
- **D0 复核**：post 报告 D0 = PASS，`protocol_verify 22/22` + 盲包 64/0 + 四条注入全阻断；postfix log 完整 10/10。**没有 `UnicodeDecodeError`**。
- **我自己在 GBK 环境复跑**：`chcp 936`，未设 `PYTHONUTF8` / `PYTHONIOENCODING` / `PYTHONLEGACYWINDOWSSTDIO`；`D:\Conda\python.exe 3.14.7`，`05_pipeline/verify/run_closed_loop_verification.py --config 05_pipeline/r28.toml` → **10/10 PASS、exit 0、19.27s、D0 无解码异常**。命令行父进程没有设置任何 UTF-8 前置。
- **结论**：原 caveat 1 的“Windows GBK 下 9/10”已由代码修复闭合，**单命令在 vanilla Windows GBK 控制台无环境前置可复现 10/10**。t8 总体仍为 `PASS_WITH_CAVEAT`，但 release blocker 只剩 caveat 2（时间戳回填，已披露、不再改回；属处置完毕状态）。
- **未修改**：pre 归档、原 t8 时间戳、原 t8 判定与证据；本补充仅追加。

