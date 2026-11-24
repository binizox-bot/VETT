
import json
from pathlib import Path
from datetime import datetime
p = Path("reports/HOURLY_VERIFY.json")
d = json.loads(p.read_text(encoding="utf-8"))
d["new_segment_hour7"] = {"hourly_file": "reports/HOURLY_20261119_072459.md",
  "segment_started_at": "2026-11-19T00:24:45+08:00",
  "verified_at": datetime.now().astimezone().isoformat(timespec="seconds"),
  "results_total": 3233, "probe_cursor": 144,
  "note": "seventh hourly of new segment; 07:24:59, 3602s after 06:24:57"}
p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
a = Path("ACCEPTANCE_V2.md")
t = a.read_text(encoding="utf-8")
if "新段连续 7 小时" not in t:
    t += """

## R. 新段连续 7 小时

- 00:24:45 起；连续八份小时报至 07:24:59。
- 07:24 时结果 3,233；P_field_sweep 到 probe_cursor 144。
- 08:00 阶段报告约 35 分钟后触发；8 小时里程碑 08:24:45。
"""
    a.write_text(t, encoding="utf-8")
print("recorded")
