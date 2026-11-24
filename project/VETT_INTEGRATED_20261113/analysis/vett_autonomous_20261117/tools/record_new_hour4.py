
import json
from pathlib import Path
from datetime import datetime
p = Path("reports/HOURLY_VERIFY.json")
d = json.loads(p.read_text(encoding="utf-8"))
d["new_segment_hour4"] = {"hourly_file": "reports/HOURLY_20261119_042451.md",
  "segment_started_at": "2026-11-19T00:24:45+08:00",
  "verified_at": datetime.now().astimezone().isoformat(timespec="seconds"),
  "results_total": 2739, "probe_cursor": 88,
  "note": "fourth hourly of new segment; 04:24:51, 3602s after 03:24:49"}
p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
a = Path("ACCEPTANCE_V2.md")
t = a.read_text(encoding="utf-8")
if "新段连续 4 小时" not in t:
    t += """

## O. 新段连续 4 小时

- 00:24:45 起；00:24:45 / 01:24:46 / 02:24:47 / 03:24:49 / 04:24:51 连续五份小时报。
- 04:24 时结果 2,739；P_field_sweep 到 probe_cursor 88。
- 8 小时里程碑 08:24:45；08:00 阶段报告仍在本段内。
"""
    a.write_text(t, encoding="utf-8")
print("recorded")
