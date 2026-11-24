import sys,json,hashlib
from pathlib import Path
WF=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
sys.path.insert(0,str(WF))
import vettlib as V, v2
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_dataset_independent_scoring_20261121")
base=ROOT/"v1_frozen"; run=ROOT/"run_dsh_v1"
rows=[json.loads(l) for l in (base/"model_inputs.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
gold={g["sample_id"]:g for g in [json.loads(l) for l in (base/"private_gold.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]}
dec=v2.decode_config(300); dec_json=json.dumps(dec,sort_keys=True)
con=V.connect()
print("ALIVE", V.pid_alive(int(V.meta_get(con,"supervisor_pid","0") or 0)), V.pid_alive(int(V.meta_get(con,"worker_pid","0") or 0)))
if con.execute("SELECT 1 FROM batches WHERE batch_id='B212'").fetchone():
    print("EXISTS"); sys.exit(0)
tasks=[]
for r in rows:
    g=gold[r["sample_id"]]; psha=hashlib.sha256(r["prompt"].encode("utf-8")).hexdigest()
    assert psha==r["prompt_sha256"]
    for m in V.MODELS:
        dg=V.model_digest(m)
        key=v2.key_v2(g["match_root"],g["innings"],m,dg,dec_json,v2.INPUT_VERSION,v2.PROMPT_VERSION,v2.REPLICATE_ID,"frozen_v1",psha)
        tasks.append({"task_key":key,"legacy_task_key":"","match":g["match_root"],"innings":g["innings"],
                      "model":m,"cond":r["condition_code"],"field_scope":"frozen_v1","fields":g["field_order"],
                      "prompt":r["prompt"],"prompt_sha":psha,"text_sha":r["text_sha256"],"num_predict":300,
                      "gold":g["gold"],"model_digest":dg,"decode_json":dec_json,
                      "input_version":v2.INPUT_VERSION,"prompt_version":v2.PROMPT_VERSION,"replicate_id":v2.REPLICATE_ID})
design={"template":"X_codex_frozen_v1","hypothesis":"Codex-frozen 5 inputs x 3 models; score with frozen private gold.",
        "rationale":"First frozen batch from v1_frozen_20261121, integrated at an idle batch boundary.",
        "positions":[{"match":g["match_root"],"innings":g["innings"],"sample_id":sid,"condition":g["condition_semantics"]} for sid,g in gold.items()],
        "fields":[],"conditions":[r["condition_code"] for r in rows],"models":V.MODELS,
        "scoring":"score_frozen.py against v1_frozen/private_gold.jsonl",
        "sources":["v1_frozen/model_inputs.jsonl","v1_frozen/private_gold.jsonl"],
        "cost":{"requests":len(tasks),"est_seconds":len(tasks)*30,"external_api":0},"created_at":V.now_iso()}
manifest={"batch_id":"B212","seq":212,"template":design["template"],"created_at":V.now_iso(),"design":design,
          "schema_version":v2.SCHEMA_VERSION,"scoring_version":v2.SCORING_VERSION,
          "tasks":[{k:t[k] for k in ("task_key","legacy_task_key","match","innings","model","cond","field_scope","fields","prompt","prompt_sha","text_sha","num_predict","gold","model_digest","decode_json","input_version","prompt_version","replicate_id")} for t in tasks],"rejected":[]}
mp=V.BATCHES/"B212.json"; mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=1),encoding="utf-8")
msha=V.sha256_text(mp.read_text(encoding="utf-8"))
con.execute("INSERT INTO batches(batch_id,seq,template,created_at,hypothesis,rationale,design_json,manifest_path,manifest_sha,status,parent_batch_id,trigger_json,cost_json,updated_at,scoring_version,manifest_version,template_version,plan_ms) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            ("B212",212,design["template"],V.now_iso(),design["hypothesis"],design["rationale"],json.dumps(design,ensure_ascii=False),str(mp),msha,"running",None,json.dumps({"rule_id":"X2","source":"codex v1_frozen"},ensure_ascii=False),json.dumps(design["cost"],ensure_ascii=False),V.now_iso(),v2.SCORING_VERSION,"v2","v2",0.0))
for t in tasks:
    con.execute("INSERT INTO tasks(task_key,batch_id,match,innings,model,cond,field_scope,fields_json,prompt,prompt_sha,text_sha,num_predict,status,attempts,created_at,updated_at,model_digest,decode_json,input_version,prompt_version,replicate_id,legacy_task_key,identity_status,gold_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (t["task_key"],"B212",t["match"],t["innings"],t["model"],t["cond"],t["field_scope"],json.dumps(t["fields"]),t["prompt"],t["prompt_sha"],t["text_sha"],t["num_predict"],"queued",0,V.now_iso(),V.now_iso(),t["model_digest"],t["decode_json"],t["input_version"],t["prompt_version"],t["replicate_id"],"","v2",json.dumps(t["gold"],ensure_ascii=False)))
V.meta_set(con,"batch_seq","212"); V.meta_set(con,"exhausted","0"); V.meta_set(con,"state","running")
con.commit()
V.event("batch_frozen",{"batch_id":"B212","template":design["template"],"tasks":len(tasks),"reused":0,"manifest_sha":msha,"note":"codex v1_frozen, 15 positions"},con)
con.commit()
run.mkdir(parents=True,exist_ok=True)
(run/"README.md").write_text("# DSH run of Codex v1_frozen\n\n- batch B212; 5 inputs x 3 models = 15 positions.\n- raw.jsonl mirrors workflow results; scores.jsonl from score_frozen.py.\n- decode: "+dec_json+"\n",encoding="utf-8")
with open(run/"positions.jsonl","w",encoding="utf-8",newline="\n") as f:
    for sid,g in gold.items():
        f.write(json.dumps({"sample_id":sid,"match":g["match_root"],"innings":g["innings"],"condition":g["condition_semantics"],"fields":g["field_order"]},ensure_ascii=False)+"\n")
con.close()
print(json.dumps({"ok":True,"batch":"B212","tasks":len(tasks),"run_dir":str(run),"manifest_sha":msha}))
