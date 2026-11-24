import sys,json,collections
sys.path.insert(0,r"D:/Download/VETT_Cricket_Complete_Delivery_R19_20261017/VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117")
import vettlib as V
con=V.connect()
b=con.execute("SELECT batch_id,status,accuracy,score_json FROM batches WHERE batch_id='B209Z'").fetchone()
print("BATCH", tuple(b) if b else None)
rows=[dict(r) for r in con.execute("SELECT r.*,t.fields_json,t.prompt_sha,t.model_digest tid FROM results r JOIN tasks t USING(task_key) WHERE r.batch_id='B209Z' ORDER BY r.match,r.cond,r.model")]
bycond=collections.defaultdict(lambda:[0,0,0,0]); bymodel=collections.defaultdict(lambda:[0,0,0,0])
maxp=0; mismatch=0; reasons=collections.Counter(); sha_bad=0
for r in rows:
    req=json.loads(r.get("request_json") or "{}"); meta=json.loads(r.get("response_meta_json") or "{}")
    sc=json.loads(r.get("score_json") or "{}")
    cells=sc.get("cells",{}); tot=len(cells); cor=sum(1 for c in cells.values() if c.get("ok"))
    taskok=1 if sc.get("task_correct") else 0
    c=bycond[r["cond"]]; c[0]+=1; c[1]+=taskok; c[2]+=cor; c[3]+=tot
    m=bymodel[r["model"]]; m[0]+=1; m[1]+=taskok; m[2]+=cor; m[3]+=tot
    maxp=max(maxp,int(req.get("prompt_chars") or 0))
    reasons[meta.get("done_reason")]+=1
    if meta.get("model") and meta["model"]!=r["model"]: mismatch+=1
    if req.get("prompt_sha") and req["prompt_sha"]!=r["prompt_sha"]: sha_bad+=1
print("CONDS")
for k in sorted(bycond): print(" ",k,bycond[k])
print("MODELS")
for k in sorted(bymodel): print(" ",k,bymodel[k])
print("MAX_PROMPT_CHARS",maxp,"NUM_CTX 8192 approx tokens",round(maxp/4,1))
print("DONE_REASONS",dict(reasons),"MODEL_MISMATCH",mismatch,"PROMPT_SHA_BAD",sha_bad,"N",len(rows))
print("PARSE_OK",sum(1 for r in rows if r["parse_ok"]))
print("DETAIL_87")
for r in rows:
    if r["match"]=="match_0087": print(" ",r["cond"],r["model"].split(":")[0],r["correct"],r["raw_output"].replace(chr(10)," ")[:120])
print("DETAIL_03")
for r in rows:
    if r["match"]=="match_0003" and r["cond"] in ("C_change_full","C_change_window"): print(" ",r["cond"],r["model"].split(":")[0],r["correct"],r["raw_output"].replace(chr(10)," ")[:150])
con.close()
