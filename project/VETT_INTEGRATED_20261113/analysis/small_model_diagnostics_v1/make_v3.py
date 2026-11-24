import sys,json,re
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); INT=ROOT/"VETT_INTEGRATED_20261113"; O=INT/"analysis"/"small_model_diagnostics_v1"
sys.path.insert(0,str(INT/"scripts")); import pilot_lib as L
BASE=[json.loads(l) for l in (INT/"analysis"/"input_and_score_audit"/"FIELD_ANSWERABILITY.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
W={"zero":0,"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,"eight":8,"nine":9,"ten":10}
def score_sentence(m,team,total_runs,total_wk):
    text=(L.DATASET/m/"commentary.txt").read_text(encoding="utf-8")
    for s in L.sentences(text):
        if team.lower() not in s.lower(): continue
        mm=re.search(r"(\d{2,3})\s+(?:for|/)\s+([A-Za-z]+|\d+)",s)
        if not mm: continue
        r=int(mm.group(1)); w=mm.group(2); w=W.get(w.lower(),int(w) if w.isdigit() else -1)
        if r==total_runs and w==total_wk: return s
    return ""
out=[]; changed=0
for x in BASE:
    y=dict(x); y["v3_status"]=x["status"]; y["v3_evidence"]=x["evidence"]; y["change_reason"]=""
    if x["field"].endswith((".total_runs",".total_wickets")) and x["status"]=="insufficient":
        # get team/gold from scorecard via ft gold function not available; use commentary match: find team name from field's gold? use scorecard parser
        pass
    out.append(y)
# use gold from full_table_rescore? need team/runs/wk; parse scorecard
for y in out:
    if not y["field"].endswith((".total_runs",".total_wickets")): continue
    m=y["match"]; md=L.parse_scorecard_full((L.DATASET/m/"scorecard.md").read_text(encoding="utf-8"),m)
    i=1 if y["field"].startswith("inn1") else 2; inn=md.innings[i-1]
    s=score_sentence(m,inn.name,inn.total_runs,inn.total_wickets)
    if s:
        y["v3_status"]="direct"; y["v3_evidence"]=s; y["change_reason"]="score sentence supplies both total runs and wickets"
        if y["status"]=="insufficient": changed+=1
(O/"FIELD_ANSWERABILITY_V3.jsonl").write_text("\n".join(json.dumps(x,ensure_ascii=False) for x in out)+"\n",encoding="utf-8")
ans={(x["match"],x["field"]) for x in out if x["v3_status"] in ("direct","derived")}
print("answerable",len(ans),"changed",changed)
# score predictions
def preds():
    ft=[json.loads(l) for l in (INT/"analysis"/"attribution_update_and_full_table"/"runs"/"ft.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    res={}
    for r in ft:
        f=r.get("fields") or r.get("parsed") or {}
        if isinstance(f,dict) and "inn1" in f:
            flat={}
            for k,v in (f.get("match") or {}).items(): flat["match."+k]=v
            for i in (1,2):
                for k,v in (f.get(f"inn{i}") or {}).items(): flat[f"inn{i}.{k}"]=v
            f=flat
        res[r["match"]]=f
    return res
P=preds()
# gold
import importlib.util
# reuse ft_score gold by parsing
def gold(m):
    md=L.parse_scorecard_full((L.DATASET/m/"scorecard.md").read_text(encoding="utf-8"),m); f={}
    f["match.result"]=md.result; f["match.toss"]=md.toss; f["match.pom"]=md.player_of_match
    for i,inn in enumerate(md.innings,1):
        p=f"inn{i}"; f[p+".team"]=inn.name; f[p+".total_runs"]=inn.total_runs; f[p+".total_wickets"]=inn.total_wickets; f[p+".overs"]=inn.overs; f[p+".byes"]=inn.byes; f[p+".leg_byes"]=inn.leg_byes; f[p+".no_balls"]=inn.no_balls; f[p+".wides"]=inn.wides
        for j,b in enumerate(sorted(inn.batters,key=lambda x:x.runs,reverse=True)[:3],1): f[f"{p}.bat{j}_name"]=b.name; f[f"{p}.bat{j}_runs"]=b.runs
        for j,b in enumerate(sorted(inn.bowlers,key=lambda x:(x.wickets,-x.runs_conceded),reverse=True)[:2],1): f[f"{p}.bowl{j}_name"]=b.name; f[f"{p}.bowl{j}_wickets"]=b.wickets; f[f"{p}.bowl{j}_runs"]=b.runs_conceded
    return f
for model in ["qwen2.5:7b-instruct-q4_K_M","gemma2:9b","llama3.1:8b"]:
    ok=n=0; full=0
    for m in ["match_0003","match_0008","match_0010","match_0012","match_0015","match_0017"]:
        f=P.get(m,{}); g=gold(m)
        for k,v in g.items():
            good=str(f.get(k)).strip().lower()==str(v).strip().lower() or (isinstance(v,int) and str(f.get(k)).replace(".0","").isdigit() and int(float(f.get(k)))==v)
            full+=good
            if (m,k) in ans: n+=1; ok+=good
    print(model,"ans",ok,"/",n,"full",full)
