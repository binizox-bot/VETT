import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"vett_local_evidence_long_run"
M=json.loads((P/"manifest.json").read_text(encoding="utf-8")); R=[json.loads(l) for l in (P/"runs"/"all.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
def eq(a,b):
    try: return int(a)==int(b)
    except Exception: return False
ev_score={}; abc_score={}
for r in R:
    if r["phase"]=="evidence":
        x=next(y for y in M["evidence"] if y["match"]==r["match"]); d=r.get("parsed") or {}
        def val(k):
            o=d.get(k) or {}
            return o.get("value") if isinstance(o,dict) else None
        oks=eq(val("total_runs"),x["runs"]) and eq(val("total_wickets"),x["wickets"])
        quotes=[]
        for k in ["total_runs","total_wickets"]:
            o=d.get(k) or {}
            if isinstance(o,dict): quotes+=o.get("quotes") or []
        qok=all(isinstance(q,str) and q in x["text"] for q in quotes) if quotes else False
        ev_score[(r["match"],r["model"])]={"ok":oks,"runs":val("total_runs"),"wk":val("total_wickets"),"qok":qok,"parse":r["parse_ok"]}
    else:
        x=next(y for y in M["abc"] if y["match"]==r["match"] and y["method"]==r["method"]); d=r.get("parsed") or {}
        ok=eq(d.get("total_runs"),x["gold_runs"]) and eq(d.get("total_wickets"),x["gold_wickets"])
        ev=d.get("evidence") or []
        qok=all(isinstance(q,str) and q in x["text"] for q in ev) if ev else False
        abc_score[(r["match"],r["method"],r["model"])]={"ok":ok,"runs":d.get("total_runs"),"wk":d.get("total_wickets"),"qok":qok,"parse":r["parse_ok"]}
json.dump({"evidence":{f"{k[0]}|{k[1]}":v for k,v in ev_score.items()},"abc":{f"{k[0]}|{k[1]}|{k[2]}":v for k,v in abc_score.items()}},open(P/"scores.json","w"),ensure_ascii=False,indent=1)
for model in ["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"]:
    print(model,"evidence",sum(1 for k,v in ev_score.items() if k[1]==model and v["ok"]),"/",sum(1 for k in ev_score if k[1]==model),
          "ABC",[sum(1 for k,v in abc_score.items() if k[2]==model and k[1]==m and v["ok"]) for m in "ABC"],"Cq",sum(1 for k,v in abc_score.items() if k[2]==model and k[1]=="C" and v["qok"]))
