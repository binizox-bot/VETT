import sys,json
from pathlib import Path
WF=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
sys.path.insert(0,str(WF))
import vettlib as V
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_dataset_independent_scoring_20261121")
run=ROOT/"run_dsh_v1"
base=ROOT/"v1_frozen"
g=[json.loads(l) for l in (base/"private_gold.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
key2sid={(x["match_root"],x["innings"],x["condition_code"]):x["sample_id"] for x in g}
con=V.connect()
print("STATUS",[dict(r) for r in con.execute("SELECT status,COUNT(*) n FROM tasks WHERE batch_id='B212' GROUP BY status")])
print("RESULTS",con.execute("SELECT COUNT(*) FROM results WHERE batch_id='B212'").fetchone()[0])
rows=[dict(r) for r in con.execute("SELECT r.*,t.prompt_sha tpsha,t.model_digest tdig,t.decode_json tdec,t.num_predict FROM results r JOIN tasks t USING(task_key) WHERE r.batch_id='B212' ORDER BY r.created_at")]
out=[]
for r in rows:
    meta=json.loads(r.get("response_meta_json") or "{}")
    sid=key2sid.get((r["match"],r["innings"],r["cond"]))
    out.append({"sample_id":sid,"model":r["model"],"raw_output":r["raw_output"],"task_id":r["task_key"],
                "prompt_sha256":r["tpsha"],"model_digest":meta.get("model_digest") or r["model_digest"],
                "decode":json.loads(r["tdec"] or "{}"),"done_reason":meta.get("done_reason"),
                "eval_count":meta.get("eval_count"),"num_predict":r["num_predict"],
                "truncated":bool(meta.get("done_reason")=="length" or (meta.get("eval_count") or 0)>=r["num_predict"]),
                "created_at":r["created_at"],"duration_ms":r["duration_ms"]})
if out:
    with open(run/"raw.jsonl","w",encoding="utf-8",newline="\n") as f:
        for x in out: f.write(json.dumps(x,ensure_ascii=False)+"\n")
print("RAW_WRITTEN",len(out),"FIRST",json.dumps(out[0],ensure_ascii=False)[:300] if out else None)
con.close()
