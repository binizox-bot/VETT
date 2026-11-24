
import json
from pathlib import Path
from datetime import datetime
p = Path("reports/HOURLY_VERIFY.json")
d = json.loads(p.read_text(encoding="utf-8"))
d["new_segment_hour2"] = {
  "hourly_file": "reports/HOURLY_20261119_022447.md",
  "segment_started_at": "2026-11-19T00:24:45+08:00",
  "verified_at": datetime.now().astimezone().isoformat(timespec="seconds"),
  "results_total": 2219, "probe_cursor": 32,
  "note": "second hourly of the new segment; 02:24:47, 3601s after 01:24:46"
}
p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
a = Path("ACCEPTANCE_V2.md")
t = a.read_text(encoding="utf-8")
if "新段连续 2 小时" not in t:
    t += """

## M. 新段连续 2 小时

- 新段 00:24:45 起；01:24:46 与 02:24:47 两份小时报，间隔 3601 秒。
- 02:24 时结果 2,219；P_field_sweep 已到 probe_cursor 32。
- 8 小时里程碑仍为 08:24:45；08:00 阶段报告落在本段内。
"""
    a.write_text(t, encoding="utf-8")
print("recorded")
