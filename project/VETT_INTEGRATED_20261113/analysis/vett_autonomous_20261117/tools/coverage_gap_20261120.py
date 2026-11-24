
import json, sys
from pathlib import Path
sys.path.insert(0, ".")
import vettlib as V
c = V.init_db()
units = [("match_0004", 1), ("match_0004", 2), ("match_0066", 2)]
V.meta_set(c, "probe_cursor", "360")
V.event("coverage_exhausted", {
    "already_covered_units": 357,
    "unavailable_units": [{"match": m, "innings": i} for m, i in units],
    "reason": "variant_unavailable: no O full-text variant",
    "note": "all authorized S/P tasks are done; no new tasks can be built"
}, c)
c.commit()
gap = "# 覆盖缺口（2026-11-20 09:07）\n\n"
gap += "- S_coverage_sweep: 360/360 处理完毕。\n"
gap += "- P_field_sweep: 357 个单元有完整 probe 三元组；3 个单元无法构建 O 全文变体。\n"
gap += "- 未覆盖单元：match_0004 inn1、match_0004 inn2、match_0066 inn2。\n"
gap += "- 原因：variant_unavailable，没有可用的 O 全文（commentary）变体；不是调度失败。\n"
gap += "- 已存在的相关 S/A 结果保留；不生成伪任务，不重复调用。\n"
gap += "- 当前 5,175 个逻辑任务全部 done，failed=0；因此进入 idle_no_valid_tasks。\n"
gap += "- 监控保持：supervisor/worker/watchdog 均存活，小时报和 08:00 阶段报告继续写快照。\n"
Path("reports/COVERAGE_GAP_20261120.md").write_text(gap, encoding="utf-8")
st = "# 状态快照（2026-11-20 09:07）\n\n"
st += "- workflow: idle_no_valid_tasks；最后结果 2026-11-19T21:20:34+08:00。\n"
st += "- results 5,175；attempts 5,129；uncertain 8；failed 0；queue done 5,175。\n"
st += "- batches 197；P 90 批；probe_cursor 360/360（3 个 variant_unavailable）。\n"
st += "- 8h 快照：HOURLY_20261120_044108.md（8.0h）。\n"
st += "- 08:00 阶段报告：STAGE_20261120_0800.md（idle 快照，任务未停）。\n"
st += "- 09:05:05 主机重启；09:07 watchdog 自动恢复：supervisor 19680 / worker 22108。\n"
st += "- watchdog 22292；单实例 1/1/1；external API 0。\n"
Path("reports/STATUS_20261120_0907.md").write_text(st, encoding="utf-8")
print("written")
