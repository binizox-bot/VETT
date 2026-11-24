import sys,json
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); INT=ROOT/"VETT_INTEGRATED_20261113"; P=INT/"analysis"/"attribution_update_and_full_table"
sys.path.insert(0,str(INT/"scripts")); import pilot_lib as L
MATCHES=["match_0003","match_0008","match_0010","match_0012","match_0015","match_0017"]
def gold(m):
    md=L.parse_scorecard_full((L.DATASET/m/"scorecard.md").read_text(encoding="utf-8"),m); f={}
    f["match.result"]=md.result; f["match.toss"]=md.toss; f["match.pom"]=md.player_of_match
    for i,inn in enumerate(md.innings,1):
        p=f"inn{i}"; f[p+".team"]=inn.name; f[p+".total_runs"]=inn.total_runs; f[p+".total_wickets"]=inn.total_wickets
        f[p+".overs"]=inn.overs; f[p+".byes"]=inn.byes; f[p+".leg_byes"]=inn.leg_byes; f[p+".no_balls"]=inn.no_balls; f[p+".wides"]=inn.wides
        for r,b in enumerate(sorted(inn.batters,key=lambda x:x.runs,reverse=True)[:3],1): f[f"{p}.bat{r}_name"]=b.name; f[f"{p}.bat{r}_runs"]=b.runs
        for r,b in enumerate(sorted(inn.bowlers,key=lambda x:(x.wickets,-x.runs_conceded),reverse=True)[:2],1): f[f"{p}.bowl{r}_name"]=b.name; f[f"{p}.bowl{r}_wickets"]=b.wickets; f[f"{p}.bowl{r}_runs"]=b.runs_conceded
    return f
def norm(v): return str(v).strip().lower().replace("  "," ")
rows=[json.loads(l) for l in (P/"runs"/"ft.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
out={"by_model":{}}
for r in rows:
    m=r["match"]; model=r["model"]; g=gold(m); f=r.get("fields") or r.get("parsed") or {}
    if isinstance(f,dict) and isinstance(f.get("fields"),dict): f=f["fields"]
    ok={k:(norm(f.get(k))==norm(v) or (str(f.get(k)).replace(".0","").isdigit() and str(int(float(f.get(k))))==str(v))) for k,v in g.items()} if isinstance(f,dict) else {}
    correct=sum(1 for v in ok.values() if v); n=len(g); missing=sum(1 for k in g if k not in f) if isinstance(f,dict) else n
    cats=lambda pfx: sum(1 for k,v in ok.items() if k.startswith(pfx))
    out["by_model"].setdefault(model,{})[m]={"n":n,"correct":correct,"missing":missing,"acc":round(correct/n,4) if n else 0,
        "match":cats("match."),"innsum":sum(1 for k,v in ok.items() if k.split(".")[-1] in ["team","total_runs","total_wickets","overs","byes","leg_byes","no_balls","wides"] and v),
        "bat":cats("inn1.bat")+cats("inn2.bat"),"bowl":cats("inn1.bowl")+cats("inn2.bowl"),
        "done":r.get("done_reason"),"eval":r.get("eval_count"),"parse":r.get("parse_ok")}
(P/"ft_scores.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
for model,d in out["by_model"].items():
    print("\n",model)
    for m,x in d.items(): print(" ",m,"acc",x["acc"],"missing",x["missing"],"parse",x["parse"],"done",x["done"],"eval",x["eval"],"bat",x["bat"],"bowl",x["bowl"])
