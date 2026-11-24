import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"vett_overnight_20261114"
M={x["match"]:x for x in json.loads((P/"expansion_manifest.json").read_text(encoding="utf-8"))}
R=[json.loads(l) for l in (P/"runs"/"expand.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
def eq(a,b):
    try: return int(a)==int(b)
    except Exception: return False
per={}
for r in R:
    s=M[r["match"]]; d=r.get("parsed") or {}; ok=eq(d.get("total_runs"),s["runs"]) and eq(d.get("total_wickets"),s["wickets"])
    per.setdefault((r["match"],r["model"]),{})[r["cond"]]={"ok":ok,"runs":d.get("total_runs"),"wk":d.get("total_wickets")}
for model in ["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"]:
    rows=[v for k,v in per.items() if k[1]==model]
    print(model,[sum(1 for v in rows if v[c]["ok"]) for c in "OME"],"/",len(rows))
for c in "OME": print(c,sum(1 for v in per.values() if v[c]["ok"]),"/",len(per))
om=[(v["O"]["ok"],v["M"]["ok"]) for v in per.values()]; oe=[(v["O"]["ok"],v["E"]["ok"]) for v in per.values()]
print("OM",sum(1 for a,b in om if not a and b),sum(1 for a,b in om if a and not b),sum(1 for a,b in om if a and b),sum(1 for a,b in om if not a and not b))
print("OE",sum(1 for a,b in oe if not a and b),sum(1 for a,b in oe if a and not b),sum(1 for a,b in oe if a and b),sum(1 for a,b in oe if not a and not b))
print("rows",len(R))
