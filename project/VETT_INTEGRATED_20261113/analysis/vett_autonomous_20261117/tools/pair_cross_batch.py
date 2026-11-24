
import json, sqlite3, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import vettlib as V

con = V.init_db()
def cells(bid, cond):
    rows = con.execute("SELECT r.match,r.innings,r.model,r.parsed_json,r.score_json,t.fields_json FROM results r "
                       "JOIN tasks t USING(task_key) WHERE r.batch_id=? AND t.cond=?", (bid, cond)).fetchall()
    out = {}
    for r in rows:
        sc = json.loads(r["score_json"] or "{}")
        out[(r["match"], r["innings"], r["model"])] = {"cells": sc.get("cells", {}), "fields": json.loads(r["fields_json"])}
    return out
b3 = cells("B003", "O")
b13 = cells("B013", "OIC")
res = {"pairs": 0, "gain": 0, "loss": 0, "both": 0, "neither": 0, "detail": []}
for k, v in b13.items():
    base_cells = b3.get(k)
    if not base_cells:
        continue
    for f, c in v["cells"].items():
        if f not in base_cells["cells"]:
            continue
        o = bool(base_cells["cells"][f]["ok"]); x = bool(c["ok"])
        res["pairs"] += 1; res["gain"] += int(x and not o); res["loss"] += int(o and not x)
        res["both"] += int(o and x); res["neither"] += int(not o and not x)
        if o != x:
            res["detail"].append({"match": k[0], "innings": k[1], "model": k[2], "field": f, "O": o, "OIC": x})
res["net"] = res["gain"] - res["loss"]
res["note"] = "B013 contains only OIC tasks; baseline O is historical B003, same root/model/field"
Path("reports/B013_CROSS_PAIR.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
lines = ["# B013 cross-batch pairing", "", "- pairs: " + str(res["pairs"]),
         "- gain: " + str(res["gain"]) + "; loss: " + str(res["loss"]) + "; net: " + str(res["net"]),
         "- both: " + str(res["both"]) + "; neither: " + str(res["neither"]), "", res["note"]]
Path("reports/B013_CROSS_PAIR.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(json.dumps(res, ensure_ascii=False))
