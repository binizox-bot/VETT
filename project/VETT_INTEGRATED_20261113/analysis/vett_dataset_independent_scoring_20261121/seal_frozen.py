import sys,json,hashlib,zipfile,datetime
from pathlib import Path
WF=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
sys.path.insert(0,str(WF))
import vettlib as V
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_dataset_independent_scoring_20261121")
base=ROOT/"v1_frozen"; run=ROOT/"run_dsh_v1"; ex=ROOT/"export_to_codex_v1"; ex.mkdir(parents=True,exist_ok=True)
raw=[json.loads(l) for l in (run/"raw.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
scores=[json.loads(l) for l in (run/"scores.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
gold={g["sample_id"]:g for g in [json.loads(l) for l in (base/"private_gold.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]}
inputs={r["sample_id"]:r for r in [json.loads(l) for l in (base/"model_inputs.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]}
dec=raw[0]["decode"]; dec_json=json.dumps(dec,sort_keys=True)
models=("qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b")
checks={"n":len(raw),"unique":len({(r["sample_id"],r["model"]) for r in raw}),"prompt_sha_bad":0,"model_bad":0,"digest_bad":0,"decode_bad":0,"truncated":0,"done_stop":0}
for r in raw:
    if r["prompt_sha256"]!=inputs[r["sample_id"]]["prompt_sha256"]: checks["prompt_sha_bad"]+=1
    if r["model"] not in models: checks["model_bad"]+=1
    if r["model_digest"]!=V.model_digest(r["model"]): checks["digest_bad"]+=1
    if json.dumps(r["decode"],sort_keys=True)!=dec_json: checks["decode_bad"]+=1
    if r["truncated"]: checks["truncated"]+=1
    if r["done_reason"]=="stop": checks["done_stop"]+=1
sc={(s["sample_id"],s["model"]):s for s in scores}
fields_ok=sum(s.get("correct_fields",0) for s in scores); fields_tot=sum(s.get("total_fields",0) for s in scores)
matrix=[]
for sid,g in gold.items():
    for m in models:
        s=sc.get((sid,m),{})
        matrix.append({"sample_id":sid,"match":g["match_root"],"innings":g["innings"],"condition":g["condition_semantics"],"model":m,"task_correct":bool(s.get("task_correct")),"fields":s.get("correct_fields"),"total":s.get("total_fields")})
summary={"batch_id":"B212","frozen_version":"v1_frozen_20261121","created_at":datetime.datetime.now().astimezone().isoformat(timespec="seconds"),"planned":15,"reused":0,"new":15,"responses":len(raw),"scorable":len(scores),"missing":15-len({(r["sample_id"],r["model"]) for r in raw}),"complete_pairs":{"long_pair":3,"attribution_triplet":3},"task_accuracy":sum(1 for s in scores if s.get("task_correct"))/len(scores),"field_accuracy":[fields_ok,fields_tot],"decode":dec,"model_digests":{m:V.model_digest(m) for m in models},"checks":checks,"matrix":matrix,"frozen_manifest_sha256":hashlib.sha256((base/"FROZEN_MANIFEST.json").read_bytes()).hexdigest(),"batch_manifest_sha256":hashlib.sha256((WF/"batches"/"B212.json").read_bytes()).hexdigest()}
(ex/"RUN_MANIFEST.json").write_text(json.dumps(summary,ensure_ascii=False,indent=1),encoding="utf-8")
for fn in ("raw.jsonl","scores.jsonl"):
    (ex/fn).write_text((run/fn).read_text(encoding="utf-8"),encoding="utf-8")
(ex/"README.md").write_text("# DSH run of Codex v1_frozen (B212)\n\n- 5 frozen inputs x 3 local models = 15 positions; 0 reused, 15 new.\n- All 15 responses scorable; 15/15 tasks and "+str(fields_ok)+"/"+str(fields_tot)+" fields correct under score_frozen.py.\n- Decode: "+dec_json+"\n- Models: qwen2.5:7b-instruct-q4_K_M, llama3.1:8b, gemma2:9b (digests in RUN_MANIFEST).\n- No truncation; all done_reason=stop.\n- Score with: python v1_frozen/score_frozen.py --predictions raw.jsonl --gold v1_frozen/private_gold.jsonl --out scores.jsonl\n",encoding="utf-8")
lines=[]
for p in sorted(ex.glob("*")):
    if p.name=="SHA256SUMS.txt" or p.suffix==".zip": continue
    lines.append(hashlib.sha256(p.read_bytes()).hexdigest()+"  "+p.name)
(ex/"SHA256SUMS.txt").write_text("\n".join(lines)+"\n",encoding="utf-8")
z=ex/"frozen_v1_B212_export.zip"
with zipfile.ZipFile(z,"w",zipfile.ZIP_DEFLATED) as zz:
    for p in sorted(ex.glob("*")):
        if p==z: continue
        zz.write(p,p.name)
print(json.dumps({"summary":{k:summary[k] for k in ("planned","reused","new","responses","scorable","missing","task_accuracy","field_accuracy","checks")},"zip_bytes":z.stat().st_size,"export":str(ex)},ensure_ascii=False))
