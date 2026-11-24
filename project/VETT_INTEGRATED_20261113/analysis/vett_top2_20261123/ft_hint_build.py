import sys,json
from pathlib import Path
WF=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
sys.path.insert(0,str(WF))
import vettlib as V, v2
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_top2_20261123")
c=V.connect()
base=c.execute("SELECT t.prompt,t.fields_json,t.text_sha,t.num_predict,t.gold_json,t.decode_json,t.input_version,t.prompt_version,t.replicate_id FROM tasks t JOIN batches b USING(batch_id) WHERE b.template='X_night_fulltable' AND t.match='match_0003' AND t.cond='N1_F_fulltable' AND t.model LIKE 'qwen%'").fetchone()
if not base: raise SystemExit("no base")
prompt,fields,tsha,npred,gold,dec,iv,pv,rep=base
# model's own B254 N1 list
own={}
for r in c.execute("SELECT r.model,r.parsed_json FROM results r WHERE r.batch_id='B254' AND r.cond='T2_N1'"):
    own[r[0]]=json.loads(r[1])["bowlers"]
def hint_prompt(p,names):
    marker="\n\nCommentary:"
    line="\n\nReference top-2 bowlers to use in the bowling rows: "+", ".join(names)+"."
    return p.replace(marker,line+marker,1)
tasks=[]
for m in V.MODELS:
    names=own[m]; p=hint_prompt(prompt,names); psha=V.sha256_text(p)
    dg=V.model_digest(m)
    key=v2.key_v2("match_0003",1,m,dg,dec,iv,pv,rep,"ft_hint",psha)
    tasks.append({"task_key":key,"legacy_task_key":"","match":"match_0003","innings":1,"model":m,"cond":"N1_F_fulltable_hint","field_scope":"ft_hint","fields":json.loads(fields),"prompt":p,"prompt_sha":psha,"text_sha":tsha,"num_predict":npred,"gold":json.loads(gold),"model_digest":dg,"decode_json":dec,"input_version":iv,"prompt_version":pv,"replicate_id":rep})
bid="B257"; NOW=V.now_iso(); seq=257
design={"template":"X_ft_hint","hypothesis":"Use model's own top-2 list as a hint when filling the 43-field table.","rationale":"Minimal backfill on match_0003 N1; 3 calls.","positions":[{"match":"match_0003","innings":1}],"fields":json.loads(fields),"conditions":["N1_F_fulltable_hint"],"models":list(V.MODELS),"scoring":"exact 43 fields; target rows separately","sources":["published commentary + ledger + notice"],"hints":{m.split(":")[0]:own[m] for m in V.MODELS},"cost":{"requests":3,"est_seconds":90,"external_api":0},"created_at":NOW}
man={"batch_id":bid,"seq":seq,"template":design["template"],"created_at":NOW,"design":design,"schema_version":v2.SCHEMA_VERSION,"scoring_version":v2.SCORING_VERSION,"tasks":[{k:t[k] for k in ("task_key","legacy_task_key","match","innings","model","cond","field_scope","fields","prompt","prompt_sha","text_sha","num_predict","gold","model_digest","decode_json","input_version","prompt_version","replicate_id")} for t in tasks],"rejected":[]}
mp=V.BATCHES/(bid+".json"); mp.write_text(json.dumps(man,ensure_ascii=False,indent=1),encoding="utf-8"); msha=V.sha256_text(mp.read_text(encoding="utf-8"))
if c.execute("SELECT 1 FROM batches WHERE batch_id=?",(bid,)).fetchone(): raise SystemExit("exists")
c.execute("INSERT INTO batches(batch_id,seq,template,created_at,hypothesis,rationale,design_json,manifest_path,manifest_sha,status,parent_batch_id,trigger_json,cost_json,updated_at,scoring_version,manifest_version,template_version,plan_ms) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(bid,seq,design["template"],NOW,design["hypothesis"],design["rationale"],json.dumps(design,ensure_ascii=False),str(mp),msha,"running",None,"{}",json.dumps(design["cost"],ensure_ascii=False),NOW,v2.SCORING_VERSION,"v2","v2",0.0))
for t in tasks:
    c.execute("INSERT INTO tasks(task_key,batch_id,match,innings,model,cond,field_scope,fields_json,prompt,prompt_sha,text_sha,num_predict,status,attempts,created_at,updated_at,model_digest,decode_json,input_version,prompt_version,replicate_id,legacy_task_key,identity_status,gold_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(t["task_key"],bid,t["match"],t["innings"],t["model"],t["cond"],t["field_scope"],json.dumps(t["fields"]),t["prompt"],t["prompt_sha"],t["text_sha"],t["num_predict"],"queued",0,NOW,NOW,t["model_digest"],t["decode_json"],t["input_version"],t["prompt_version"],t["replicate_id"],"","v2",json.dumps(t["gold"],ensure_ascii=False)))
V.meta_set(c,"batch_seq",str(seq)); V.meta_set(c,"exhausted","0"); V.meta_set(c,"state","running"); c.commit(); c.close()
print(json.dumps({"batch":bid,"tasks":len(tasks),"hints":{m.split(":")[0]:own[m] for m in V.MODELS}},ensure_ascii=False))
