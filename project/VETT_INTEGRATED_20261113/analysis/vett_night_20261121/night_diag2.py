import sys,json,hashlib
from pathlib import Path
WF=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
sys.path.insert(0,str(WF))
import vettlib as V, v2
import night_build as NB, night_diag as ND
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_night_20261121")
DEC=v2.decode_config(300); DECJ=json.dumps(DEC,sort_keys=True); MODELS=list(V.MODELS)
con=V.connect(); seq=int(V.meta_get(con,"batch_seq","243") or 243); con.close()
for code,label in (("N0_F","no_notice"),("N1_F","maintain")):
    tasks=[]; ev=NB.load_events()
    for s in ev:
        inn=int(str(s["innings"]).replace("inn","")); text=NB.build_texts(s)["arms"][code][1]
        tasks+=ND.ask(s["match"],inn,"q1_batter","Which batter's dismissal is under review? Name the batter.",text,["batter"],{"batter":s["batter"]})
        tasks+=ND.ask(s["match"],inn,"q2_original","Which bowler was originally credited with this dismissal in the record? Name the bowler.",text,["original_bowler"],{"original_bowler":s["A"]})
        tasks+=ND.ask(s["match"],inn,"q4_old","Give the pre-revision wicket counts of the two bowlers named in the record.",text,[s["A"]+"_wickets",s["B"]+"_wickets"],{s["A"]+"_wickets":s["Aw"],s["B"]+"_wickets":s["Bw"]})
    seq+=1; bid="B"+str(seq).zfill(3); NOW=V.now_iso()
    design={"template":"X_night_diag","hypothesis":"Minimal diagnostics on "+label+" text.","rationale":"Branch 2 extension after N2 diag.","positions":[{"match":s["match"],"innings":int(str(s["innings"]).replace("inn",""))} for s in ev],"fields":[],"conditions":["q1_batter","q2_original","q4_old"],"models":MODELS,"scoring":"exact","sources":["published commentary + ledger + notice"],"cost":{"requests":len(tasks),"est_seconds":len(tasks)*30,"external_api":0},"created_at":NOW}
    man={"batch_id":bid,"seq":seq,"template":design["template"],"created_at":NOW,"design":design,"schema_version":v2.SCHEMA_VERSION,"scoring_version":v2.SCORING_VERSION,"tasks":[{k:t[k] for k in ("task_key","legacy_task_key","match","innings","model","cond","field_scope","fields","prompt","prompt_sha","text_sha","num_predict","gold","model_digest","decode_json","input_version","prompt_version","replicate_id")} for t in tasks],"rejected":[]}
    mp=V.BATCHES/(bid+".json"); mp.write_text(json.dumps(man,ensure_ascii=False,indent=1),encoding="utf-8"); msha=V.sha256_text(mp.read_text(encoding="utf-8"))
    con=V.connect()
    con.execute("INSERT INTO batches(batch_id,seq,template,created_at,hypothesis,rationale,design_json,manifest_path,manifest_sha,status,parent_batch_id,trigger_json,cost_json,updated_at,scoring_version,manifest_version,template_version,plan_ms) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(bid,seq,design["template"],NOW,design["hypothesis"],design["rationale"],json.dumps(design,ensure_ascii=False),str(mp),msha,"running",None,"{}",json.dumps(design["cost"],ensure_ascii=False),NOW,v2.SCORING_VERSION,"v2","v2",0.0))
    for t in tasks:
        con.execute("INSERT INTO tasks(task_key,batch_id,match,innings,model,cond,field_scope,fields_json,prompt,prompt_sha,text_sha,num_predict,status,attempts,created_at,updated_at,model_digest,decode_json,input_version,prompt_version,replicate_id,legacy_task_key,identity_status,gold_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(t["task_key"],bid,t["match"],t["innings"],t["model"],t["cond"],t["field_scope"],json.dumps(t["fields"]),t["prompt"],t["prompt_sha"],t["text_sha"],t["num_predict"],"queued",0,NOW,NOW,t["model_digest"],t["decode_json"],t["input_version"],t["prompt_version"],t["replicate_id"],"","v2",json.dumps(t["gold"],ensure_ascii=False)))
    V.meta_set(con,"batch_seq",str(seq)); V.meta_set(con,"exhausted","0"); V.meta_set(con,"state","running"); con.commit(); con.close()
    print(json.dumps({"batch":bid,"code":code,"tasks":len(tasks)}))
