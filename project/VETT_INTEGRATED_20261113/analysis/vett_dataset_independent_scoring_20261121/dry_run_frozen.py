import sys,json,hashlib
from pathlib import Path
WF=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
sys.path.insert(0,str(WF))
import vettlib as V, v2
base=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_dataset_independent_scoring_20261121\v1_frozen")
rows=[json.loads(l) for l in (base/"model_inputs.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
gold={g["sample_id"]:g for g in [json.loads(l) for l in (base/"private_gold.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]}
dec=v2.decode_config(300); dec_json=json.dumps(dec,sort_keys=True)
print("DECODE",dec_json)
con=V.connect(); digests={m:V.model_digest(m) for m in V.MODELS}
print("DIGESTS",digests)
tot_reuse=0
for r in rows:
    h=hashlib.sha256(r["prompt"].encode("utf-8")).hexdigest()
    g=gold[r["sample_id"]]
    print("INPUT",r["sample_id"],"sha_ok",h==r["prompt_sha256"],"chars",len(r["prompt"]),"match",g["match_root"],"inn",g["innings"],"sem",g["condition_semantics"],"fields",g["field_order"])
    for m in V.MODELS:
        cand=con.execute("SELECT task_key,decode_json,model_digest FROM tasks WHERE prompt_sha=? AND model=?",(h,m)).fetchall()
        hit=None
        for t in cand:
            if t[1]==dec_json and t[2]==digests[m]:
                if con.execute("SELECT 1 FROM results WHERE task_key=?",(t[0],)).fetchone():
                    hit=t[0]
        if hit: tot_reuse+=1
        print("   ",m.split(":")[0],"candidates",len(cand),"reuse",bool(hit))
print("REUSE_TOTAL",tot_reuse,"of",len(rows)*len(V.MODELS))
con.close()
