import sys,json,hashlib
from pathlib import Path
WF=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
sys.path.insert(0,str(WF))
import vettlib as V, v2
import night_build as NB, night_diag as ND, night_more as NM
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_night_20261121")
MODELS=list(V.MODELS)

def freeze(tasks,template,hyp,rationale,positions,conds,sources,seq):
    bid="B"+str(seq).zfill(3); NOW=V.now_iso()
    design={"template":template,"hypothesis":hyp,"rationale":rationale,"positions":positions,"fields":[],"conditions":conds,"models":MODELS,"scoring":"exact","sources":sources,"cost":{"requests":len(tasks),"est_seconds":len(tasks)*30,"external_api":0},"created_at":NOW}
    man={"batch_id":bid,"seq":seq,"template":template,"created_at":NOW,"design":design,"schema_version":v2.SCHEMA_VERSION,"scoring_version":v2.SCORING_VERSION,"tasks":[{k:t[k] for k in ("task_key","legacy_task_key","match","innings","model","cond","field_scope","fields","prompt","prompt_sha","text_sha","num_predict","gold","model_digest","decode_json","input_version","prompt_version","replicate_id")} for t in tasks],"rejected":[]}
    mp=V.BATCHES/(bid+".json"); mp.write_text(json.dumps(man,ensure_ascii=False,indent=1),encoding="utf-8"); msha=V.sha256_text(mp.read_text(encoding="utf-8"))
    con=V.connect()
    con.execute("INSERT INTO batches(batch_id,seq,template,created_at,hypothesis,rationale,design_json,manifest_path,manifest_sha,status,parent_batch_id,trigger_json,cost_json,updated_at,scoring_version,manifest_version,template_version,plan_ms) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(bid,seq,template,NOW,hyp,rationale,json.dumps(design,ensure_ascii=False),str(mp),msha,"running",None,"{}",json.dumps(design["cost"],ensure_ascii=False),NOW,v2.SCORING_VERSION,"v2","v2",0.0))
    for t in tasks:
        con.execute("INSERT INTO tasks(task_key,batch_id,match,innings,model,cond,field_scope,fields_json,prompt,prompt_sha,text_sha,num_predict,status,attempts,created_at,updated_at,model_digest,decode_json,input_version,prompt_version,replicate_id,legacy_task_key,identity_status,gold_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(t["task_key"],bid,t["match"],t["innings"],t["model"],t["cond"],t["field_scope"],json.dumps(t["fields"]),t["prompt"],t["prompt_sha"],t["text_sha"],t["num_predict"],"queued",0,NOW,NOW,t["model_digest"],t["decode_json"],t["input_version"],t["prompt_version"],t["replicate_id"],"","v2",json.dumps(t["gold"],ensure_ascii=False)))
    V.meta_set(con,"batch_seq",str(seq)); V.meta_set(con,"exhausted","0"); V.meta_set(con,"state","running"); con.commit(); con.close()
    return bid

con=V.connect(); seq=int(V.meta_get(con,"batch_seq","245") or 245); con.close()
ev=NB.load_events()
# B246 window diagnostics
tasks=[]
for s in ev:
    inn=int(str(s["innings"]).replace("inn","")); b=NB.build_texts(s)
    for code in ("N0_W","N1_W","N2_W"):
        text=b["arms"][code][1]
        tasks+=ND.ask(s["match"],inn,"q1_batter","Which batter's dismissal is under review? Name the batter.",text,["batter"],{"batter":s["batter"]})
        tasks+=ND.ask(s["match"],inn,"q2_original","Which bowler was originally credited with this dismissal in the record? Name the bowler.",text,["original_bowler"],{"original_bowler":s["A"]})
        if code=="N2_W":
            tasks+=ND.ask(s["match"],inn,"q3_final","Which bowler is credited with this dismissal after the review? Name the bowler.",text,["final_bowler"],{"final_bowler":s["B"]})
        tasks+=ND.ask(s["match"],inn,"q4_old","Give the pre-revision wicket counts of the two bowlers named in the record.",text,[s["A"]+"_wickets",s["B"]+"_wickets"],{s["A"]+"_wickets":s["Aw"],s["B"]+"_wickets":s["Bw"]})
bid246=freeze(tasks,"X_night_diag","Window-text minimal diagnostics.","Branch 2 window complement.","",["q1_batter","q2_original","q3_final","q4_old"],["window text"],seq+1)
# B247 no-notice full table
seq+=1; tasks=[]
for s in ev:
    inn=int(str(s["innings"]).replace("inn","")); b=V.load_bundle(s["match"]); g=V.gold43(b["md"]); text=NB.build_texts(s)["arms"]["N0_F"][1]
    tasks+=NM.make("night_fulltable",s["match"],inn,"N0_F_fulltable",text,list(V.FULL43),g,900)
bid247=freeze(tasks,"X_night_fulltable","No-notice full table.","Section 4 complement: same text without review notice.",[{"match":s["match"]} for s in ev],["N0_F_fulltable"],["published commentary + ledger"],seq+1)
print(json.dumps({"b246":bid246,"n246":len(tasks),"b247":bid247,"n247":len(tasks)}))
