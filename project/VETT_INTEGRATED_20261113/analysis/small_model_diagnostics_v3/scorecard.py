import sys,json
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); INT=ROOT/"VETT_INTEGRATED_20261113"; O=INT/"analysis"/"small_model_diagnostics_v3"
sys.path.insert(0,str(INT/"scripts")); import pilot_lib as L
v4=[json.loads(l) for l in (INT/"analysis"/"small_model_diagnostics_v2"/"FIELD_ANSWERABILITY_V4.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
new=[x for x in v4 if x.get("change_reason_v4","").startswith("team-root")]
print("new fields",len(new))
for x in new: print(x["match"],x["field"],x["gold"],"|",x["v4_evidence"][:140])
ans={(x["match"],x["field"]) for x in v4 if x["v4_status"] in ("direct","derived")}
def gold(m):
    md=L.parse_scorecard_full((L.DATASET/m/"scorecard.md").read_text(encoding="utf-8"),m); f={}
    f["match.result"]=md.result; f["match.toss"]=md.toss; f["match.pom"]=md.player_of_match
    for i,inn in enumerate(md.innings,1):
        p=f"inn{i}"; f[p+".team"]=inn.name; f[p+".total_runs"]=inn.total_runs; f[p+".total_wickets"]=inn.total_wickets; f[p+".overs"]=inn.overs; f[p+".byes"]=inn.byes; f[p+".leg_byes"]=inn.leg_byes; f[p+".no_balls"]=inn.no_balls; f[p+".wides"]=inn.wides
        for j,b in enumerate(sorted(inn.batters,key=lambda x:x.runs,reverse=True)[:3],1): f[f"{p}.bat{j}_name"]=b.name; f[f"{p}.bat{j}_runs"]=b.runs
        for j,b in enumerate(sorted(inn.bowlers,key=lambda x:(x.wickets,-x.runs_conceded),reverse=True)[:2],1): f[f"{p}.bowl{j}_name"]=b.name; f[f"{p}.bowl{j}_wickets"]=b.wickets; f[f"{p}.bowl{j}_runs"]=b.runs_conceded
    return f
ft=[json.loads(l) for l in (INT/"analysis"/"attribution_update_and_full_table"/"runs"/"ft.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
tot=0; per={}
for r in ft:
    if not r["model"].startswith("llama"): continue
    try: d=json.loads(r["raw_output"]); flat={}
    except Exception: flat={}
    for k,v in (d.get("match") or {}).items(): flat["match."+k]=v
    for i in (1,2):
        for k,v in (d.get(f"inn{i}") or {}).items(): flat[f"inn{i}.{k}"]=v
    g=gold(r["match"]); n=ok=0
    for k,v in g.items():
        if (r["match"],k) not in ans: continue
        n+=1; ok+= (str(flat.get(k)).strip().lower()==str(v).strip().lower()) or (isinstance(v,int) and str(flat.get(k)).replace(".0","").isdigit() and int(float(flat.get(k)))==v)
    per[r["match"]]=[ok,n]; tot+=ok
print("llama",tot,"/",len(ans),"per",per)
