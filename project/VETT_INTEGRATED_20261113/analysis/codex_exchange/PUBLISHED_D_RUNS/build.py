import sys,json,re,hashlib
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); INT=ROOT/"VETT_INTEGRATED_20261113"; O=INT/"analysis"/"vett_overnight_20261114"; O.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(INT/"scripts")); import pilot_lib as L
# D sixth sample
m="match_0021"; team="Delta A Women"; runs=142; wk=7
text=(L.DATASET/m/"commentary.txt").read_text(encoding="utf-8"); ss=L.sentences(text)
ev=next((s for s in ss if "Delta A" in s and f"{runs} for" in s),"")
idx=ss.index(ev)
M=" ".join(ss[1:]+[ev]) if idx==0 else " ".join([ss[0],ev]+ss[1:idx]+ss[idx+1:])
E=" ".join(ss[max(0,idx-1):idx+2])
D={"match":m,"innings":1,"team":team,"runs":runs,"wickets":wk,"evidence":ev,"O":text,"M":M,"E":E,"ev_index":idx,"n_sent":len(ss),"O_sha":hashlib.sha256(text.encode()).hexdigest(),"M_sha":hashlib.sha256(M.encode()).hexdigest(),"E_sha":hashlib.sha256(E.encode()).hexdigest()}
# T roots
T=[]
for m in ["match_0100","match_0111","match_0120","match_0130","match_0140","match_0160"]:
    text=(L.DATASET/m/"commentary.txt").read_text(encoding="utf-8"); md=L.parse_scorecard_full((L.DATASET/m/"scorecard.md").read_text(encoding="utf-8"),m)
    gold={}
    gold["match.result"]=md.result; gold["match.toss"]=md.toss; gold["match.pom"]=md.player_of_match
    for i,inn in enumerate(md.innings,1):
        p=f"inn{i}"; gold[p+".team"]=inn.name; gold[p+".total_runs"]=inn.total_runs; gold[p+".total_wickets"]=inn.total_wickets; gold[p+".overs"]=inn.overs
        for j,b in enumerate(sorted(inn.batters,key=lambda x:x.runs,reverse=True)[:3],1): gold[f"{p}.bat{j}_name"]=b.name; gold[f"{p}.bat{j}_runs"]=b.runs
        for j,b in enumerate(sorted(inn.bowlers,key=lambda x:(x.wickets,-x.runs_conceded),reverse=True)[:2],1): gold[f"{p}.bowl{j}_name"]=b.name; gold[f"{p}.bowl{j}_wickets"]=b.wickets; gold[f"{p}.bowl{j}_runs"]=b.runs_conceded
    T.append({"match":m,"text":text,"gold":gold,"text_sha256":hashlib.sha256(text.encode()).hexdigest()})
(O/"manifest.json").write_text(json.dumps({"D":D,"T":T},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("D",D["match"],"evidx",idx,"T",len(T),[x["match"] for x in T])
