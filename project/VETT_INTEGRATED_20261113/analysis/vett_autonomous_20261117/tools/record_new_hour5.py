
import json
from pathlib import Path
from datetime import datetime
p = Path("reports/HOURLY_VERIFY.json")
d = json.loads(p.read_text(encoding="utf-8"))
d["new_segment_hour5"] = {"hourly_file": "reports/HOURLY_20261119_052454.md",
  "segment_started_at": "2026-11-19T00:24:45+08:00",
  "verified_at": datetime.now().astimezone().isoformat(timespec="seconds"),
  "results_total": 2909, "probe_cursor": 108,
  "note": "fifth hourly of new segment; 05:24:54, 3603s after 04:24:51"}
p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
a = Path("ACCEPTANCE_V2.md")
t = a.read_text(encoding="utf-8")
if "新段连续 5 小时" not in t:
    t += """

## P. 新段连续 5 小时

- 00:24:45 起；00:24:45 / 01:24:46 / 02:24:47 / 03:24:49 / 04:24:51 / 05:24:54 连续六份小时报。
- 05:24 时结果 2,909；P_field_sweep 到 probe_cursor 108。
- 8 小时里程碑 08:24:45；08:00 阶段报告将在约 2.5 小时后触发。
"""
    a.write_text(t, encoding="utf-8")
print("recorded")
