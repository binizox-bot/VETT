import sys,json
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); INT=ROOT/"VETT_INTEGRATED_20261113"; O=INT/"analysis"/"small_model_diagnostics_v2"
sys.path.insert(0,str(INT/"scripts")); import pilot_lib as L
fa=[json.loads(l) for l in (O/"FIELD_ANSWERABILITY_V4.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
ans={(x["match"],x["field"]) for x in fa if x["v4_status"] in ("direct","derived")}
for x in fa:
    if x["match"]=="match_0008" and "total_wickets" in x["field"]: print(x["field"],x["v4_status"],x["v4_evidence"])
def gold(m):
    md=L.parse_scorecard_full((L.DATASET/m/"scorecard.md").read_text(encoding="utf-8"),m); f={}
    f["match.result"]=md.result; f["match.toss"]=md.toss; f["match.pom"]=md.player_of_match
    for i,inn in enumerate(md.innings,1):
        p=f"inn{i}"; f[p+".team"]=inn.name; f[p+".total_runs"]=inn.total_runs; f[p+".total_wickets"]=inn.total_wickets; f[p+".overs"]=inn.overs; f[p+".byes"]=inn.byes; f[p+".leg_byes"]=inn.leg_byes; f[p+".no_balls"]=inn.no_balls; f[p+".wides"]=inn.wides
        for j,b in enumerate(sorted(inn.batters,key=lambda x:x.runs,reverse=True)[:3],1): f[f"{p}.bat{j}_name"]=b.name; f[f"{p}.bat{j}_runs"]=b.runs
        for j,b in enumerate(sorted(inn.bowlers,key=lambda x:(x.wickets,-x.runs_conceded),reverse=True)[:2],1): f[f"{p}.bowl{j}_name"]=b.name; f[f"{p}.bowl{j}_wickets"]=b.wickets; f[f"{p}.bowl{j}_runs"]=b.runs_conceded
    return f
ft=[json.loads(l) for l in (INT/"analysis"/"attribution_update_and_full_table"/"runs"/"ft.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
ok=n=0
for r in ft:
    if not r["model"].startswith("llama"): continue
    try: d=json.loads(r["raw_output"]); flat={}
    except Exception: flat={}
    for k,v in (d.get("match") or {}).items(): flat["match."+k]=v
    for i in (1,2):
        for k,v in (d.get(f"inn{i}") or {}).items(): flat[f"inn{i}.{k}"]=v
    g=gold(r["match"])
    for k,v in g.items():
        if (r["match"],k) not in ans: continue
        n+=1; ok+= (str(flat.get(k)).strip().lower()==str(v).strip().lower()) or (isinstance(v,int) and str(flat.get(k)).replace(".0","").isdigit() and int(float(flat.get(k)))==v)
print("llama",ok,"/",n)
