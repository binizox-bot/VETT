import json
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); INT=ROOT/"VETT_INTEGRATED_20261113"; P=INT/"analysis"/"vett_evidence_position_transfer"
S=json.loads((P/"manifest.json").read_text(encoding="utf-8"))
mp=[]; diff=[]
for x in S:
    for f,v in [("total_runs",x["runs"]),("total_wickets",x["wickets"])]:
        mp.append({"match":x["match"],"innings":x["innings"],"field":f,"value":v,"source":"published commentary","evidence":x["evidence"],"variants":["O","M","E"],"r28_id":None,"status":"auto_verified"})
    diff.append({"match":x["match"],"innings":x["innings"],"ev_index":x["ev_index"],"n_sent":x["n_sent"],"O_sha":x["O_sha"],"M_sha":x["M_sha"],"E_sha":x["E_sha"],"move":"evidence sentence moved to after first sentence" if x["ev_index"]>0 else "evidence sentence moved to end"})
(P/"evidence_map.jsonl").write_text("\n".join(json.dumps(x,ensure_ascii=False) for x in mp)+"\n",encoding="utf-8")
(P/"position_diff.jsonl").write_text("\n".join(json.dumps(x,ensure_ascii=False) for x in diff)+"\n",encoding="utf-8")
rows=[]
sc=json.loads((P/"scores.json").read_text(encoding="utf-8"))
for k,v in sc["per"].items():
    m,model=k.split("|")
    for cond in "OME": rows.append({"phase":"ome","match":m,"model":model,"condition":cond,"ok":v[cond]["ok"],"runs":v[cond]["runs"],"wk":v[cond]["wk"]})
old=json.loads((INT/"analysis"/"vett_local_evidence_long_run"/"scores.json").read_text(encoding="utf-8"))
for k,v in old["evidence"].items(): rows.append({"phase":"evidence","key":k,"ok":v["ok"]})
for k,v in old["abc"].items(): rows.append({"phase":"abc","key":k,"ok":v["ok"]})
link=json.loads((INT/"analysis"/"vett_220_r28_link_pilot"/"scores.json").read_text(encoding="utf-8"))
for k,v in link["per"].items():
    m,model,cond=k.split("|"); rows.append({"phase":"linkage","match":m,"model":model,"condition":cond,"A_ok":v["A_ok"],"B_ok":v["B_ok"]})
(P/"score_replay.jsonl").write_text("\n".join(json.dumps(x,ensure_ascii=False) for x in rows)+"\n",encoding="utf-8")
print("map",len(mp),"diff",len(diff),"replay",len(rows))
