import sys,json
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); INT=ROOT/"VETT_INTEGRATED_20261113"; P=INT/"analysis"/"vett_overnight_20261114"
sys.path.insert(0,str(INT/"scripts")); import pilot_lib as L
R=[json.loads(l) for l in (P/"runs"/"u_full.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
def eq(a,b):
    try: return int(a)==int(b)
    except Exception: return False
cache={}
per={}
for r in R:
    m=r["match"]
    if m not in cache:
        md=L.parse_scorecard_full((L.DATASET/m/"scorecard.md").read_text(encoding="utf-8"),m); cache[m]={1:md.innings[0],2:md.innings[1] if len(md.innings)>1 else md.innings[0]}
    inn=cache[m][r["innings"]]; d=r.get("parsed") or {}
    def val(k):
        o=d.get(k) or {}; return o.get("value") if isinstance(o,dict) else None
    q=[]
    for k in ["total_runs","total_wickets"]:
        o=d.get(k) or {}
        if isinstance(o,dict): q+=o.get("quotes") or []
    qok=all(isinstance(x,str) and x in r.get("text_sha256","") for x in []) if False else None
    per[(m,r["innings"],r["model"])]={"runs":eq(val("total_runs"),inn.total_runs),"wk":eq(val("total_wickets"),inn.total_wickets),"both":eq(val("total_runs"),inn.total_runs) and eq(val("total_wickets"),inn.total_wickets),"unknown":val("total_runs")=="UNKNOWN" or val("total_wickets")=="UNKNOWN","parse":r["parse_ok"]}
for model in ["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"]:
    rows=[v for k,v in per.items() if k[2]==model]
    print(model,"n",len(rows),"both",sum(v["both"] for v in rows),"runs",sum(v["runs"] for v in rows),"wk",sum(v["wk"] for v in rows),"unknown",sum(v["unknown"] for v in rows),"parse",sum(v["parse"] for v in rows))
print("total",len(per),"both",sum(v["both"] for v in per.values()),"runs",sum(v["runs"] for v in per.values()),"wk",sum(v["wk"] for v in per.values()),"unknown",sum(v["unknown"] for v in per.values()))
