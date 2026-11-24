import sqlite3, json, os
db = r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\state\workflow.db"
con = sqlite3.connect("file:" + db + "?mode=ro", uri=True); con.row_factory = sqlite3.Row
cur = con.cursor()
print("BATCH_ROWS")
for r in cur.execute("select batch_id, template, status, accuracy, manifest_path, manifest_sha, design_json from batches where batch_id in ('B019','B022','B210','B211')"):
    d = dict(r); d["design_json"] = str(d.get("design_json"))[:200]; print(" ", json.dumps(d, ensure_ascii=False))
print("COUNT")
for r in cur.execute("select batch_id, cond, count(*) n from tasks where batch_id in ('B019','B022') group by batch_id, cond"):
    print(" ", dict(r))
print("SAMPLE_TASK")
r = cur.execute("select * from tasks where batch_id='B019' and cond='C_change' limit 1").fetchone()
d = dict(r)
for k in ["task_key","match","innings","model","cond","field_scope","prompt_sha","text_sha","model_digest","decode_json","gold_json","fields_json","num_predict","input_version","prompt_version"]:
    print("  ", k, "=", str(d.get(k))[:300])
print("PROMPT_HEAD", str(d.get("prompt"))[:1800])
print("SAMPLE_RESULT")
r = cur.execute("select * from results where batch_id='B019' and cond='C_change' limit 1").fetchone()
d = dict(r)
for k in ["task_key","raw_output","parsed_json","parse_ok","score_json","request_json","response_meta_json","model_digest","decode_json"]:
    print("  ", k, "=", str(d.get(k))[:700])
print("SAMPLES_JSON")
p = r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\attribution_followup\samples.json"
obj = json.load(open(p, encoding="utf-8"))
print(" type", type(obj).__name__)
if isinstance(obj, list):
    print(" n", len(obj)); s = obj[0]
else:
    print(" keys", list(obj.keys())[:20]); s = obj[list(obj.keys())[0]]
print(" sample_keys", list(s.keys()) if isinstance(s, dict) else type(s).__name__)
print(" sample", json.dumps(s, ensure_ascii=False)[:1500])
