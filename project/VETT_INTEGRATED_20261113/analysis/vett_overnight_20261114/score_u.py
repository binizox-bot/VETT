import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"vett_overnight_20261114"
S={x["match"]:x for x in json.loads((P/"u_manifest.json").read_text(encoding="utf-8"))}
R=[json.loads(l) for l in (P/"runs"/"u_audit.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
def eq(a,b):
    try: return int(a)==int(b)
    except Exception: return False
per={}
for r in R:
    s=S[r["match"]]; d=r.get("parsed") or {}
    def v(k):
        o=d.get(k) or {}; return o.get("value") if isinstance(o,dict) else None
    q=[]
    for k in ["total_runs","total_wickets"]:
        o=d.get(k) or {}
        if isinstance(o,dict): q+=o.get("quotes") or []
    qok=all(isinstance(x,str) and x in s["text"] for x in q) if q else False
    per[(r["match"],r["model"])]={"runs":eq(v("total_runs"),s["runs"]),"wk":eq(v("total_wickets"),s["wickets"]),"both":eq(v("total_runs"),s["runs"]) and eq(v("total_wickets"),s["wickets"]),"qok":qok,"parse":r["parse_ok"]}
for model in ["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"]:
    rows=[v for k,v in per.items() if k[1]==model]
    print(model,"both",sum(v["both"] for v in rows),"/",len(rows),"runs",sum(v["runs"] for v in rows),"wk",sum(v["wk"] for v in rows),"quote",sum(v["qok"] for v in rows))
print("total",sum(v["both"] for v in per.values()),"/",len(per),"rows",len(R))
