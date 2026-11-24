import sys,json,re
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); INT=ROOT/"VETT_INTEGRATED_20261113"; O=INT/"analysis"/"small_model_diagnostics_v2"
sys.path.insert(0,str(INT/"scripts")); import pilot_lib as L
rows=[json.loads(l) for l in (O/"FIELD_ANSWERABILITY_V4.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
W={"zero":0,"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,"eight":8,"nine":9,"ten":10}
def root(t): return re.sub(r"\s+(XI|Women|CC|Club)$","",t.strip(),flags=re.I)
changed=0
for x in rows:
    if not x["field"].endswith((".total_runs",".total_wickets")): continue
    md=L.parse_scorecard_full((L.DATASET/x["match"]/"scorecard.md").read_text(encoding="utf-8"),x["match"]); inn=md.innings[0 if x["field"].startswith("inn1") else 1]
    text=(L.DATASET/x["match"]/"commentary.txt").read_text(encoding="utf-8"); ev=""
    for s in L.sentences(text):
        if root(inn.name).lower() not in s.lower(): continue
        m=re.search(r"(\d{2,3})\s+(?:for|/)\s+([A-Za-z]+|\d+)",s)
        if not m: continue
        r=int(m.group(1)); w=m.group(2); w=W.get(w.lower(),int(w) if w.isdigit() else -1)
        if r==inn.total_runs and w==inn.total_wickets: ev=s; break
    if ev and x["v4_status"]=="insufficient":
        x["v4_status"]="direct"; x["v4_evidence"]=ev; x["change_reason_v4"]="team-root score sentence supplies total"; changed+=1
open(O/"FIELD_ANSWERABILITY_V4.jsonl","w",encoding="utf-8").write("\n".join(json.dumps(x,ensure_ascii=False) for x in rows)+"\n")
ans={(x["match"],x["field"]) for x in rows if x["v4_status"] in ("direct","derived")}
print("answerable",len(ans),"changed",changed)
# predictions
ft=[json.loads(l) for l in (INT/"analysis"/"attribution_update_and_full_table"/"runs"/"ft.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
def flat(r):
    f=r.get("fields") or r.get("parsed") or {}
    if isinstance(f,dict) and "inn1" in f:
        z={}
        for k,v in (f.get("match") or {}).items(): z["match."+k]=v
        for i in (1,2):
            for k,v in (f.get(f"inn{i}") or {}).items(): z[f"inn{i}.{k}"]=v
        return z
    return f if isinstance(f,dict) else {}
def gold(m):
    md=L.parse_scorecard_full((L.DATASET/m/"scorecard.md").read_text(encoding="utf-8"),m); f={}
    f["match.result"]=md.result; f["match.toss"]=md.toss; f["match.pom"]=md.player_of_match
    for i,inn in enumerate(md.innings,1):
        p=f"inn{i}"; f[p+".team"]=inn.name; f[p+".total_runs"]=inn.total_runs; f[p+".total_wickets"]=inn.total_wickets; f[p+".overs"]=inn.overs; f[p+".byes"]=inn.byes; f[p+".leg_byes"]=inn.leg_byes; f[p+".no_balls"]=inn.no_balls; f[p+".wides"]=inn.wides
        for j,b in enumerate(sorted(inn.batters,key=lambda x:x.runs,reverse=True)[:3],1): f[f"{p}.bat{j}_name"]=b.name; f[f"{p}.bat{j}_runs"]=b.runs
        for j,b in enumerate(sorted(inn.bowlers,key=lambda x:(x.wickets,-x.runs_conceded),reverse=True)[:2],1): f[f"{p}.bowl{j}_name"]=b.name; f[f"{p}.bowl{j}_wickets"]=b.wickets; f[f"{p}.bowl{j}_runs"]=b.runs_conceded
    return f
for model in ["qwen2.5:7b-instruct-q4_K_M","gemma2:9b","llama3.1:8b"]:
    ok=n=0
    for r in [z for z in ft if z["model"]==model]:
        f=flat(r); g=gold(r["match"])
        for k,v in g.items():
            if (r["match"],k) not in ans: continue
            n+=1; ok+= (str(f.get(k)).strip().lower()==str(v).strip().lower()) or (isinstance(v,int) and str(f.get(k)).replace(".0","").isdigit() and int(float(f.get(k)))==v)
    print(model,ok,"/",n)
