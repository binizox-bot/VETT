import sys,json,hashlib,collections,os,zipfile
from pathlib import Path
WF=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
sys.path.insert(0,str(WF))
import vettlib as V
EX=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\codex_exchange")
con=V.connect()
rows=[dict(r) for r in con.execute("SELECT r.*,t.prompt,t.prompt_sha tpsha,t.decode_json tdec,t.model_digest tdig,t.gold_json,t.fields_json FROM results r JOIN tasks t USING(task_key) WHERE r.batch_id='B209Z' ORDER BY r.match,r.cond,r.model")]
batch=con.execute("SELECT batch_id,status,accuracy,score_json,manifest_sha FROM batches WHERE batch_id='B209Z'").fetchone()
score=json.loads(batch[3])
checks={"sha_recompute_bad":0,"request_sha_bad":0,"decode_mismatch":0,"digest_mismatch":0,"model_name_mismatch":0}
maxp=0; reasons=collections.Counter()
for r in rows:
    if hashlib.sha256(r["prompt"].encode("utf-8")).hexdigest()!=r["tpsha"]: checks["sha_recompute_bad"]+=1
    req=json.loads(r.get("request_json") or "{}"); meta=json.loads(r.get("response_meta_json") or "{}")
    if req.get("prompt_sha")!=r["tpsha"]: checks["request_sha_bad"]+=1
    if req.get("options")!=json.loads(r["tdec"] or "{}"): checks["decode_mismatch"]+=1
    if meta.get("model_digest")!=r["tdig"]: checks["digest_mismatch"]+=1
    if meta.get("model")!=r["model"]: checks["model_name_mismatch"]+=1
    maxp=max(maxp,int(req.get("prompt_chars") or 0)); reasons[meta.get("done_reason")]+=1
summary={"batch_id":"B209Z","status":batch[1],"accuracy":batch[2],"n":len(rows),"score":score,
         "protocol":{"prompt_sha_recompute":"ok" if checks["sha_recompute_bad"]==0 else checks["sha_recompute_bad"],
                     "request_sha":"ok" if checks["request_sha_bad"]==0 else checks["request_sha_bad"],
                     "decode":"ok" if checks["decode_mismatch"]==0 else checks["decode_mismatch"],
                     "digest":"ok" if checks["digest_mismatch"]==0 else checks["digest_mismatch"],
                     "model_name":"ok" if checks["model_name_mismatch"]==0 else checks["model_name_mismatch"],
                     "max_prompt_chars":maxp,"num_ctx":8192,"done_reasons":dict(reasons)},
         "reused":json.loads((WF/"batches"/"B209Z_REUSE.json").read_text(encoding="utf-8"))}
sd=EX/"SEALED_B209Z"; sd.mkdir(parents=True,exist_ok=True)
with open(sd/"tasks.jsonl","w",encoding="utf-8",newline="\n") as f:
    for r in con.execute("SELECT * FROM tasks WHERE batch_id='B209Z' ORDER BY match,cond,model"):
        d=dict(r); d.pop("prompt",None)
        f.write(json.dumps(d,ensure_ascii=False)+"\n")
with open(sd/"results.jsonl","w",encoding="utf-8",newline="\n") as f:
    for r in rows:
        f.write(json.dumps({k:r.get(k) for k in ("task_key","match","innings","model","cond","raw_output","parsed_json","parse_ok","score_json","correct","duration_ms","request_json","response_meta_json","model_digest","decode_json","created_at")},ensure_ascii=False)+"\n")
(sd/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=1),encoding="utf-8")
# update manifest file list + checksums + zip
mp=EX/"MANIFEST_v1.json"; man=json.loads(mp.read_text(encoding="utf-8"))
man["version"]="codex-exchange-v1.1"; man["sealed_batches"]=["B019","B022","B209Z"]
files=[]
for root,_,fs in os.walk(EX):
    for fn in sorted(fs):
        p=Path(root)/fn
        if p.suffix==".zip" or p.name in ("SHA256SUMS.txt",): continue
        files.append({"path":str(p.relative_to(EX)).replace("\\","/"),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()})
man["files"]=files
mp.write_text(json.dumps(man,ensure_ascii=False,indent=1),encoding="utf-8")
lines=[]
for root,_,fs in os.walk(EX):
    for fn in sorted(fs):
        p=Path(root)/fn
        if p.suffix==".zip" or p.name=="SHA256SUMS.txt": continue
        lines.append(hashlib.sha256(p.read_bytes()).hexdigest()+"  "+str(p.relative_to(EX)).replace("\\","/"))
(EX/"SHA256SUMS.txt").write_text("\n".join(lines)+"\n",encoding="utf-8")
z=EX/"codex_exchange_20261121.zip"
with zipfile.ZipFile(z,"w",zipfile.ZIP_DEFLATED) as zz:
    for root,_,fs in os.walk(EX):
        for fn in sorted(fs):
            p=Path(root)/fn
            if p==z: continue
            zz.write(p,str(p.relative_to(EX)).replace("\\","/"))
con.close()
print(json.dumps({"summary":{k:summary[k] for k in ("batch_id","status","accuracy","n")},"protocol":summary["protocol"],
                  "by_condition":score.get("by_condition"),"zip_bytes":z.stat().st_size},ensure_ascii=False))
