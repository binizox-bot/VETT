import sys,json,re,hashlib
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); INT=ROOT/"VETT_INTEGRATED_20261113"; O=INT/"analysis"/"vett_evidence_position_transfer"
sys.path.insert(0,str(INT/"scripts")); import pilot_lib as L
SEL=[("match_0066",1,"Southwell",64,5),("match_0085",1,"Bayport",226,9),("match_0087",2,"Eastmoor",198,6),("match_0096",1,"Crimson Vale",134,7),("match_0099",2,"Lakeside",137,2),("match_0165",1,"Aurora Bay Women",142,5)]
out=[]
for m,inn,team,runs,wk in SEL:
    text=(L.DATASET/m/"commentary.txt").read_text(encoding="utf-8"); ss=L.sentences(text)
    ev=next((s for s in ss if team.split()[0].lower() in s.lower() and re.search(rf"\b{runs}\b",s) and re.search(rf"\b(wk|{'%d'%wk})\b",s)),"")
    if not ev: print("no ev",m); continue
    idx=ss.index(ev)
    # M: move evidence to after first sentence
    if idx==0: M=" ".join(ss[1:]+[ev])
    else: M=" ".join([ss[0],ev]+ss[1:idx]+ss[idx+1:])
    E=" ".join(ss[max(0,idx-1):idx+2])
    # check restore
    restore=" ".join([ev]+[s for i,s in enumerate(ss) if i!=idx]) if idx==0 else " ".join([ss[0]]+[s for i,s in enumerate(ss) if i not in (0,idx)]+[ev]) if False else ""
    out.append({"match":m,"innings":inn,"team":team,"runs":runs,"wickets":wk,"evidence":ev,"O":text,"M":M,"E":E,"ev_index":idx,"n_sent":len(ss),"O_sha":hashlib.sha256(text.encode()).hexdigest(),"M_sha":hashlib.sha256(M.encode()).hexdigest(),"E_sha":hashlib.sha256(E.encode()).hexdigest()})
(O/"manifest.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("built",len(out))
for x in out: print(x["match"],x["team"],x["runs"],x["wickets"],"idx",x["ev_index"],"/",x["n_sent"],"ev",x["evidence"][:100])
