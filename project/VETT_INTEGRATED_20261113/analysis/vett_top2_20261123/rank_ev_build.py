import sys,json
from pathlib import Path
WF=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
sys.path.insert(0,str(WF)); sys.path.insert(0,str(WF.parent/"vett_night_20261121"))
import vettlib as V, v2, night_build as NB
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_top2_20261123")
S={s["match"]:s for s in json.loads((WF.parent/"attribution_followup"/"samples.json").read_text(encoding="utf-8"))}
DECJ=json.dumps(v2.decode_config(300),sort_keys=True)
def top2(s,new=True):
    b=V.load_bundle(s["match"]); inn=b["md"].innings[int(str(s["innings"]).replace("inn",""))-1]
    arr=[{"n":x.name,"w":x.wickets,"r":x.runs_conceded} for x in inn.bowlers]
    if new:
        for x in arr:
            if x["n"]==s["A"]: x["w"]-=1
            if x["n"]==s["B"]: x["w"]+=1
    return [x["n"] for x in sorted(arr,key=lambda x:(-x["w"],x["r"],x["n"]))[:2]]
def ask(match,inn,text):
    return ("You are a cricket scorer. Read the commentary for the specified innings. List the two bowlers who should occupy the top two rows of this innings' bowling table, best first. "
            "If the commentary does not contain enough information to determine the top two uniquely, do not guess: return {\"uncertain\": true, \"missing\": \"<what information is missing>\"}. "
            "Otherwise return {\"bowlers\": [\"Name One\", \"Name Two\"]}. Return ONLY a JSON object. No prose.\n\n"
            "Match: "+match+"\nInnings: "+str(inn)+"\n\nCommentary:\n"+text+"\n\nJSON:")
tasks=[]; design={"positions":[]}
for m,extra in (("match_0008","Additional evidence: Evan Reed conceded 27 runs."),("match_0010","Additional evidence: Luke Barrett conceded 38 runs.")):
    s=S[m]; b=V.load_bundle(m); inn=int(str(s["innings"]).replace("inn","")); base=NB.build_texts(s)["arms"]["N2_F"][1]
    gold=top2(s,True); design["positions"].append({"match":m,"innings":inn,"gold_new_top2":gold,"missing_evidence":extra})
    for ver,text in (("MISS",base),("EVID",base+" "+extra)):
        p=ask(m,inn,text); psha=V.sha256_text(p)
        for mod in V.MODELS:
            dg=V.model_digest(mod)
            key=v2.key_v2(m,inn,mod,dg,DECJ,v2.INPUT_VERSION,v2.PROMPT_VERSION,v2.REPLICATE_ID,"rank_ev",psha)
            tasks.append({"task_key":key,"legacy_task_key":"","match":m,"innings":inn,"model":mod,"cond":"RANK_"+ver,"field_scope":"rank_ev","fields":["bowlers","uncertain","missing"],"prompt":p,"prompt_sha":psha,"text_sha":V.sha256_text(text),"num_predict":300,"gold":{"bowlers":gold},"model_digest":dg,"decode_json":DECJ,"input_version":v2.INPUT_VERSION,"prompt_version":v2.PROMPT_VERSION,"replicate_id":v2.REPLICATE_ID})
now=V.now_iso(); bid="B260"; seq=260
design.update({"template":"X_rank_evidence","hypothesis":"Missing runs prevent unique top-2; adding them permits a legal list.","rationale":"2 matches x 2 versions x 3 models; revised protocol allows uncertain.","conditions":["RANK_MISS","RANK_EVID"],"models":list(V.MODELS),"scoring":"missing: uncertain+missing info; evidence: legal top2","sources":["N2 full text; evidence adds one runs sentence"],"cost":{"requests":len(tasks),"est_seconds":120,"external_api":0},"created_at":now})
man={"batch_id":bid,"seq":seq,"template":design["template"],"created_at":now,"design":design,"schema_version":v2.SCHEMA_VERSION,"scoring_version":v2.SCORING_VERSION,"tasks":[{k:t[k] for k in ("task_key","legacy_task_key","match","innings","model","cond","field_scope","fields","prompt","prompt_sha","text_sha","num_predict","gold","model_digest","decode_json","input_version","prompt_version","replicate_id")} for t in tasks],"rejected":[]}
mp=V.BATCHES/(bid+".json"); mp.write_text(json.dumps(man,ensure_ascii=False,indent=1),encoding="utf-8"); msha=V.sha256_text(mp.read_text(encoding="utf-8"))
c=V.connect()
if c.execute("SELECT 1 FROM batches WHERE batch_id=?",(bid,)).fetchone(): raise SystemExit("exists")
c.execute("INSERT INTO batches(batch_id,seq,template,created_at,hypothesis,rationale,design_json,manifest_path,manifest_sha,status,parent_batch_id,trigger_json,cost_json,updated_at,scoring_version,manifest_version,template_version,plan_ms) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(bid,seq,design["template"],now,design["hypothesis"],design["rationale"],json.dumps(design,ensure_ascii=False),str(mp),msha,"running",None,"{}",json.dumps(design["cost"],ensure_ascii=False),now,v2.SCORING_VERSION,"v2","v2",0.0))
for t in tasks:
    c.execute("INSERT INTO tasks(task_key,batch_id,match,innings,model,cond,field_scope,fields_json,prompt,prompt_sha,text_sha,num_predict,status,attempts,created_at,updated_at,model_digest,decode_json,input_version,prompt_version,replicate_id,legacy_task_key,identity_status,gold_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(t["task_key"],bid,t["match"],t["innings"],t["model"],t["cond"],t["field_scope"],json.dumps(t["fields"]),t["prompt"],t["prompt_sha"],t["text_sha"],t["num_predict"],"queued",0,now,now,t["model_digest"],t["decode_json"],t["input_version"],t["prompt_version"],t["replicate_id"],"","v2",json.dumps(t["gold"],ensure_ascii=False)))
V.meta_set(c,"batch_seq",str(seq)); V.meta_set(c,"exhausted","0"); V.meta_set(c,"state","running"); c.commit(); c.close()
print(json.dumps({"batch":bid,"tasks":len(tasks),"positions":design["positions"]},ensure_ascii=False))
