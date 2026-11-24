
import json, sqlite3, urllib.request
c = sqlite3.connect("state/workflow.db"); c.row_factory = sqlite3.Row
new = c.execute("SELECT model,load_ms,inference_ms,duration_ms,created_at FROM results "
                "WHERE created_at>='2026-11-19T15:42:34' ORDER BY created_at").fetchall()
print("new_results", len(new))
from collections import defaultdict
agg = defaultdict(lambda: {"n":0,"load":0,"big":0,"small":0,"inf":0})
for r in new:
    a = agg[r["model"]]; a["n"] += 1; a["load"] += r["load_ms"]; a["inf"] += r["inference_ms"]
    if r["load_ms"] > 1000: a["big"] += 1
    if r["load_ms"] < 100: a["small"] += 1
for k, a in agg.items():
    print(k, {"n": a["n"], "load_avg": round(a["load"]/a["n"],1), "load_gt1s": a["big"], "load_lt100ms": a["small"], "inf_avg": round(a["inf"]/a["n"],1)})
print("sequence", [(r["model"].split(":")[0], round(r["load_ms"],1)) for r in new[-20:]])
try:
    print("ps", urllib.request.urlopen("http://127.0.0.1:11434/api/ps", timeout=3).read().decode())
except Exception as e:
    print("ps_err", e)
print("queue", {r["status"]: r["n"] for r in c.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")})
