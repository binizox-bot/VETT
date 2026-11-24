import json
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); INT=ROOT/"VETT_INTEGRATED_20261113"; O=INT/"analysis"/"vett_local_evidence_long_run"
M=json.loads((O/"manifest.json").read_text(encoding="utf-8"))
au=[]; mp=[]
for x in M["evidence"]:
    for field,val in [("total_runs",x["runs"]),("total_wickets",x["wickets"])]:
        au.append({"match":x["match"],"innings":x["innings"],"team":x["team"],"field":field,"value":val,"quote":x["sentence"],"status":"auto_verified","source":"published commentary"})
        mp.append({"match":x["match"],"innings":x["innings"],"field":field,"source":"published commentary","evidence":x["sentence"],"r28_id":None})
for x in [("match_0003",1,"Evan Clarke_wickets",4),("match_0003",1,"Connor Reed_wickets",1),("match_0012",1,"Caleb Brooks_wickets",4),("match_0012",1,"Lucas Vale_wickets",2)]:
    mp.append({"match":x[0],"innings":x[1],"field":x[2],"source":"scorecard rerender","evidence":None,"r28_id":x[0]+"_r28","published_evidence":False,"value":x[3]})
(O/"evidence_audit.jsonl").write_text("\n".join(json.dumps(x,ensure_ascii=False) for x in au)+"\n",encoding="utf-8")
(O/"evidence_map.jsonl").write_text("\n".join(json.dumps(x,ensure_ascii=False) for x in mp)+"\n",encoding="utf-8")
# score replay: linkage
L=json.loads((INT/"analysis"/"vett_220_r28_link_pilot"/"scores.json").read_text(encoding="utf-8"))
rows=[]
for k,v in L["per"].items():
    m,model,cond=k.split("|")
    rows.append({"phase":"linkage_replay","match":m,"model":model,"condition":cond,"A_ok":v["A_ok"],"B_ok":v["B_ok"],"B_exec":v["B_exec"]})
S=json.loads((O/"scores.json").read_text(encoding="utf-8"))
for k,v in S["evidence"].items(): rows.append({"phase":"evidence","key":k,"ok":v["ok"],"qok":v["qok"]})
for k,v in S["abc"].items(): rows.append({"phase":"abc","key":k,"ok":v["ok"],"qok":v["qok"]})
(O/"score_replay.jsonl").write_text("\n".join(json.dumps(x,ensure_ascii=False) for x in rows)+"\n",encoding="utf-8")
print("audit",len(au),"map",len(mp),"replay",len(rows))
