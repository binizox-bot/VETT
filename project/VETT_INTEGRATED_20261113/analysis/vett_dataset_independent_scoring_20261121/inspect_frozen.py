import json,hashlib,os
from pathlib import Path
base=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_dataset_independent_scoring_20261121\v1_frozen")
man=json.loads((base/"FROZEN_MANIFEST.json").read_text(encoding="utf-8"))
print("MANIFEST", man["schema"], man["version"], man["status"], "samples", man["sample_count"], "requests", man["expected_request_count"])
bad=[]
for f in man["files"]:
    p=base/f["path"]
    h=hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
    if h!=f["sha256"]: bad.append((f["path"],h,f["sha256"]))
print("HASH_BAD", bad)
rows=[json.loads(l) for l in (base/"model_inputs.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
print("INPUT_N",len(rows))
for r in rows:
    print("ROW", json.dumps({k:r.get(k) for k in ("sample_id","match","innings","task","condition_code","text_version","pair_id","pair_role","prompt_sha256","decode","fields")}, ensure_ascii=False)[:700])
print("ROW_KEYS", list(rows[0].keys()))
gold=[json.loads(l) for l in (base/"private_gold.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
print("GOLD_N",len(gold)); print("GOLD_KEYS", list(gold[0].keys()))
schema=json.loads((base/"SCHEMA.json").read_text(encoding="utf-8"))
print("SCHEMA", json.dumps(schema, ensure_ascii=False)[:1200])
