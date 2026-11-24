import sys,json,argparse
from pathlib import Path
WF=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
sys.path.insert(0,str(WF))
sys.path.insert(0,str(WF.parent/"vett_night_20261121"))
import vettlib as V, v2
import night_build as NB
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_top2_20261123")
MODELS=list(V.MODELS); DECJ=json.dumps(v2.decode_config(300),sort_keys=True)
S=json.loads((WF.parent/"attribution_followup"/"samples.json").read_text(encoding="utf-8"))
def top2(s,arm):
    b=V.load_bundle(s["match"]); inn=b["md"].innings[int(str(s["innings"]).replace("inn",""))-1]
    arr=[{"name":x.name,"w":x.wickets,"r":x.runs_conceded} for x in inn.bowlers]
    if arm=="N2":
        for x in arr:
            if x["name"]==s["A"]: x["w"]-=1
            if x["name"]==s["B"]: x["w"]+=1
    arr.sort(key=lambda x:(-x["w"],x["r"],x["name"]))
    return [x["name"] for x in arr[:2]]
def prompt(match,inn,text):
    return ("You are a cricket scorer. Read the commentary for the specified innings. "
            "List the two bowlers who should occupy the top two rows of this innings' bowling table, best first. "
            "Return ONLY a JSON object: {\"bowlers\": [\"Name One\", \"Name Two\"]}. No prose.\n\n"
            "Match: "+match+"\nInnings: "+str(inn)+"\n\nCommentary:\n"+text+"\n\nJSON:")
def build(matches,seq):
    tasks=[]; positions=[]
    for s in matches:
        inn=int(str(s["innings"]).replace("inn","")); built=NB.build_texts(s)
        for arm in ("N0","N1","N2"):
            text=built["arms"][arm+"_F"][1]; p=prompt(s["match"],inn,text); psha=V.sha256_text(p)
            gold=top2(s,arm)
            for m in MODELS:
                dg=V.model_digest(m)
                key=v2.key_v2(s["match"],inn,m,dg,DECJ,v2.INPUT_VERSION,v2.PROMPT_VERSION,v2.REPLICATE_ID,"top2",psha)
                tasks.append({"task_key":key,"legacy_task_key":"","match":s["match"],"innings":inn,"model":m,"cond":"T2_"+arm,"field_scope":"top2","fields":["bowlers"],"prompt":p,"prompt_sha":psha,"text_sha":V.sha256_text(text),"num_predict":120,"gold":{"bowlers":gold},"model_digest":dg,"decode_json":DECJ,"input_version":v2.INPUT_VERSION,"prompt_version":v2.PROMPT_VERSION,"replicate_id":v2.REPLICATE_ID})
        positions.append({"match":s["match"],"innings":inn,"old":top2(s,"N0"),"new":top2(s,"N2")})
    con=V.connect(); bid="B"+str(seq).zfill(3); NOW=V.now_iso()
    design={"template":"X_top2_membership","hypothesis":"Neutral top-2 bowler membership/order under 3 notices.","rationale":"Audited 8 roots; no target names in prompt.","positions":positions,"fields":["bowlers"],"conditions":["T2_N0","T2_N1","T2_N2"],"models":MODELS,"scoring":"membership set first; order separately","sources":["published commentary + ledger + notice"],"cost":{"requests":len(tasks),"est_seconds":len(tasks)*20,"external_api":0},"created_at":NOW}
    man={"batch_id":bid,"seq":seq,"template":design["template"],"created_at":NOW,"design":design,"schema_version":v2.SCHEMA_VERSION,"scoring_version":v2.SCORING_VERSION,"tasks":[{k:t[k] for k in ("task_key","legacy_task_key","match","innings","model","cond","field_scope","fields","prompt","prompt_sha","text_sha","num_predict","gold","model_digest","decode_json","input_version","prompt_version","replicate_id")} for t in tasks],"rejected":[]}
    mp=V.BATCHES/(bid+".json"); mp.write_text(json.dumps(man,ensure_ascii=False,indent=1),encoding="utf-8"); msha=V.sha256_text(mp.read_text(encoding="utf-8"))
    con.execute("INSERT INTO batches(batch_id,seq,template,created_at,hypothesis,rationale,design_json,manifest_path,manifest_sha,status,parent_batch_id,trigger_json,cost_json,updated_at,scoring_version,manifest_version,template_version,plan_ms) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(bid,seq,design["template"],NOW,design["hypothesis"],design["rationale"],json.dumps(design,ensure_ascii=False),str(mp),msha,"running",None,"{}",json.dumps(design["cost"],ensure_ascii=False),NOW,v2.SCORING_VERSION,"v2","v2",0.0))
    for t in tasks:
        con.execute("INSERT INTO tasks(task_key,batch_id,match,innings,model,cond,field_scope,fields_json,prompt,prompt_sha,text_sha,num_predict,status,attempts,created_at,updated_at,model_digest,decode_json,input_version,prompt_version,replicate_id,legacy_task_key,identity_status,gold_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(t["task_key"],bid,t["match"],t["innings"],t["model"],t["cond"],t["field_scope"],json.dumps(t["fields"]),t["prompt"],t["prompt_sha"],t["text_sha"],t["num_predict"],"queued",0,NOW,NOW,t["model_digest"],t["decode_json"],t["input_version"],t["prompt_version"],t["replicate_id"],"","v2",json.dumps(t["gold"],ensure_ascii=False)))
    V.meta_set(con,"batch_seq",str(seq)); V.meta_set(con,"exhausted","0"); V.meta_set(con,"state","running"); con.commit(); con.close()
    return {"batch":bid,"tasks":len(tasks),"positions":positions}
if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("mode"); a=ap.parse_args()
    if a.mode=="first":
        print(json.dumps(build([x for x in S if x["match"]=="match_0003"],254),ensure_ascii=False))
    elif a.mode=="rest":
        print(json.dumps(build([x for x in S if x["match"]!="match_0003"],255),ensure_ascii=False))
