
import json
from pathlib import Path
from datetime import datetime
p = Path("reports/HOURLY_VERIFY.json")
d = json.loads(p.read_text(encoding="utf-8"))
d["new_segment_hour1"] = {
  "hourly_file": "reports/HOURLY_20261119_012446.md",
  "segment_started_at": "2026-11-19T00:24:45+08:00",
  "run_elapsed_seconds": 3601.2, "results_total": 1808, "attempts": 1759, "uncertain": 4, "exceptions": 0,
  "note": "first hourly of the new segment; totals include legacy results, segment delta is 400"
}
p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
a = Path("ACCEPTANCE_V2.md")
t = a.read_text(encoding="utf-8")
if "## L. S→P 接续" not in t:
    t += """

## L. S→P 接续（2026-11-19 02:05）

- S_coverage_sweep 到 cursor 350 时剩余 unit 已无合格任务；旧逻辑仍返回 S，导致 no_eligible_tasks 并进入 idle。
- 修复：S 模板无任务时把 sweep_cursor 置 360，并回退 P_field_sweep。
- 结果：B107 P_field_sweep 自动冻结，36 任务，probe_cursor 4；S 共跑到 B106。
- 01:24:46 新段第一份小时报已验证（3601.2 秒）；8 小时里程碑仍为 08:24:45。
"""
    a.write_text(t, encoding="utf-8")
r = Path("RUN_PLAN_48H.md")
x = r.read_text(encoding="utf-8")
if "S→P 实际接续" not in x:
    x += """

## 7. S→P 实际接续

- S_coverage_sweep 于 2026-11-19 02:05 到 B106，累计 1,959 results，cursor 置 360。
- P_field_sweep 于 B107 自动接续，36 任务/批，probe_cursor 4。
- 计划中 P 的 3,240 任务位现在开始兑现；按每分钟约 6 条估算可覆盖到 08:24 之后。
"""
    r.write_text(x, encoding="utf-8")
print("recorded")
