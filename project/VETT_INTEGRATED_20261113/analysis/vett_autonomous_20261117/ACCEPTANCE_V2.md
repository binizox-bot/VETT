
# 验收口径修正（v2）

原“12 项全部 PASS”过于笼统。现拆为三类。

## A. 已通过短时实际验证

- 10 个历史批次（B001–B010）已评分；v2 后 B011–B015 继续评分。
- 受控 stop/start：pids 清空、claimed 退回 queued、不再派发。
- 恢复：claimed 任务写 uncertain 后重跑；results 只保留一条。
- 脱离终端：启动调用返回后仍落盘。
- 单 worker：PowerShell 计数 1/1。
- 外部 API 0。

## B. 已通过隔离测试

- 计时器阈值：tests/test_timers.py 7/7。
- v2 freeze：tests/test_v2_freeze.py，18 个 A 分支任务、身份列、task_key_map 全部写入。
- 离线审计：B002–B009 原文/金标复核，见 SCIENCE_AUDIT 与 AUDIT_FOLLOWUP。
- 去重：v2 任务身份与 task_key_map 能阻止旧任务整体重跑。

## C. 尚待长时间运行验证

- 连续 8 小时无人值守：尚未完成。此前 9 分 30 秒运行不算整夜验收。
- 生产环境连续 1 小时快照：尚未完成。阈值测试不等于生产已连续跑满一小时。
- 08:00 阶段报告：下一次 08:00 才触发；当前 14:50 启动。
- 48 小时有效队列：未达到，见 RUN_PLAN_48H.md。
- 分支 C：B019+B022 共 8 事件、72 任务；C_change 12/24，C_maintain 23/24，C_no_notice 24/24。错误集中在正式改判后的 A−1/B+1 传播。
- 底层推理 exactly-once：不宣称；attempts 记录 sent/responded/persisted/accepted 与 uncertain。

## D. 当前运行

- 启动：2026-11-18 14:50:24。
- 已启用 coverage sweep；sweep_cursor 从 0 开始，360 个 unit。
- 每小时写 HOURLY_<stamp>.md；08:00 写 STAGE_<date>_0800.md；两者都不停止推理。
- 状态报告区分 workflow_state / batch_state / task_state；stopped 时显示 interrupted_batch，不显示 running。

## E. 边界

- 人工复核 0；所有证据状态保持 pending_human_review。
- 规则模板驱动；planning_mode=rule_template。未接通 DSH 自动分析，不宣称自主提出研究假设。
- 外部 API 0；仅 127.0.0.1:11434。


## F. 首个小时报（生产验证）

- 文件：reports/HOURLY_20261118_155025.md
- 触发：14:50:24 启动，15:50:25 写盘，间隔 3601 秒。
- 1 小时：591 results / 541 attempts / 3 uncertain / 0 exceptions。
- 耗时拆分：load 3,012,266.9 ms；inference 438,800.8 ms；scoring 171.2 ms；planning 1,884.6 ms；waiting 估计 3,161,143.4 ms。
- 结论：Ollama 模型加载占首小时约 84%，是吞吐主瓶颈；推理本身只占约 12%。


## G. 覆盖组

- S_coverage_sweep 426 results：E 0.9537、OI 0.7407、WI 0.6875、O 0.5458。
- 与诊断组（0.6816）分开报告；不把覆盖组速率写成全池错误率。
- 文件：reports/COVERAGE_GROUP.md / .json。

## H. 字段探针覆盖

- P_field_sweep 已启用：360 unit × 3 变体 × 3 模型 = 3,240 任务；S + P 约 7,560 个不同任务位，估算 12.8 小时。
- 覆盖 8 小时里程碑，但仍不足以覆盖 48 小时。


## I. 连续 2 小时验证

- 15:50:25 与 16:50:26 连续两次小时报，间隔均为 3601 秒。
- 2 小时：851 results / 802 attempts / 4 uncertain / 0 exceptions。
- 耗时：load 6,157,691.8 ms；inference 627,030.1 ms；scoring 257.3 ms；planning 4,462.5 ms；waiting 估计 6,570,950.1 ms。
- 第 1 小时 591 条，第 2 小时 260 条；后半段全文本 O 提示更长，吞吐下降。
- 8 小时里程碑仍未到。


## J. 连续 3 小时验证

- 14:50:24 启动；15:50:25、16:50:26、17:50:27 连续三份小时报，间隔均 3601 秒。
- 3 小时：1,091 results / 1,042 attempts / 4 uncertain / 0 exceptions。
- load 9,385,650.3 ms；inference 781,754.1 ms；scoring 336.9 ms；planning 7,243.3 ms。
- 第 3 小时 240 条，延续全文本 O 的低吞吐；load 仍占约 86%。


## K. 夜间中断与重启

- 旧连续段 2026-11-18 14:50:24–19:13:30：4h23m，5 份小时报；**8 小时未达成**。
- 死因：主机空闲休眠导致 supervisor/worker 停止，同时 Ollama 服务停止；日志无异常，主机未重启。
- 修复：SetThreadExecutionState keep-awake；Ollama 每分钟 watchdog；新 segment_started_at。
- 新连续段：2026-11-19 00:24:45 起，supervisor 12068 / worker 26892；8 小时里程碑 **08:24:45**，08:00 阶段报告落在本段内。


## L. S→P 接续（2026-11-19 02:05）

- S_coverage_sweep 到 cursor 350 时剩余 unit 已无合格任务；旧逻辑仍返回 S，导致 no_eligible_tasks 并进入 idle。
- 修复：S 模板无任务时把 sweep_cursor 置 360，并回退 P_field_sweep。
- 结果：B107 P_field_sweep 自动冻结，36 任务，probe_cursor 4；S 共跑到 B106。
- 01:24:46 新段第一份小时报已验证（3601.2 秒）；8 小时里程碑仍为 08:24:45。


## M. 新段连续 2 小时

- 新段 00:24:45 起；01:24:46 与 02:24:47 两份小时报，间隔 3601 秒。
- 02:24 时结果 2,219；P_field_sweep 已到 probe_cursor 32。
- 8 小时里程碑仍为 08:24:45；08:00 阶段报告落在本段内。


## N. 新段连续 3 小时

- 00:24:45 起；00:24:45、01:24:46、02:24:47、03:24:49 连续四份小时报。
- 03:24 时结果 2,550；P_field_sweep 到 probe_cursor 68。
- 8 小时里程碑 08:24:45；08:00 阶段报告仍落在本段内。


## O. 新段连续 4 小时

- 00:24:45 起；00:24:45 / 01:24:46 / 02:24:47 / 03:24:49 / 04:24:51 连续五份小时报。
- 04:24 时结果 2,739；P_field_sweep 到 probe_cursor 88。
- 8 小时里程碑 08:24:45；08:00 阶段报告仍在本段内。


## P. 新段连续 5 小时

- 00:24:45 起；00:24:45 / 01:24:46 / 02:24:47 / 03:24:49 / 04:24:51 / 05:24:54 连续六份小时报。
- 05:24 时结果 2,909；P_field_sweep 到 probe_cursor 108。
- 8 小时里程碑 08:24:45；08:00 阶段报告将在约 2.5 小时后触发。


## Q. 新段连续 6 小时

- 00:24:45 起；连续七份小时报至 06:24:57。
- 06:24 时结果 3,073；P_field_sweep 到 probe_cursor 124。
- 8 小时里程碑 08:24:45；08:00 阶段报告约 1.5 小时后触发。


## R. 新段连续 7 小时

- 00:24:45 起；连续八份小时报至 07:24:59。
- 07:24 时结果 3,233；P_field_sweep 到 probe_cursor 144。
- 08:00 阶段报告约 35 分钟后触发；8 小时里程碑 08:24:45。


## S. 8 小时里程碑通过

- 新段 2026-11-19 00:24:45 起，08:24:45 达成 8 小时；最后结果 08:24:54。
- 9 份小时报连续；08:00 阶段报告 STAGE_20261119_0800.md 已生成，推理继续。
- 3,389 results / 3,340 attempts / 4 uncertain / 0 exceptions；external API 0。
- 48 小时有效队列仍未达到；人工复核仍 pending。


## T. 主机重启终止

- 8 小时里程碑已于 08:24:45 通过；09:09:18 最后结果，09:10:15 主机重启，进程终止。
- 全程 8h44m；不是代码异常。状态已修正为 stopped（host_reboot_20261119_0910）。
- 主机重启无法由 keep-awake 防止；跨重启自动恢复需 Windows 计划任务/服务。
