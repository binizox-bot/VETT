
import sys
sys.path.insert(0, ".")
import vettlib as V, planner
con = V.init_db()
design, tasks, rejects = planner.build_probe_sweep(con, {"rationale":"test"})
print("built", len(tasks), "rejects", len(rejects), "cursor", V.meta_get(con,"probe_cursor","0"))
from collections import Counter
print("scopes", Counter(t["field_scope"] for t in tasks))
print("positions", design["positions"])
