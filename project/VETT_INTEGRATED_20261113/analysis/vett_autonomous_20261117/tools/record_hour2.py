
import json
from pathlib import Path
from datetime import datetime
p = Path("reports/HOURLY_VERIFY.json")
d = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
d["second_hour"] = {
  "hourly_file": "reports/HOURLY_20261118_165026.md",
  "verified_at": datetime.now().astimezone().isoformat(timespec="seconds"),
  "run_elapsed_seconds": 7202.7, "results": 851, "attempts": 802, "uncertain": 4, "exceptions": 0,
  "load_ms": 6157691.8, "inference_ms": 627030.1, "scoring_ms": 257.3,
  "planning_ms": 4462.5, "waiting_ms_est": 6570950.1,
  "note": "second production hourly fired at 16:50:26; two consecutive 3600s intervals"
}
d["throughput"] = {"hour1_results": 591, "hour2_results": 260, "two_hour_results": 851,
                   "two_hour_rate_per_hour": 425.5,
                   "note": "hour2 slower because later sweep units use full-text O and longer prompts; load still dominates"}
p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")

a = Path("ACCEPTANCE_V2.md")
t = a.read_text(encoding="utf-8")
if "连续 2 小时" not in t:
    t += """

## I. 连续 2 小时验证

- 15:50:25 与 16:50:26 连续两次小时报，间隔均为 3601 秒。
- 2 小时：851 results / 802 attempts / 4 uncertain / 0 exceptions。
- 耗时：load 6,157,691.8 ms；inference 627,030.1 ms；scoring 257.3 ms；planning 4,462.5 ms；waiting 估计 6,570,950.1 ms。
- 第 1 小时 591 条，第 2 小时 260 条；后半段全文本 O 提示更长，吞吐下降。
- 8 小时里程碑仍未到。
"""
    a.write_text(t, encoding="utf-8")

r = Path("RUN_PLAN_48H.md")
x = r.read_text(encoding="utf-8")
if "两小时实测" not in x:
    x += """

## 6. 两小时实测修正

- 第 1 小时 591 条，第 2 小时 260 条，两小时合计 851 条，平均 425.5 条/小时。
- 后段全文本 O 的提示更长，吞吐低于首小时。
- 按 425 条/小时估算：S 剩余 + P 3,240 条约需 10–18 小时，仍足以覆盖 22:50 的 8 小时里程碑。
- 48 小时仍不足；该估算会随条件组合变化。
"""
    r.write_text(x, encoding="utf-8")
print("recorded 2h")
