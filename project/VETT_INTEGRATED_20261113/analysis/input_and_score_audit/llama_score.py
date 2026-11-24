import sys,json
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); INT=ROOT/"VETT_INTEGRATED_20261113"; A=INT/"analysis"/"attribution_update_and_full_table"
sys.path.insert(0,str(INT/"scripts")); import pilot_lib as L
def gold(m):
    md=L.parse_scorecard_full((L.DATASET/m/"scorecard.md").read_text(encoding="utf-8"),m); f={}
    f["match.result"]=md.result; f["match.toss"]=md.toss; f["match.pom"]=md.player_of_match
    for i,inn in enumerate(md.innings,1):
        p=f"inn{i}"; f[p+".team"]=inn.name; f[p+".total_runs"]=inn.total_runs; f[p+".total_wickets"]=inn.total_wickets; f[p+".overs"]=inn.overs; f[p+".byes"]=inn.byes; f[p+".leg_byes"]=inn.leg_byes; f[p+".no_balls"]=inn.no_balls; f[p+".wides"]=inn.wides
        for r,b in enumerate(sorted(inn.batters,key=lambda x:x.runs,reverse=True)[:3],1): f[f"{p}.bat{r}_name"]=b.name; f[f"{p}.bat{r}_runs"]=b.runs
        for r,b in enumerate(sorted(inn.bowlers,key=lambda x:(x.wickets,-x.runs_conceded),reverse=True)[:2],1): f[f"{p}.bowl{r}_name"]=b.name; f[f"{p}.bowl{r}_wickets"]=b.wickets; f[f"{p}.bowl{r}_runs"]=b.runs_conceded
    return f
def norm(v): return str(v).strip().lower()
rows=[json.loads(l) for l in (A/"runs"/"ft.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
for r in rows:
    if not r["model"].startswith("llama"): continue
    try: d=json.loads(r["raw_output"]); flat={}
    except Exception: print(r["match"],"parse_fail"); continue
    for k,v in (d.get("match") or {}).items(): flat["match."+k]=v
    for i in (1,2):
        for k,v in (d.get(f"inn{i}") or {}).items(): flat[f"inn{i}.{k}"]=v
    if not flat: print(r["match"],"empty"); continue
    g=gold(r["match"]); ok=sum(1 for k,v in g.items() if norm(flat.get(k))==norm(v) or (isinstance(v,int) and str(flat.get(k)).replace(".0","").isdigit() and int(float(flat.get(k)))==v))
    print(r["match"],"recovered",ok,"/",len(g))
