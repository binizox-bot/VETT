
import sys, json
sys.path.insert(0, ".")
import vettlib as V, planner
con = V.init_db()
print("cursor", V.meta_get(con,"sweep_cursor","0"), "units", len(planner.sweep_units()))
design, tasks, rejects = planner.build_sweep(con, {"rationale":"test"})
print("built", len(tasks), "rejects", len(rejects), "next", design.get("sweep_next_cursor"))
from collections import Counter
print("conds", Counter(t["cond"] for t in tasks))
print("positions", design["positions"][:6])
print("dup_reasons", Counter(r["reason"] for r in rejects).most_common(5))
