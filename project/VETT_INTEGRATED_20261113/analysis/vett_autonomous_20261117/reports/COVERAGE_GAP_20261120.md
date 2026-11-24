# 覆盖缺口（2026-11-20 09:07）

- S_coverage_sweep: 360/360 处理完毕。
- P_field_sweep: 357 个单元有完整 probe 三元组；3 个单元无法构建 O 全文变体。
- 未覆盖单元：match_0004 inn1、match_0004 inn2、match_0066 inn2。
- 原因：variant_unavailable，没有可用的 O 全文（commentary）变体；不是调度失败。
- 已存在的相关 S/A 结果保留；不生成伪任务，不重复调用。
- 当前 5,175 个逻辑任务全部 done，failed=0；因此进入 idle_no_valid_tasks。
- 监控保持：supervisor/worker/watchdog 均存活，小时报和 08:00 阶段报告继续写快照。
