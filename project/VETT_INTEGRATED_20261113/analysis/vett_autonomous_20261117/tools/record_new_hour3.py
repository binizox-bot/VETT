
import json
from pathlib import Path
from datetime import datetime
p = Path("reports/HOURLY_VERIFY.json")
d = json.loads(p.read_text(encoding="utf-8"))
d["new_segment_hour3"] = {"hourly_file": "reports/HOURLY_20261119_032449.md",
  "segment_started_at": "2026-11-19T00:24:45+08:00",
  "verified_at": datetime.now().astimezone().isoformat(timespec="seconds"),
  "results_total": 2550, "probe_cursor": 68,
  "note": "third hourly of new segment; 03:24:49, 3602s after 02:24:47"}
p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
a = Path("ACCEPTANCE_V2.md")
t = a.read_text(encoding="utf-8")
if "新段连续 3 小时" not in t:
    t += """

## N. 新段连续 3 小时

- 00:24:45 起；00:24:45、01:24:46、02:24:47、03:24:49 连续四份小时报。
- 03:24 时结果 2,550；P_field_sweep 到 probe_cursor 68。
- 8 小时里程碑 08:24:45；08:00 阶段报告仍落在本段内。
"""
    a.write_text(t, encoding="utf-8")
print("recorded")
