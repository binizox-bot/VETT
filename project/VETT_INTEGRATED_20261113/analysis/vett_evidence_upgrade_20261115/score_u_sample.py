import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"vett_evidence_upgrade_20261115"
S=json.loads((P/"U_SAMPLE_MANIFEST.json").read_text(encoding="utf-8"))
R=[json.loads(l) for l in (P/"RUNS"/"u_sample.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
def eq(a,b):
    try: return int(a)==int(b)
    except Exception: return False
rows=[]
for r in R:
    s=next(x for x in S if x["match"]==r["match"] and x["innings"]==r["innings"]); d=r.get("parsed") or {}
    def v(k):
        o=d.get(k) or {}; return o.get("value") if isinstance(o,dict) else None
    rows.append((r["group"],r["model"],eq(v("total_runs"),s["runs"]) and eq(v("total_wickets"),s["wickets"]),r["parse_ok"],v("total_runs")=="UNKNOWN" or v("total_wickets")=="UNKNOWN"))
for g in ["both","runs_only","wk_only","neither"]:
    x=[r for r in rows if r[0]==g]; print(g,"n",len(x),"both",sum(1 for r in x if r[2]),"parse",sum(1 for r in x if r[3]),"unknown",sum(1 for r in x if r[4]))
for model in ["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"]:
    x=[r for r in rows if r[1]==model]; print(model,"both",sum(1 for r in x if r[2]),"/",len(x))
print("total",len(rows),"both",sum(1 for r in rows if r[2]))
