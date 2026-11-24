import sys,json
from pathlib import Path
WF=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
sys.path.insert(0,str(WF))
import vettlib as V, v2
import night_build as NB
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_night_20261121")
MODELS=list(V.MODELS); DECJ=json.dumps(v2.decode_config(300),sort_keys=True)
def freeze(tasks,template,hyp,seq,conds):
    bid="B"+str(seq).zfill(3); NOW=V.now_iso()
    design={"template":template,"hypothesis":hyp,"rationale":"No-notice complement of field/partial experiments.","positions":[],"fields":[],"conditions":conds,"models":MODELS,"scoring":"exact","sources":["no-notice text"],"cost":{"requests":len(tasks),"est_seconds":len(tasks)*20,"external_api":0},"created_at":NOW}
    man={"batch_id":bid,"seq":seq,"template":template,"created_at":NOW,"design":design,"schema_version":v2.SCHEMA_VERSION,"scoring_version":v2.SCORING_VERSION,"tasks":[{k:t[k] for k in ("task_key","legacy_task_key","match","innings","model","cond","field_scope","fields","prompt","prompt_sha","text_sha","num_predict","gold","model_digest","decode_json","input_version","prompt_version","replicate_id")} for t in tasks],"rejected":[]}
    mp=V.BATCHES/(bid+".json"); mp.write_text(json.dumps(man,ensure_ascii=False,indent=1),encoding="utf-8"); msha=V.sha256_text(mp.read_text(encoding="utf-8"))
    con=V.connect(); con.execute("INSERT INTO batches(batch_id,seq,template,created_at,hypothesis,rationale,design_json,manifest_path,manifest_sha,status,parent_batch_id,trigger_json,cost_json,updated_at,scoring_version,manifest_version,template_version,plan_ms) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(bid,seq,template,NOW,hyp,design["rationale"],json.dumps(design,ensure_ascii=False),str(mp),msha,"running",None,"{}",json.dumps(design["cost"],ensure_ascii=False),NOW,v2.SCORING_VERSION,"v2","v2",0.0))
    for t in tasks:
        con.execute("INSERT INTO tasks(task_key,batch_id,match,innings,model,cond,field_scope,fields_json,prompt,prompt_sha,text_sha,num_predict,status,attempts,created_at,updated_at,model_digest,decode_json,input_version,prompt_version,replicate_id,legacy_task_key,identity_status,gold_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(t["task_key"],bid,t["match"],t["innings"],t["model"],t["cond"],t["field_scope"],json.dumps(t["fields"]),t["prompt"],t["prompt_sha"],t["text_sha"],t["num_predict"],"queued",0,NOW,NOW,t["model_digest"],t["decode_json"],t["input_version"],t["prompt_version"],t["replicate_id"],"","v2",json.dumps(t["gold"],ensure_ascii=False)))
    V.meta_set(con,"batch_seq",str(seq)); V.meta_set(con,"exhausted","0"); V.meta_set(con,"state","running"); con.commit(); con.close(); return bid
con=V.connect(); seq=int(V.meta_get(con,"batch_seq","251") or 251); con.close(); ev=NB.load_events()
# B252 field N0
tasks=[]
for s in ev:
    inn=int(str(s["innings"]).replace("inn","")); b=NB.build_texts(s); fields=[s["A"]+"_wickets",s["A"]+"_runs",s["B"]+"_wickets",s["B"]+"_runs","innings_total_wickets"]; gold=dict(b["old"])
    for code in ("N0_F","N0_W"):
        text=b["arms"][code][1]
        for f in fields:
            intro="You are a cricket scorer. Read the commentary and return exactly one field. Return ONLY a JSON object. No prose."
            p=(intro+"\n\nMatch: "+s["match"]+"\nInnings: "+str(inn)+"\nField:\n- "+f+"\n\nCommentary:\n"+text+"\n\nJSON:")
            psha=V.sha256_text(p)
            for m in MODELS:
                dg=V.model_digest(m); key=v2.key_v2(s["match"],inn,m,dg,DECJ,v2.INPUT_VERSION,v2.PROMPT_VERSION,v2.REPLICATE_ID,"night_field",psha)
                tasks.append({"task_key":key,"legacy_task_key":"","match":s["match"],"innings":inn,"model":m,"cond":code+"_"+f,"field_scope":"night_field","fields":[f],"prompt":p,"prompt_sha":psha,"text_sha":V.sha256_text(text),"num_predict":120,"gold":{f:gold[f]},"model_digest":dg,"decode_json":DECJ,"input_version":v2.INPUT_VERSION,"prompt_version":v2.PROMPT_VERSION,"replicate_id":v2.REPLICATE_ID})
b252=freeze(tasks,"X_night_field","No-notice single-field extraction.",seq+1,["N0_F","N0_W"])
# B253 partial N0
seq+=1; tasks=[]
for s in ev:
    inn=int(str(s["innings"]).replace("inn","")); b=NB.build_texts(s); fields=[s["A"]+"_wickets",s["A"]+"_runs",s["B"]+"_wickets",s["B"]+"_runs","innings_total_wickets"]; gold=dict(b["old"])
    for code in ("N0_F","N0_W"):
        text=b["arms"][code][1]
        intro=("You are a cricket scorer. Read the commentary and fill ONLY the two named bowling rows plus the innings total. Return ONLY a JSON object. No prose.")
        p=(intro+"\n\nMatch: "+s["match"]+"\nInnings: "+str(inn)+"\nRows:\n- "+s["A"]+"\n- "+s["B"]+"\nFields:\n"+"\n".join("- "+f for f in fields)+"\n\nCommentary:\n"+text+"\n\nJSON:")
        psha=V.sha256_text(p)
        for m in MODELS:
            dg=V.model_digest(m); key=v2.key_v2(s["match"],inn,m,dg,DECJ,v2.INPUT_VERSION,v2.PROMPT_VERSION,v2.REPLICATE_ID,"night_partial",psha)
            tasks.append({"task_key":key,"legacy_task_key":"","match":s["match"],"innings":inn,"model":m,"cond":code+"_partial","field_scope":"night_partial","fields":fields,"prompt":p,"prompt_sha":psha,"text_sha":V.sha256_text(text),"num_predict":300,"gold":gold,"model_digest":dg,"decode_json":DECJ,"input_version":v2.INPUT_VERSION,"prompt_version":v2.PROMPT_VERSION,"replicate_id":v2.REPLICATE_ID})
b253=freeze(tasks,"X_night_partial","No-notice named two-row table.",seq+1,["N0_F_partial","N0_W_partial"])
print(json.dumps({"b252":b252,"n252":240,"b253":b253,"n253":48}))
