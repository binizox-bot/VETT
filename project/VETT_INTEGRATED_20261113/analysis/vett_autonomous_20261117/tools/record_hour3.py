
import json
from pathlib import Path
from datetime import datetime
p = Path("reports/HOURLY_VERIFY.json")
d = json.loads(p.read_text(encoding="utf-8"))
d["third_hour"] = {"hourly_file": "reports/HOURLY_20261118_175027.md",
  "verified_at": datetime.now().astimezone().isoformat(timespec="seconds"),
  "run_elapsed_seconds": 10803.5, "results": 1091, "attempts": 1042, "uncertain": 4, "exceptions": 0,
  "load_ms": 9385650.3, "inference_ms": 781754.1, "scoring_ms": 336.9,
  "planning_ms": 7243.3, "waiting_ms_est": 10014165.7,
  "note": "third production hourly fired at 17:50:27; three consecutive 3601s intervals"}
p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
a = Path("ACCEPTANCE_V2.md")
t = a.read_text(encoding="utf-8")
if "连续 3 小时" not in t:
    t += """

## J. 连续 3 小时验证

- 14:50:24 启动；15:50:25、16:50:26、17:50:27 连续三份小时报，间隔均 3601 秒。
- 3 小时：1,091 results / 1,042 attempts / 4 uncertain / 0 exceptions。
- load 9,385,650.3 ms；inference 781,754.1 ms；scoring 336.9 ms；planning 7,243.3 ms。
- 第 3 小时 240 条，延续全文本 O 的低吞吐；load 仍占约 86%。
"""
    a.write_text(t, encoding="utf-8")
print("third hour recorded")
