import sys,json,re
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); INT=ROOT/"VETT_INTEGRATED_20261113"
A=INT/"analysis"/"attribution_update_and_full_table"; O=INT/"analysis"/"input_and_score_audit"
sys.path.insert(0,str(INT/"scripts")); import pilot_lib as L
M=["match_0003","match_0008","match_0010","match_0012","match_0015","match_0017"]
def gold(m):
    md=L.parse_scorecard_full((L.DATASET/m/"scorecard.md").read_text(encoding="utf-8"),m); f={}
    f["match.result"]=md.result; f["match.toss"]=md.toss; f["match.pom"]=md.player_of_match
    for i,inn in enumerate(md.innings,1):
        p=f"inn{i}"; f[p+".team"]=inn.name; f[p+".total_runs"]=inn.total_runs; f[p+".total_wickets"]=inn.total_wickets
        f[p+".overs"]=inn.overs; f[p+".byes"]=inn.byes; f[p+".leg_byes"]=inn.leg_byes; f[p+".no_balls"]=inn.no_balls; f[p+".wides"]=inn.wides
        for r,b in enumerate(sorted(inn.batters,key=lambda x:x.runs,reverse=True)[:3],1): f[f"{p}.bat{r}_name"]=b.name; f[f"{p}.bat{r}_runs"]=b.runs
        for r,b in enumerate(sorted(inn.bowlers,key=lambda x:(x.wickets,-x.runs_conceded),reverse=True)[:2],1): f[f"{p}.bowl{r}_name"]=b.name; f[f"{p}.bowl{r}_wickets"]=b.wickets; f[f"{p}.bowl{r}_runs"]=b.runs_conceded
    return f
def evidence(field,val,text):
    ss=L.sentences(text)
    kw=None
    if field.startswith("match.result"): kw="won by"
    elif field.startswith("match.toss"): kw="won the toss"
    elif field.startswith("match.pom"): kw="Player of the Match"
    elif field.endswith(".team"): kw=str(val)
    elif field.endswith(".overs"): kw="overs"
    elif field.endswith(".byes"): kw="byes"
    elif field.endswith(".leg_byes"): kw="leg byes"
    elif field.endswith(".no_balls"): kw="no balls"
    elif field.endswith(".wides"): kw="wides"
    elif "_name" in field: kw=str(val)
    else: kw=None
    if kw:
        for s in ss:
            if kw.lower() in s.lower() and (str(val).lower() in s.lower() or field.endswith(".team") or field.startswith("match.")): return "direct",s[:220]
        for s in ss:
            if kw.lower() in s.lower(): return "derived" if field.endswith((".total_runs",".total_wickets")) else "insufficient",s[:220]
    if field.endswith(".total_runs") or field.endswith(".total_wickets"):
        for s in ss:
            if re.search(r"\d+\s*(?:/|for)\s*\d+",s): return "derived",s[:220]
    return "insufficient",""
def pred_fields(r):
    f=r.get("fields") or r.get("parsed") or {}
    if isinstance(f,dict) and isinstance(f.get("fields"),dict): f=f["fields"]
    if isinstance(f,dict) and "inn1" in f:
        flat={}
        for k,v in (f.get("match") or {}).items(): flat["match."+k]=v
        for i in (1,2):
            for k,v in (f.get(f"inn{i}") or {}).items(): flat[f"inn{i}.{k}"]=v
        return flat
    return f if isinstance(f,dict) else {}
def norm(v): return str(v).strip().lower().replace("  "," ")
rows=[json.loads(l) for l in (A/"runs"/"ft.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
out=[]; stats={m:{"n":0,"direct":0,"derived":0,"insufficient":0,"conflict":0,"pred":{},"ok":0,"ans_ok":0,"ans_n":0} for m in M}
for m in M:
    g=gold(m); text=(L.DATASET/m/"commentary.txt").read_text(encoding="utf-8")
    for k,v in g.items():
        st,ev=evidence(k,v,text); out.append({"match":m,"field":k,"gold":v,"status":st,"evidence":ev})
        d=stats[m]; d["n"]+=1; d[st]=d.get(st,0)+1
for r in rows:
    m=r["match"]; p=pred_fields(r); g=gold(m); d=stats[m]; d["pred"][r["model"]]={"fields":p,"ok":0,"ans_ok":0,"ans_n":0,"full_ok":0}
    for k,v in g.items():
        ok=norm(p.get(k))==norm(v) or (isinstance(v,int) and str(p.get(k)).replace(".0","").isdigit() and int(float(p.get(k)))==v)
        st=next(x for x in out if x["match"]==m and x["field"]==k)["status"]
        d["pred"][r["model"]]["full_ok"]+=ok
        if st in ("direct","derived"): d["pred"][r["model"]]["ans_n"]+=1; d["pred"][r["model"]]["ans_ok"]+=ok
open(O/"FIELD_ANSWERABILITY.jsonl","w",encoding="utf-8").write("\n".join(json.dumps(x,ensure_ascii=False) for x in out)+"\n")
tot={k:sum(stats[m][k] for m in M) for k in ["n","direct","derived","insufficient","conflict"]}
tot["answerable"]=tot["direct"]+tot["derived"]
json.dump({"fields":tot,"per_match":stats},open(O/"full_table_rescore.json","w"),ensure_ascii=False,indent=1)
print("fields",tot)
for m in M:
    print(m,{k:stats[m][k] for k in ["n","direct","derived","insufficient"]})
    for model,x in stats[m]["pred"].items(): print(" ",model,"full",x["full_ok"],"ans",x["ans_ok"],"/",x["ans_n"])
