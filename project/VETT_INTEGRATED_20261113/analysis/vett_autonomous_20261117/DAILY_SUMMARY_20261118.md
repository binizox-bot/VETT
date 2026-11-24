# VETT 执行汇总（2026-11-18 14:50 → 2026-11-19 09:10）

## 0. 结论

- 8 小时无人值守验收在 2026-11-19 08:24:45 达成，08:00 阶段报告已生成且推理继续。
- 运行在 09:09:18 后随主机重启（boot 09:10:15）终止，全程 8h44m；不是代码异常。
- 当前状态已修正为 stopped（stop_reason=host_reboot_20261119_0910），可 resume。

## 1. 关键数字

- 结果：3502；attempts：3453；批次：149；任务：3507
- 外部 API：0
- 小时报：14 份；08:00 阶段报告：1 份
- sweep_cursor：360/360；probe_cursor：172/360
- 人工复核：7 条记录 pending_human_review

## 2. 时间线

- 2026-11-18 14:50:24 启动旧连续段。
- 19:13:30 旧段死亡：主机休眠 + Ollama 停止；旧段 4h23m，不计入 8h。
- 2026-11-19 00:24:45 新连续段重启（keep-awake + Ollama watchdog）。
- 08:00 生成 STAGE_20261119_0800.md；08:24:45 达成 8 小时。
- 09:09:18 最后结果；09:10:15 主机重启，进程终止。

## 3. 批次结构

- S_coverage_sweep: 88 批，平均准确率 0.554
- P_field_sweep: 43 批，平均准确率 0.503
- T1_baseline_o: 4 批，平均准确率 0.9375
- T5_hard_fulltext: 3 批，平均准确率 0.0
- T3_matched_deletion: 3 批，平均准确率 0.1296
- T2_hard_excerpt: 2 批，平均准确率 0.8333
- C_adjudication: 2 批，平均准确率 0.95
- T4_full_table: 1 批，平均准确率 0.1938
- B_cross_innings: 1 批，平均准确率 0.0
- B2_matched_control: 1 批，平均准确率 0.0
- A_field_probe: 1 批，平均准确率 0.9167

- B001–B010：历史基线/摘录/删除/整表。
- B011–B015：v2 续跑与旧模板。
- B016–B106：S_coverage_sweep，1,959 results，cursor 360。
- B107–B149：P_field_sweep，probe_cursor 172。

## 4. 研究结论

- 覆盖组同根配对：E +75、OI +16（根依赖）、WI +3。
- E 的 10 个反例是 wickets 绑定/空答，不是缺证。
- B002/B005：runs 全对，wickets 4/6、2/3。
- B003：O 0/6、WI 0/6、OI 3/6；OI 收益未被长度匹配 NEI 复现，标为未定。
- B004：43 字段含两局，目标四格 7/12；全字段 25/129，可核实子集 24/105。
- B007/B009：加入英文数字词后 B009 6/6 有明确总分句，0% 不是缺证。
- 分支 C：C_change 12/24、C_maintain 23/24、C_no_notice 24/24；错误集中在改判后的 A−1/B+1 传播。
- P 字段探针前 266 条：runs 51.1%、wickets 44.9%、both 格 49.4%。

## 5. P 字段探针（当前累计）

- probe_both: 513 任务，任务准确率 0.4444，格准确率 0.5166
- probe_runs: 516 任务，任务准确率 0.5039，格准确率 0.5039
- probe_wickets: 514 任务，任务准确率 0.4689，格准确率 0.4689

## 6. 可靠性修复

- v2 任务身份、task_key_map、attempts 生命周期（sent/responded/persisted/accepted/uncertain）。
- 心跳独立于长请求；不再因单请求超过 150 秒判死。
- 状态区分 workflow/batch/task；stale running 已修正。
- S→P 接续修复：S 无合格任务时 cursor 置 360 并回退 P。
- Windows keep-awake（SetThreadExecutionState）与 Ollama watchdog。
- 主机重启无法由进程内机制防止；如需跨重启，需要 Windows 计划任务/服务自启动。

## 7. 验收

- 生产 1 小时：通过。
- 连续 2/3 小时：通过。
- 8 小时：通过（新段 00:24:45–08:24:45）。
- 08:00 阶段报告：通过，且推理继续。
- 48 小时有效队列：未达到。
- exactly-once：不宣称；结果持久化一次，尝试可多次。

## 8. 产物

- ACCEPTANCE_V2.md、MILESTONE_8H.md、SCIENCE_CORRECTIONS.md、BRANCH_C.md
- COVERAGE_GROUP/PAIRED/COUNTEREXAMPLES、PROBE_SWEEP_PARTIAL
- records/INDEX.json（7 条）、data_patches/（5 个）
- reports/HOURLY_*.md（{len(hourly)} 份）、STAGE_20261119_0800.md
- INCIDENT_20261118_1913.md、INCIDENT_20261119_0910.md

## 9. 未完成与下一阶段建议

1. 人工复核 7 条记录。
2. 48 小时有效队列仍有缺口；当前估算 10–18 小时不同任务。
3. 主机重启后自动恢复：需要 Windows 计划任务/服务，而不是仅 keep-awake。
4. 规划仍是 rule_template，未接通 DSH 自动分析。
5. 如继续 P_field_sweep：vettctl.py start，从 probe_cursor 172 继续。
