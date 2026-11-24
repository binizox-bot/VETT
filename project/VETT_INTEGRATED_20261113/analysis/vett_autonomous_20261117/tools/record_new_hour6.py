
import json
from pathlib import Path
from datetime import datetime
p = Path("reports/HOURLY_VERIFY.json")
d = json.loads(p.read_text(encoding="utf-8"))
d["new_segment_hour6"] = {"hourly_file": "reports/HOURLY_20261119_062457.md",
  "segment_started_at": "2026-11-19T00:24:45+08:00",
  "verified_at": datetime.now().astimezone().isoformat(timespec="seconds"),
  "results_total": 3073, "probe_cursor": 124,
  "note": "sixth hourly of new segment; 06:24:57, 3603s after 05:24:54"}
p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
a = Path("ACCEPTANCE_V2.md")
t = a.read_text(encoding="utf-8")
if "新段连续 6 小时" not in t:
    t += """

## Q. 新段连续 6 小时

- 00:24:45 起；连续七份小时报至 06:24:57。
- 06:24 时结果 3,073；P_field_sweep 到 probe_cursor 124。
- 8 小时里程碑 08:24:45；08:00 阶段报告约 1.5 小时后触发。
"""
    a.write_text(t, encoding="utf-8")
print("recorded")
