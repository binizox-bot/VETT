import sys,json,hashlib,argparse
from pathlib import Path
WF=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
sys.path.insert(0,str(WF))
import vettlib as V, v2
import night_build as NB
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_night_20261121")
DEC=v2.decode_config(300); DECJ=json.dumps(DEC,sort_keys=True); MODELS=list(V.MODELS)

def ask(match,inn,qid,question,text,fields,gold):
    intro=("You are a cricket scorer. Read the commentary and answer the question. "
           "Return ONLY a JSON object mapping each field id to its value. No prose.")
    p=(intro+"\n\nMatch: "+match+"\nInnings: "+str(inn)+"\nQuestion: "+question+
       "\nFields:\n"+"\n".join("- "+f for f in fields)+"\n\nCommentary:\n"+text+"\n\nJSON:")
    psha=V.sha256_text(p); out=[]
    for m in MODELS:
        dg=V.model_digest(m)
        key=v2.key_v2(match,inn,m,dg,DECJ,v2.INPUT_VERSION,v2.PROMPT_VERSION,v2.REPLICATE_ID,"night_diag",psha)
        out.append({"task_key":key,"legacy_task_key":"","match":match,"innings":inn,"model":m,"cond":qid,"field_scope":"night_diag","fields":fields,"prompt":p,"prompt_sha":psha,"text_sha":V.sha256_text(text),"num_predict":300,"gold":gold,"model_digest":dg,"decode_json":DECJ,"input_version":v2.INPUT_VERSION,"prompt_version":v2.PROMPT_VERSION,"replicate_id":v2.REPLICATE_ID})
    return out

def main():
    ev=NB.load_events(); tasks=[]
    for s in ev:
        inn=int(str(s["innings"]).replace("inn","")); built=NB.build_texts(s)
        text=built["arms"]["N2_F"][1]
        tasks+=ask(s["match"],inn,"q1_batter","Which batter's dismissal is under review? Name the batter.",text,["batter"],{"batter":s["batter"]})
        tasks+=ask(s["match"],inn,"q2_original","Which bowler was originally credited with this dismissal before the review? Name the bowler.",text,["original_bowler"],{"original_bowler":s["A"]})
        tasks+=ask(s["match"],inn,"q3_final","Which bowler is credited with this dismissal after the review? Name the bowler.",text,["final_bowler"],{"final_bowler":s["B"]})
        tasks+=ask(s["match"],inn,"q4_old","Give the pre-revision wicket counts of the two bowlers named in the record.",text,[s["A"]+"_wickets",s["B"]+"_wickets"],{s["A"]+"_wickets":s["Aw"],s["B"]+"_wickets":s["Bw"]})
    con=V.connect(); seq=int(V.meta_get(con,"batch_seq","242") or 242)+1; bid="B"+str(seq).zfill(3); NOW=V.now_iso()
    design={"template":"X_night_diag","hypothesis":"Minimal diagnostics: identity, original bowler, final bowler, old wickets.","rationale":"Branch 2 after core/full-table/fallback exhaustion.","positions":[{"match":s["match"],"innings":int(str(s["innings"]).replace("inn",""))} for s in ev],"fields":[],"conditions":["q1_batter","q2_original","q3_final","q4_old"],"models":MODELS,"scoring":"exact after case-insensitive string normalize; ints exact","sources":["published commentary + ledger + notice"],"cost":{"requests":len(tasks),"est_seconds":len(tasks)*30,"external_api":0},"created_at":NOW}
    man={"batch_id":bid,"seq":seq,"template":design["template"],"created_at":NOW,"design":design,"schema_version":v2.SCHEMA_VERSION,"scoring_version":v2.SCORING_VERSION,"tasks":[{k:t[k] for k in ("task_key","legacy_task_key","match","innings","model","cond","field_scope","fields","prompt","prompt_sha","text_sha","num_predict","gold","model_digest","decode_json","input_version","prompt_version","replicate_id")} for t in tasks],"rejected":[]}
    mp=V.BATCHES/(bid+".json"); mp.write_text(json.dumps(man,ensure_ascii=False,indent=1),encoding="utf-8"); msha=V.sha256_text(mp.read_text(encoding="utf-8"))
    con.execute("INSERT INTO batches(batch_id,seq,template,created_at,hypothesis,rationale,design_json,manifest_path,manifest_sha,status,parent_batch_id,trigger_json,cost_json,updated_at,scoring_version,manifest_version,template_version,plan_ms) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(bid,seq,design["template"],NOW,design["hypothesis"],design["rationale"],json.dumps(design,ensure_ascii=False),str(mp),msha,"running",None,"{}",json.dumps(design["cost"],ensure_ascii=False),NOW,v2.SCORING_VERSION,"v2","v2",0.0))
    for t in tasks:
        con.execute("INSERT INTO tasks(task_key,batch_id,match,innings,model,cond,field_scope,fields_json,prompt,prompt_sha,text_sha,num_predict,status,attempts,created_at,updated_at,model_digest,decode_json,input_version,prompt_version,replicate_id,legacy_task_key,identity_status,gold_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(t["task_key"],bid,t["match"],t["innings"],t["model"],t["cond"],t["field_scope"],json.dumps(t["fields"]),t["prompt"],t["prompt_sha"],t["text_sha"],t["num_predict"],"queued",0,NOW,NOW,t["model_digest"],t["decode_json"],t["input_version"],t["prompt_version"],t["replicate_id"],"","v2",json.dumps(t["gold"],ensure_ascii=False)))
    V.meta_set(con,"batch_seq",str(seq)); V.meta_set(con,"exhausted","0"); V.meta_set(con,"state","running"); con.commit()
    V.event("batch_frozen",{"batch_id":bid,"template":design["template"],"tasks":len(tasks),"note":"night diag branch2"},con); con.commit(); con.close()
    print(json.dumps({"batch":bid,"tasks":len(tasks)}))
if __name__=="__main__": main()
